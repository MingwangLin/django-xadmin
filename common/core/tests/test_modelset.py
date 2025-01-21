from decimal import Decimal
from django.contrib.auth import get_user_model
from django.db import models, connection
from django.test import TestCase, TransactionTestCase, override_settings
from django.urls import reverse, path, include
from rest_framework import serializers, viewsets, permissions
from rest_framework.routers import DefaultRouter
from rest_framework.test import APITransactionTestCase, URLPatternsTestCase, force_authenticate

from common.core.modelset import SearchColumnsAction
from system.models.field import ModelSeparationField


# Test model for our viewset
class TestModel(models.Model):
    name = models.CharField(max_length=100, verbose_name="Name")
    age = models.IntegerField(verbose_name="Age")

    class Meta:
        app_label = 'system'
        db_table = 'system_test_model'
        managed = True
        verbose_name = 'Test Model'
        verbose_name_plural = 'Test Models'

    def __str__(self):
        return self.name


# Test serializer
class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestModel
        fields = ['name', 'age']


# Test viewset
class TestViewSet(SearchColumnsAction, viewsets.GenericViewSet):
    queryset = TestModel.objects.all()
    serializer_class = TestSerializer
    basename = 'testmodel'
    permission_classes = [permissions.IsAuthenticated]


# Create router and register viewset
router = DefaultRouter()
router.register(r'testmodel', TestViewSet, basename='testmodel')


class SearchColumnsEditTests(APITransactionTestCase, URLPatternsTestCase):
    urlpatterns = [
        path('api/', include(router.urls)),
    ]

    def setUp(self):
        # Create the test table
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(TestModel)

        self.viewset = TestViewSet()
        self.url = '/api/testmodel/search-columns-edit/'
        
        # Create test user and authenticate
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            is_staff=True
        )
        self.client.force_authenticate(user=self.user)
        
        # Create test model instance
        self.test_model = TestModel.objects.create(
            name="Test Name",
            age=25
        )
        
        # Create some test separation fields
        self.separation_field1 = ModelSeparationField.objects.create(
            model_name='system.testmodel',
            name='section1',
            label='Section 1',
            label_visible=True,
            describe='Test section 1',
            style='style1',
            color='#000000',
            label_color='#FFFFFF',
            field_auth='auth1',
            form_grid=Decimal('12.00'),
            table_show=Decimal('1.00')
        )
        
        self.separation_field2 = ModelSeparationField.objects.create(
            model_name='system.testmodel',
            name='section2',
            label='Section 2',
            label_visible=False,
            describe='Test section 2',
            style='style2',
            color='#111111',
            label_color='#EEEEEE',
            field_auth='auth2',
            form_grid=Decimal('6.00'),
            table_show=Decimal('2.00')
        )

    def tearDown(self):
        # Drop the test table
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(TestModel)
        self.user.delete()
        ModelSeparationField.objects.all().delete()

    def test_search_columns_edit_basic(self):
        """Test basic functionality of search_columns_edit"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()['data']
        
        # Check if base fields from serializer are present
        base_fields = ['name', 'age']
        for field in base_fields:
            self.assertTrue(any(f['key'] == field for f in data))
        
        # Check if separation fields are present
        separation_fields = ['section1', 'section2']
        for field in separation_fields:
            self.assertTrue(any(f['key'] == field for f in data))

    def test_separation_field_attributes(self):
        """Test if separation fields have correct attributes"""
        response = self.client.get(self.url)
        data = response.json()['data']
        
        # Find section1 in response
        section1 = next(f for f in data if f['key'] == 'section1')
        
        # Check all attributes
        self.assertEqual(section1['label'], 'Section 1')
        self.assertEqual(section1['label_visible'], True)
        self.assertEqual(section1['describe'], 'Test section 1')
        self.assertEqual(section1['style'], 'style1')
        self.assertEqual(section1['color'], '#000000')
        self.assertEqual(section1['label_color'], '#FFFFFF')
        self.assertEqual(section1['field_auth'], 'auth1')
        self.assertEqual(section1['form_grid'], 12.00)
        self.assertEqual(section1['table_show'], 1.00)
        self.assertEqual(section1['input_type'], 'separator')
        self.assertEqual(section1['required'], False)
        self.assertEqual(section1['read_only'], False)
        self.assertEqual(section1['write_only'], False)

    def test_ordering_by_table_show(self):
        """Test if fields are properly ordered by table_show"""
        response = self.client.get(self.url)
        data = response.json()['data']
        
        # Get separation fields
        separation_fields = [f for f in data if f['input_type'] == 'separator']
        
        # Check if they're ordered by table_show
        self.assertEqual(separation_fields[0]['key'], 'section1')  # table_show = 1.00
        self.assertEqual(separation_fields[1]['key'], 'section2')  # table_show = 2.00

    def test_model_without_separation_fields(self):
        """Test behavior when model has no separation fields"""
        # Delete all separation fields
        ModelSeparationField.objects.all().delete()
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()['data']
        # Should only have base fields
        self.assertTrue(all(f['input_type'] != 'separator' for f in data))

    def test_invalid_model_name(self):
        """Test behavior with invalid model name"""
        # Create field with invalid model name
        ModelSeparationField.objects.create(
            model_name='invalid.model',
            name='invalid_section',
            label='Invalid Section',
            table_show=Decimal('1.00')
        )
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()['data']
        # Should not include the invalid model's fields
        self.assertFalse(any(f['key'] == 'invalid_section' for f in data))

    def test_null_values_handling(self):
        """Test handling of null values in separation fields"""
        # Create field with null values
        null_field = ModelSeparationField.objects.create(
            model_name='system.testmodel',
            name='null_section',
            label='Null Section',
            form_grid=None,
            table_show=None
        )
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()['data']
        null_section = next(f for f in data if f['key'] == 'null_section')
        
        # Check null values are handled properly
        self.assertIsNone(null_section['form_grid'])
        self.assertIsNone(null_section['table_show']) 