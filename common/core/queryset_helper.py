from datetime import timedelta, datetime
from django.db.models import Q, F, Case, When, Value, IntegerField, Func, TextField
from django.db.models.functions import Concat, Cast
from django.utils import timezone
from common.core.json_helper import JsonHelper
from common.core.orm_helper import Convert
from common.core.str_helper import StrHelper
from common.core.time_helper import TimeHelper
from common.utils import get_logger
logger = get_logger(__name__)


class GBKConversion(Func):
    """
    Custom database function to convert string to GBK encoding for sorting.
    This uses PostgreSQL's convert_to function to handle GBK encoding.
    """
    function = 'CONVERT_TO'
    template = "%(function)s(%(expressions)s, 'GBK')"


class QuerysetHelper:
    """
    A helper class for handling Django queryset operations including filtering, sorting, and searching.
    
    This class provides utility methods to process and apply filters, sort operations, and text searches
    on Django querysets in a flexible and reusable way.
    """

    def __init__(self):
        super(QuerysetHelper, self).__init__()

    @classmethod
    def get_filter_dict(cls, request_data):
        """
        Extracts and processes filter parameters from request data.

        Args:
            request_data (dict): The request data containing filter parameters.

        Returns:
            dict: A processed dictionary containing filter conditions.
                The filter data should be in JSON format under the 'filter' key.
        """
        filter_param = request_data.get('filter')
        filter_dict = JsonHelper.get_loaded_dict(filter_param)
        filter_dict = StrHelper.decode_json_strings(filter_dict)
        return filter_dict

    @classmethod
    def apply_filter(cls, queryset, filter_dict):
        """
        Applies complex filtering conditions to a Django queryset.

        Args:
            queryset (QuerySet): The Django queryset to filter.
            filter_dict (dict): A dictionary containing filter conditions with the following structure:
                {
                    'rel': str,  # Relationship between conditions ('and'/'or')
                    'cond': [    # List of conditions
                        {
                            'field': str,     # Field name (supports nested fields with '.')
                            'method': str,     # Filter method (e.g., 'exact', 'contains', 'in')
                            'value': any,      # Filter value
                            'type': str       # Value type (e.g., 'text', 'datetime')
                        }
                    ]
                }

        Returns:
            QuerySet: Filtered queryset based on the provided conditions.

        Features:
            - Supports nested field filtering using dot notation
            - Handles datetime filtering with exact minute precision
            - Supports negation of conditions using '~' prefix
            - Special handling for NULL values and empty lists
            - Supports datetime formula-based filtering
            - Combines multiple conditions using AND/OR logic
        """
        filter_dict = filter_dict or dict()
        rel = filter_dict.get('rel', 'and').lower()
        q_list = []
        for condition in filter_dict.get('cond', []):
            field = condition.get('field')
            field = field.replace('.', '__')
            method = condition.get('method')
            value = condition.get('value')
            value_type = condition.get('type')

            if not field or not method:
                continue

            if method in ['isnull', '~isnull']:
                continue  # Skip 'isnull' methods as per instruction

            negate = False
            if method.startswith('~'):
                negate = True
                method = method[1:]
            if method == 'iexact':
                method = 'exact'  # 'iexact' used with 'datetime' has problem

            # Handle the new 'formula' method for datetime
            if value_type == 'datetime' and method == 'formula':
                if not isinstance(value, list):
                    continue  # Skip invalid value format
                now = timezone.now()
                now = TimeHelper.astimezone(now)
                for item in value:
                    formula_list = item.get('formula', [])
                    if not isinstance(formula_list, list) or len(formula_list) != 2:
                        continue  # Skip invalid formula format
                    start_formula = formula_list[0]
                    end_formula = formula_list[1]

                    start_datetime = cls.parse_formula(start_formula, now, is_start=True)
                    end_datetime = cls.parse_formula(end_formula, now, is_start=False)

                    if start_datetime and end_datetime:
                        kwargs = {f"{field}__range": (start_datetime, end_datetime)}
                    elif start_datetime and not end_datetime:
                        kwargs = {f"{field}__gte": start_datetime}
                    elif not start_datetime and end_datetime:
                        kwargs = {f"{field}__lte": end_datetime}
                    else:
                        continue  # Both start and end are None, skip condition
                    q_obj = Q(**kwargs)
                    q_list.append(q_obj)
                continue  # Move to the next condition after processing formula
            # Handle None or empty list values
            if value is None or (isinstance(value, list) and not value):
                if value_type == 'text' and method in ['exact', 'iexact']:
                    # For text fields, check for NULL or empty string
                    kwargs = (Q(**{f"{field}__isnull": True}) | Q(**{f"{field}": ''}))
                elif method in ['exact', 'iexact']:
                    kwargs = {f"{field}__isnull": True}
                else:
                    continue  # Skip this condition to avoid ValueError
            else:
                if value_type == 'datetime' and method in ['exact', 'iexact']:
                    value = value[0]
                    # Convert value to datetime object
                    if isinstance(value, str):
                        try:
                            value = datetime.fromisoformat(value)
                        except ValueError:
                            logger.error(f'apply_filter: Skip invalid datetime formats')
                            continue  # Skip invalid datetime formats
                    # Create a time range for the given minute
                    start_time = value
                    end_time = start_time + timedelta(minutes=1) - timedelta(microseconds=1)
                    kwargs = {f"{field}__range": (start_time, end_time)}
                elif method in ['in', 'range']:
                    kwargs = {f"{field}__{method}": value}
                else:
                    if isinstance(value, list):
                        kwargs = {f"{field}__{method}": value[0]}
                    else:
                        kwargs = {f"{field}__{method}": value}

            q_obj = Q(**kwargs) if type(kwargs) == dict else kwargs
            if negate:
                q_obj = ~q_obj
            q_list.append(q_obj)
        combined_q = Q()
        for q_obj in q_list:
            if rel == 'or':
                combined_q |= q_obj
            else:
                combined_q &= q_obj
        return queryset.filter(combined_q)

    @classmethod
    def parse_formula(cls, formula, now, is_start):
        from datetime import datetime, timedelta
        from dateutil.relativedelta import relativedelta

        if formula is None:
            return None

        if not isinstance(formula, str):
            return None

        formula = formula.strip()
        if not formula:
            return None

        sign = None
        if formula[0] in '+-':
            sign = formula[0]
            rest = formula[1:]
        else:
            rest = formula

        if not rest:
            return None

        # Extract amount and unit
        if rest[-1] in ('d', 'w', 'M', 'Q', 'y', 'm', 'q'):
            unit = rest[-1]
            amount_str = rest[:-1] or '1'
        else:
            return None  # Invalid unit

        try:
            amount = int(amount_str)
        except ValueError:
            return None  # Invalid amount

        if amount < 0:
            return None  # Amount should be positive

        date = now

        # Adjust date based on sign and unit
        if sign in ('+', '-'):
            if unit == 'd':
                delta = timedelta(days=amount)
            elif unit == 'w':
                delta = timedelta(weeks=amount)
            elif unit in ('M', 'm'):
                delta = relativedelta(months=amount)
            elif unit in ('Q', 'q'):
                delta = relativedelta(months=3 * amount)
            elif unit == 'y':
                delta = relativedelta(years=amount)
            else:
                return None  # Invalid unit

            if sign == '+':
                date += delta
            else:
                date -= delta
        else:
            # sign is None, use current period
            pass  # date remains as now

        # Get start or end of the period
        if unit == 'd':
            if is_start:
                return date.replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                return date.replace(hour=23, minute=59, second=59, microsecond=999999)
        elif unit == 'w':
            weekday = date.weekday()  # Monday is 0
            if is_start:
                start_date = date - timedelta(days=weekday)
                return start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                end_date = date + timedelta(days=6 - weekday)
                return end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        elif unit in ('M', 'm'):
            if is_start:
                start_date = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                return start_date
            else:
                next_month = date.replace(day=28) + timedelta(days=4)  # this will never fail
                last_day = next_month - timedelta(days=next_month.day)
                return last_day.replace(hour=23, minute=59, second=59, microsecond=999999)
        elif unit in ('Q', 'q'):
            # Compute the quarter
            month = ((date.month - 1) // 3) * 3 + 1
            if is_start:
                start_date = date.replace(month=month, day=1, hour=0, minute=0, second=0, microsecond=0)
                return start_date
            else:
                month += 2
                next_month = date.replace(month=month, day=28) + timedelta(days=4)
                last_day = next_month - timedelta(days=next_month.day)
                return last_day.replace(hour=23, minute=59, second=59, microsecond=999999)
        elif unit == 'y':
            if is_start:
                start_date = date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
                return start_date
            else:
                end_date = date.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
                return end_date
        else:
            return None  # Invalid unit

    @classmethod
    def _get_gbk_order(cls, field_name):
        """
        Helper method to create a GBK encoding expression for sorting.
        Uses PostgreSQL's convert_to function to convert text to GBK encoding.
        
        Args:
            field_name (str): The name of the field to sort by GBK encoding
            
        Returns:
            Expression that converts the field to GBK encoding for sorting
        """
        return GBKConversion(F(field_name))

    @classmethod
    def get_general_sort_keys_filtered_queryset(cls, sortkeys, queryset, model, use_gbk=True):
        """
        Applies sorting to a queryset based on provided sort keys, handling nested model relationships.
        Supports GBK encoding sorting for Chinese characters.

        Args:
            sortkeys (list): List of strings representing sort fields. Each key can be:
                           - Prefixed with '-' for descending order
                           - Use dot notation for nested relationships
                           - Use Django's double underscore notation
            queryset (QuerySet): The Django queryset to sort
            model (Model): The Django model class associated with the queryset
            use_gbk (bool): Whether to use GBK encoding for sorting (default: False)

        Returns:
            QuerySet: A new queryset ordered by the specified sort keys

        Raises:
            ValueError: If a specified relationship field doesn't exist in the model

        Example:
            sortKeys = ['name', '-created_at', 'department.name']
            sorted_queryset = get_general_sort_keys_filtered_queryset(sortKeys, queryset, User, use_gbk=True)
        """
        sortkeys = sortkeys or list()
        sortkeys = StrHelper.get_dot_transformed_list(sortkeys)
        processed_sort_keys = []

        for key in sortkeys:
            descending = '-' in key
            field_path = key.lstrip('-')  # Remove leading '-' if present for descending order
            field_parts = field_path.split('__')

            # Traverse through the model fields and relationships to get to the field
            current_model = model
            for part in field_parts[:-1]:
                field = current_model._meta.get_field(part)
                if hasattr(field, 'related_model'):
                    current_model = field.related_model
                else:
                    raise ValueError(f"No related model found for field '{part}' in model '{current_model.__name__}'.")

            # If GBK sorting is enabled and the field is a character field
            if use_gbk:
                field = current_model._meta.get_field(field_parts[-1])
                if field.get_internal_type() in ['CharField', 'TextField']:
                    # Create a GBK ordering annotation
                    annotation_name = f"{field_path}_gbk_order"
                    queryset = queryset.annotate(**{annotation_name: cls._get_gbk_order(field_path)})
                    if descending:
                        processed_sort_keys.append(f"-{annotation_name}")
                    else:
                        processed_sort_keys.append(annotation_name)
                    continue

            # For non-GBK sorting or non-character fields
            if descending:
                processed_sort_keys.append('-' + field_path)
            else:
                processed_sort_keys.append(field_path)

        # Order the queryset based on processed sortkeys
        queryset = queryset.order_by(*processed_sort_keys)
        logger.info(f"processed_sort_keys: {processed_sort_keys}")
        logger.info(f"queryset: {queryset}")
        logger.info(f"queryset.query: {queryset.query}")
        return queryset

    @classmethod
    def get_search_text_multiple_filtered_queryset(cls, request_get_dict, queryset, filter_fields):
        """
        Performs a case-insensitive text search across multiple fields in a queryset.

        Args:
            request_get_dict (dict): Request parameters containing 'searchtext' key
            queryset (QuerySet): The Django queryset to filter
            filter_fields (list): List of field names to search within

        Returns:
            QuerySet: Filtered queryset containing records that match the search text
                     in any of the specified fields

        Example:
            filter_fields = ['name', 'description', 'email']
            filtered_qs = get_search_text_multiple_filtered_queryset(request.GET, queryset, filter_fields)
        """
        search_text = request_get_dict.get('searchtext')
        if search_text:
            query = Q()
            for field in filter_fields:
                query |= Q(**{f"{field}__icontains": search_text})
            queryset = queryset.filter(query)
        return queryset
                                             