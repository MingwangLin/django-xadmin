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

# Test Models
class VenueLetter(models.Model):
    fileName = models.CharField(max_length=255)
    key = models.CharField(max_length=255)
    auditUserId = models.IntegerField()
    uploadTime = models.DateTimeField(null=True)

    class Meta:
        app_label = 'common'

class BatchOverview(models.Model):
    taskIssueDate = models.DateField(null=True)

    class Meta:
        app_label = 'common'

class ApplyFilterTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fixed_now = datetime(2021, 10, 1, 12, 25, 20, 345627, tzinfo=pytz.UTC)
        cls.test_time = cls.fixed_now
        cls.test_time_start = cls.test_time.replace(hour=0, minute=0, second=0, microsecond=0)
        cls.test_time_end = cls.test_time.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Create test instances
        VenueLetter.objects.create(id=1, uploadTime=cls.test_time, fileName='Test1', auditUserId=10)
        VenueLetter.objects.create(id=2, uploadTime=cls.test_time_start, fileName='Test2', auditUserId=20)
        VenueLetter.objects.create(id=3, uploadTime=cls.test_time_end, fileName='Test3', auditUserId=30)
        VenueLetter.objects.create(id=4, uploadTime=None, fileName='Test4', auditUserId=40)
        VenueLetter.objects.create(id=5, uploadTime=cls.test_time + timedelta(days=1), fileName='Test5', auditUserId=50)
        VenueLetter.objects.create(id=6, uploadTime=cls.test_time - timedelta(days=1), fileName='Test6', auditUserId=60)
        VenueLetter.objects.create(id=7, uploadTime=cls.test_time + relativedelta(months=1), fileName='Test7', auditUserId=70)
        VenueLetter.objects.create(id=8, uploadTime=cls.test_time - relativedelta(months=1), fileName='Test8', auditUserId=80)

    def get_queryset(self):
        return VenueLetter.objects.all()

    def apply_and_assert(self, filter_dict, expected_names):
        queryset = self.get_queryset()
        filtered_queryset = QuerysetHelper.apply_filter(queryset, filter_dict)
        result_names = set(filtered_queryset.values_list('fileName', flat=True))
        self.assertSetEqual(result_names, set(expected_names))

    def test_iexact(self):
        filter_dict = {
            'rel': 'and',
            'cond': [
                {'field': 'fileName', 'method': 'iexact', 'value': ['Test1']}
            ]
        }
        self.apply_and_assert(filter_dict, ['Test1'])

    def test_negated_iexact(self):
        filter_dict = {
            'rel': 'and',
            'cond': [
                {'field': 'fileName', 'method': '~iexact', 'value': ['Test1']}
            ]
        }
        self.apply_and_assert(filter_dict, ['Test2', 'Test3', 'Test4', 'Test5', 'Test6', 'Test7', 'Test8'])

    def test_in_method(self):
        filter_dict = {
            'rel': 'and',
            'cond': [
                {'field': 'key', 'method': 'in', 'value': ['A001', 'C001']}
            ]
        }
        self.apply_and_assert(filter_dict, [])  # Empty because no matching keys exist

    def test_negated_in_method(self):
        filter_dict = {
            'rel': 'and',
            'cond': [
                {'field': 'key', 'method': '~in', 'value': ['A001', 'C001']}
            ]
        }
        self.apply_and_assert(filter_dict, ['Test1', 'Test2', 'Test3', 'Test4', 'Test5', 'Test6', 'Test7', 'Test8'])

    def test_icontains(self):
        filter_dict = {
            'rel': 'and',
            'cond': [
                {'field': 'fileName', 'method': 'icontains', 'value': ['Test']}
            ]
        }
        self.apply_and_assert(filter_dict, ['Test1', 'Test2', 'Test3', 'Test4', 'Test5', 'Test6', 'Test7', 'Test8'])

    def test_negated_icontains(self):
        filter_dict = {
            'rel': 'and',
            'cond': [
                {'field': 'fileName', 'method': '~icontains', 'value': ['Test1']}
            ]
        }
        self.apply_and_assert(filter_dict, ['Test2', 'Test3', 'Test4', 'Test5', 'Test6', 'Test7', 'Test8'])

    def test_gt_method(self):
        filter_dict = {
            'rel': 'and',
            'cond': [
                {'field': 'auditUserId', 'method': 'gt', 'value': [25]}
            ]
        }
        self.apply_and_assert(filter_dict, ['Test3', 'Test4', 'Test5', 'Test6', 'Test7', 'Test8'])

    def test_gte_method(self):
        filter_dict = {
            'rel': 'and',
            'cond': [
                {'field': 'auditUserId', 'method': 'gte', 'value': [30]}
            ]
        }
        self.apply_and_assert(filter_dict, ['Test3', 'Test4', 'Test5', 'Test6', 'Test7', 'Test8'])

    def test_lt_method(self):
        filter_dict = {
            'rel': 'and',
            'cond': [
                {'field': 'auditUserId', 'method': 'lt', 'value': [25]}
            ]
        }
        self.apply_and_assert(filter_dict, ['Test1', 'Test2'])

    def test_lte_method(self):
        filter_dict = {
            'rel': 'and',
            'cond': [
                {'field': 'auditUserId', 'method': 'lte', 'value': [20]}
            ]
        }
        self.apply_and_assert(filter_dict, ['Test1', 'Test2'])

    def test_range_method(self):
        filter_dict = {
            'rel': 'and',
            'cond': [
                {'field': 'auditUserId', 'method': 'range', 'value': [15, 35]}
            ]
        }
        self.apply_and_assert(filter_dict, ['Test2', 'Test3'])

    def test_or_relation(self):
        filter_dict = {
            'rel': 'or',
            'cond': [
                {'field': 'fileName', 'method': 'iexact', 'value': ['Test1']},
                {'field': 'fileName', 'method': 'iexact', 'value': ['Test2']}
            ]
        }
        self.apply_and_assert(filter_dict, ['Test1', 'Test2'])

    def test_and_relation(self):
        filter_dict = {
            'rel': 'and',
            'cond': [
                {'field': 'fileName', 'method': 'icontains', 'value': ['Test']},
                {'field': 'auditUserId', 'method': 'gt', 'value': [20]}
            ]
        }
        self.apply_and_assert(filter_dict, ['Test3', 'Test4', 'Test5', 'Test6', 'Test7', 'Test8'])

    def test_empty_value_list(self):
        filter_dict = {
            'rel': 'and',
            'cond': [
                {'field': 'fileName', 'method': 'iexact', 'value': []}
            ]
        }
        self.apply_and_assert(filter_dict, [])

    def test_missing_field_or_method(self):
        filter_dict = {
            'rel': 'and',
            'cond': [
                {'field': '', 'method': 'iexact', 'value': ['Test1']},
                {'field': 'fileName', 'method': '', 'value': ['Test1']}
            ]
        }
        self.apply_and_assert(filter_dict, ['Test1', 'Test2', 'Test3', 'Test4', 'Test5', 'Test6', 'Test7', 'Test8'])

    def test_invalid_method(self):
        filter_dict = {
            'rel': 'and',
            'cond': [
                {'field': 'fileName', 'method': 'unknown', 'value': ['Test1']}
            ]
        }
        with self.assertRaises(FieldError):
            QuerysetHelper.apply_filter(self.get_queryset(), filter_dict)

    def test_null_value(self):
        filter_dict = {
            'rel': 'and',
            'cond': [
                {'field': 'fileName', 'method': 'iexact', 'value': None}
            ]
        }
        self.apply_and_assert(filter_dict, [])

    def test_no_conditions(self):
        filter_dict = {'rel': 'and', 'cond': []}
        self.apply_and_assert(filter_dict, ['Test1', 'Test2', 'Test3', 'Test4', 'Test5', 'Test6', 'Test7', 'Test8']) 