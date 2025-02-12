from django.test import TestCase
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError, FieldError
from django.db.models import Q
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import mock
import pytz

from common.core.queryset_helper import QuerysetHelper
from .test_queryset_helper import VenueLetter, BatchOverview

class QuerysetHelperFormulaTest(TestCase):
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

class QuerysetHelperFormulaWeekAndLargerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fixed_now = datetime(2021, 10, 1, 12, 25, 20, 345627, tzinfo=pytz.UTC)
        cls.test_time = cls.fixed_now
        cls.test_time_start = cls.test_time.replace(hour=0, minute=0, second=0, microsecond=0)
        cls.test_time_end = cls.test_time.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Create test instances with various dates
        VenueLetter.objects.create(id=1, uploadTime=cls.test_time, fileName='Test1', auditUserId=10)
        VenueLetter.objects.create(id=2, uploadTime=cls.test_time_start, fileName='Test2', auditUserId=20)
        VenueLetter.objects.create(id=3, uploadTime=cls.test_time_end, fileName='Test3', auditUserId=30)
        VenueLetter.objects.create(id=4, uploadTime=None, fileName='Test4', auditUserId=40)
        VenueLetter.objects.create(id=5, uploadTime=cls.test_time + timedelta(days=1), fileName='Test5', auditUserId=50)
        VenueLetter.objects.create(id=6, uploadTime=cls.test_time - timedelta(days=1), fileName='Test6', auditUserId=60)
        VenueLetter.objects.create(id=7, uploadTime=cls.test_time + relativedelta(months=1), fileName='Test7', auditUserId=70)
        VenueLetter.objects.create(id=8, uploadTime=cls.test_time - relativedelta(months=1), fileName='Test8', auditUserId=80)
        VenueLetter.objects.create(id=9, uploadTime=cls.test_time + relativedelta(years=1), fileName='Test9', auditUserId=90)
        VenueLetter.objects.create(id=10, uploadTime=cls.test_time - relativedelta(years=1), fileName='Test10', auditUserId=100)
        VenueLetter.objects.create(id=11, uploadTime=cls.test_time + timedelta(weeks=1), fileName='Test11', auditUserId=110)
        VenueLetter.objects.create(id=12, uploadTime=cls.test_time - timedelta(weeks=1), fileName='Test12', auditUserId=120)
        VenueLetter.objects.create(id=13, uploadTime=cls.test_time + relativedelta(months=3), fileName='Test13', auditUserId=130)
        VenueLetter.objects.create(id=14, uploadTime=cls.test_time - relativedelta(months=3), fileName='Test14', auditUserId=140)

    def apply_filter_and_assert(self, formula, expected_ids):
        filter_dict = {
            'rel': 'and',
            'cond': [{
                'field': 'uploadTime',
                'method': 'formula',
                'value': [{'mode': 'custom', 'formula': formula}],
                'type': 'datetime'
            }]
        }
        with mock.patch('django.utils.timezone.now', return_value=self.fixed_now):
            queryset = VenueLetter.objects.all()
            filtered_queryset = QuerysetHelper.apply_filter(queryset, filter_dict)
            self.assertQuerySetEqual(
                filtered_queryset.order_by('id'),
                VenueLetter.objects.filter(id__in=expected_ids).order_by('id'),
                transform=lambda x: x
            )

    def test_formula_minus_1w_plus_1w(self):
        # ["-1w", "+1w"]: from start of last week to end of next week
        expected_ids = [1, 2, 3, 5, 6, 11, 12]
        self.apply_filter_and_assert(["-1w", "+1w"], expected_ids)

    def test_formula_1w_1w(self):
        # ["1w", "1w"]: objects in the current week
        expected_ids = [1, 2, 3, 5, 6]
        self.apply_filter_and_assert(["1w", "1w"], expected_ids)

    def test_formula_minus_1w_1w(self):
        # ["-1w", "1w"]: from start of last week to end of current week
        expected_ids = [1, 2, 3, 5, 6, 12]
        self.apply_filter_and_assert(["-1w", "1w"], expected_ids)

    def test_formula_1w_plus_1w(self):
        # ["1w", "+1w"]: from start of current week to end of next week
        expected_ids = [1, 2, 3, 5, 6, 11]
        self.apply_filter_and_assert(["1w", "+1w"], expected_ids)

    def test_formula_none_plus_1w(self):
        # [None, "+1w"]: up to end of next week
        expected_ids = [1, 2, 3, 5, 6, 8, 10, 11, 12, 14]
        self.apply_filter_and_assert([None, "+1w"], expected_ids)

    def test_formula_minus_1w_none(self):
        # ["-1w", None]: from start of last week onwards
        expected_ids = [1, 2, 3, 5, 6, 7, 9, 11, 12, 13]
        self.apply_filter_and_assert(["-1w", None], expected_ids)

    def test_formula_minus_1m_plus_1m(self):
        # ["-1m", "+1m"]: from start of last month to end of next month
        expected_ids = [1, 2, 3, 5, 6, 7, 8, 11, 12]
        self.apply_filter_and_assert(["-1m", "+1m"], expected_ids)

    def test_formula_1m_1m(self):
        # ["1m", "1m"]: objects in the current month
        expected_ids = [1, 2, 3, 5, 11]
        self.apply_filter_and_assert(["1m", "1m"], expected_ids)

    def test_formula_minus_1m_1m(self):
        # ["-1m", "1m"]: from start of last month to end of current month
        expected_ids = [1, 2, 3, 5, 6, 8, 11, 12]
        self.apply_filter_and_assert(["-1m", "1m"], expected_ids)

    def test_formula_1m_plus_1m(self):
        # ["1m", "+1m"]: from start of current month to end of next month
        expected_ids = [1, 2, 3, 5, 7, 11]
        self.apply_filter_and_assert(["1m", "+1m"], expected_ids)

    def test_formula_none_plus_1m(self):
        # [None, "+1m"]: up to end of next month
        expected_ids = [1, 2, 3, 5, 6, 7, 8, 10, 11, 12, 14]
        self.apply_filter_and_assert([None, "+1m"], expected_ids)

    def test_formula_minus_1m_none(self):
        # ["-1m", None]: from start of last month onwards
        expected_ids = [1, 2, 3, 5, 6, 7, 8, 9, 11, 12, 13]
        self.apply_filter_and_assert(["-1m", None], expected_ids)

    def test_formula_minus_1q_plus_1q(self):
        # ["-1q", "+1q"]: from start of last quarter to end of next quarter
        expected_ids = [1, 2, 3, 5, 6, 7, 8, 11, 12, 13, 14]
        self.apply_filter_and_assert(["-1q", "+1q"], expected_ids)

    def test_formula_1q_1q(self):
        # ["1q", "1q"]: objects in the current quarter
        expected_ids = [1, 2, 3, 5, 7, 11]
        self.apply_filter_and_assert(["1q", "1q"], expected_ids)

    def test_formula_minus_1q_1q(self):
        # ["-1q", "1q"]: from start of last quarter to end of current quarter
        expected_ids = [1, 2, 3, 5, 6, 7, 8, 11, 12, 14]
        self.apply_filter_and_assert(["-1q", "1q"], expected_ids)

    def test_formula_1q_plus_1q(self):
        # ["1q", "+1q"]: from start of current quarter to end of next quarter
        expected_ids = [1, 2, 3, 5, 7, 11, 13]
        self.apply_filter_and_assert(["1q", "+1q"], expected_ids)

    def test_formula_none_plus_1q(self):
        # [None, "+1q"]: up to end of next quarter
        expected_ids = [1, 2, 3, 5, 6, 7, 8, 10, 11, 12, 13, 14]
        self.apply_filter_and_assert([None, "+1q"], expected_ids)

    def test_formula_minus_1q_none(self):
        # ["-1q", None]: from start of last quarter onwards
        expected_ids = [1, 2, 3, 5, 6, 7, 8, 9, 11, 12, 13, 14]
        self.apply_filter_and_assert(["-1q", None], expected_ids)

    def test_formula_minus_1y_plus_1y(self):
        # ["-1y", "+1y"]: from start of last year to end of next year
        expected_ids = [1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
        self.apply_filter_and_assert(["-1y", "+1y"], expected_ids)

    def test_formula_1y_1y(self):
        # ["1y", "1y"]: objects in the current year
        expected_ids = [1, 2, 3, 5, 6, 7, 8, 11, 12, 14]
        self.apply_filter_and_assert(["1y", "1y"], expected_ids)

    def test_formula_minus_1y_1y(self):
        # ["-1y", "1y"]: from start of last year to end of current year
        expected_ids = [1, 2, 3, 5, 6, 7, 8, 10, 11, 12, 14]
        self.apply_filter_and_assert(["-1y", "1y"], expected_ids)

    def test_formula_1y_plus_1y(self):
        # ["1y", "+1y"]: from start of current year to end of next year
        expected_ids = [1, 2, 3, 5, 6, 7, 8, 9, 11, 12, 13, 14]
        self.apply_filter_and_assert(["1y", "+1y"], expected_ids)

    def test_formula_none_plus_1y(self):
        # [None, "+1y"]: up to end of next year
        expected_ids = [1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
        self.apply_filter_and_assert([None, "+1y"], expected_ids)

    def test_formula_minus_1y_none(self):
        # ["-1y", None]: from start of last year onwards
        expected_ids = [1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
        self.apply_filter_and_assert(["-1y", None], expected_ids) 