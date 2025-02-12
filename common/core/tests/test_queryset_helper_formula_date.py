from django.test import TestCase
from django.utils import timezone
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import mock
import pytz

from common.core.queryset_helper import QuerysetHelper
from .test_queryset_helper import BatchOverview

class QuerysetHelperFormulaDateTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fixed_now = datetime(2021, 10, 1, 12, 25, 20, 345627, tzinfo=pytz.UTC)
        cls.test_time = cls.fixed_now.date()

        # Create test instances
        BatchOverview.objects.create(id=1, taskIssueDate=cls.test_time)
        BatchOverview.objects.create(id=2, taskIssueDate=cls.test_time)
        BatchOverview.objects.create(id=3, taskIssueDate=cls.test_time)
        BatchOverview.objects.create(id=4, taskIssueDate=None)
        BatchOverview.objects.create(id=5, taskIssueDate=cls.test_time + timedelta(days=1))
        BatchOverview.objects.create(id=6, taskIssueDate=cls.test_time - timedelta(days=1))
        BatchOverview.objects.create(id=7, taskIssueDate=cls.test_time + relativedelta(months=1))
        BatchOverview.objects.create(id=8, taskIssueDate=cls.test_time - relativedelta(months=1))

    def apply_filter_and_assert(self, formula, expected_ids):
        filter_dict = {
            'rel': 'and',
            'cond': [{
                'field': 'taskIssueDate',
                'method': 'formula',
                'value': [{'mode': 'custom', 'formula': formula}],
                'type': 'datetime'
            }]
        }
        with mock.patch('django.utils.timezone.now', return_value=self.fixed_now):
            queryset = BatchOverview.objects.all()
            filtered_queryset = QuerysetHelper.apply_filter(queryset, filter_dict)
            self.assertQuerySetEqual(
                filtered_queryset.order_by('id'),
                BatchOverview.objects.filter(id__in=expected_ids).order_by('id'),
                transform=lambda x: x
            )

    def test_formula_minus_1d_plus_1d(self):
        # ["-1d", "+1d"]: should include objects from one day ago to one day after
        expected_ids = [1, 2, 3, 5, 6]
        self.apply_filter_and_assert(["-1d", "+1d"], expected_ids)

    def test_formula_1d_1d(self):
        # ["1d", "1d"]: should include objects from the start to end of the current day
        expected_ids = [1, 2, 3]
        self.apply_filter_and_assert(["1d", "1d"], expected_ids)

    def test_formula_minus_1d_1d(self):
        # ["-1d", "1d"]: should include objects from one day ago up to the end of the current day
        expected_ids = [1, 2, 3, 6]
        self.apply_filter_and_assert(["-1d", "1d"], expected_ids)

    def test_formula_1d_plus_1d(self):
        # ["1d", "+1d"]: should include objects from start of current day to end of next day
        expected_ids = [1, 2, 3, 5]
        self.apply_filter_and_assert(["1d", "+1d"], expected_ids)

    def test_formula_none_plus_1d(self):
        # [None, "+1d"]: should include objects up to end of next day
        expected_ids = [1, 2, 3, 5, 6, 8]
        self.apply_filter_and_assert([None, "+1d"], expected_ids)

    def test_formula_minus_1d_none(self):
        # ["-1d", None]: should include objects from one day ago onwards
        expected_ids = [1, 2, 3, 5, 6, 7]
        self.apply_filter_and_assert(["-1d", None], expected_ids)

    def test_formula_none_none(self):
        # [None, None]: should include all objects
        expected_ids = [1, 2, 3, 4, 5, 6, 7, 8]
        self.apply_filter_and_assert([None, None], expected_ids)

    def test_formula_minus_1m_plus_1m(self):
        # ["-1m", "+1m"]: should include objects from start of last month to end of next month
        expected_ids = [1, 2, 3, 5, 6, 7, 8]
        self.apply_filter_and_assert(["-1m", "+1m"], expected_ids)

    def test_formula_1q_1q(self):
        # ["1q", "1q"]: should include objects in the current quarter
        expected_ids = [1, 2, 3, 5, 7]
        self.apply_filter_and_assert(["1q", "1q"], expected_ids)

    def test_formula_invalid_format(self):
        # Test with invalid formula format
        expected_ids = [1, 2, 3, 4, 5, 6, 7, 8]
        self.apply_filter_and_assert(["invalid", "format"], expected_ids)

        # Test with invalid unit
        expected_ids = [1, 2, 3, 4, 5, 6, 7, 8]
        self.apply_filter_and_assert(["-1x", "+1x"], expected_ids)

    def test_formula_empty_formula(self):
        # Test with empty formula
        expected_ids = [1, 2, 3, 4, 5, 6, 7, 8]
        self.apply_filter_and_assert([], expected_ids)

    def test_formula_single_none(self):
        # Test with one value None and other valid
        expected_ids = [1, 2, 3, 6, 8]
        self.apply_filter_and_assert([None, "1d"], expected_ids)

    def test_formula_year(self):
        # Test with year unit
        expected_ids = [1, 2, 3, 5, 6, 7, 8]
        self.apply_filter_and_assert(["1y", "1y"], expected_ids)

    def test_formula_week(self):
        # Test with week unit
        expected_ids = [1, 2, 3, 5, 6]
        self.apply_filter_and_assert(["-1w", "+1w"], expected_ids) 