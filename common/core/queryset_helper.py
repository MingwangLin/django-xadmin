from datetime import timedelta, datetime
from django.db.models import Q
from django.utils import timezone
from common.core.json_helper import JsonHelper
from common.core.orm_helper import Convert
from common.core.str_helper import StrHelper
from common.core.time_helper import TimeHelper
import logging

logger = logging.getLogger(__name__)

class QuerysetHelper:

    def __init__(self):
        super(QuerysetHelper, self).__init__()

    @classmethod
    def get_filter_dict(cls, request_data):
        filter_param = request_data.get('filter')
        filter_dict = JsonHelper.get_loaded_dict(filter_param)
        filter_dict = StrHelper.decode_json_strings(filter_dict)
        return filter_dict

    @classmethod
    def apply_filter(cls, queryset, filter_dict):
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
    def get_general_sort_kyes_filtered_queryset(cls, request_get_dict, queryset, model):
        """

        :param request_get_dict:
        :param queryset:
        :param model: initial model
        :return:
        """
        from django.db import models

        sortKeys = JsonHelper.get_loaded_list(request_get_dict.get('sortkeys'))
        sortKeys = StrHelper.get_dot_transformed_list(sortKeys)

        processed_sort_keys = []

        for key in sortKeys:
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

            # Get the final field
            final_field_name = field_parts[-1]
            final_field = current_model._meta.get_field(final_field_name)
            is_integer = isinstance(final_field, (models.IntegerField, models.AutoField, models.DecimalField))

            if is_integer:
                # Add field as is for integer types
                if descending:
                    processed_sort_keys.append('-' + field_path)
                else:
                    processed_sort_keys.append(field_path)
            else:
                # Use Convert class for non-integer types
                if descending:
                    processed_sort_keys.append(Convert(field_path, 'gbk').desc())
                else:
                    processed_sort_keys.append(Convert(field_path, 'gbk').asc())

        # Order the queryset based on processed sortKeys
        queryset = queryset.order_by(*processed_sort_keys)
        return queryset
    
    @classmethod
    def get_search_text_multiple_filtered_queryset(cls, request_get_dict, queryset, filter_fields):
        search_text = request_get_dict.get('searchtext')
        if search_text:
            query = Q()
            for field in filter_fields:
                query |= Q(**{f"{field}__icontains": search_text})
            queryset = queryset.filter(query)
        return queryset
                                             