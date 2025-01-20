from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
import mock

from device.models import Device
from device.serializers import DeviceSerializer
from system.models import UserInfo
from device.models import Channel, DeviceChannel

import logging
logger = logging.getLogger(__name__)

class DeviceViewSetTests(APITestCase):
    def setUp(self):
        # Clear the database first
        Device.objects.all().delete()
        UserInfo.objects.all().delete()
        Channel.objects.all().delete()
        DeviceChannel.objects.all().delete()
        
        self.client = APIClient()
        self.client.defaults['HTTP_USER_AGENT'] = 'Mozilla/5.0 (test)'
        self.client.defaults['HTTP_ACCEPT'] = 'application/json'
        
        # Create admin user first (will be used as creator)
        self.admin_user = UserInfo.objects.create_user(
            username='admin',
            password='admin123',
            nickname='Admin User',
            is_staff=True,
            is_superuser=True
        )
        # Set admin as their own creator and modifier
        self.admin_user.creator = self.admin_user
        self.admin_user.modifier = self.admin_user
        self.admin_user.save()
        
        # Create test user
        self.user = UserInfo.objects.create_user(
            username='testuser',
            password='testpass123',
            nickname='Test User',
            is_staff=True,
            is_superuser=True,
            creator=self.admin_user,  # Set the creator as admin user
            modifier=self.admin_user  # Set the modifier as admin user
        )
        
        self.user.save()
        
        self.client.force_authenticate(user=self.user)
        
        self.device_1 = Device.objects.create(
            name="Test Device 1",
            device_id="DEV001",
            manufacturer="Test Manufacturer",
            type=Device.TypeChoices.IPC,
            status=Device.StreamStatusChoices.ONLINE,
            creator=self.admin_user,
            modifier=self.admin_user
        )
        self.device_2 = Device.objects.create(
            name="Test Device 2", 
            device_id="DEV002",
            manufacturer="Another Manufacturer",
            type=Device.TypeChoices.PATROL,
            status=Device.StreamStatusChoices.OFFLINE,
            creator=self.admin_user,
            modifier=self.admin_user
        )
        # Using correct URL names from urls.py
        self.list_url = reverse('device:device-list')
        self.detail_url = reverse('device:device-detail', kwargs={'pk': self.device_1.pk})
        self.query_url = reverse('device:device-query')
        self.batch_destroy_url = reverse('device:device-batch-destroy')
        self.export_url = reverse('device:device-export-data')

    def tearDown(self):
        # Clean up all test data after each test
        Device.objects.all().delete()
        UserInfo.objects.all().delete()
        Channel.objects.all().delete()
        DeviceChannel.objects.all().delete()
        super().tearDown()

    def test_list_devices(self):
        """Test retrieving a list of devices"""
        response = self.client.get(self.list_url)
        devices = Device.objects.all()
        serializer = DeviceSerializer(devices, many=True)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(sorted(response.data['data']['results'], key=lambda x: x['pk']), sorted(serializer.data, key=lambda x: x['pk']))
        self.assertEqual(len(response.data['data']['results']), 2)

    def test_create_device(self):
        """Test creating a new device"""
        data = {
            'name': 'New Device',
            'device_id': 'DEV003',
            'manufacturer': 'New Manufacturer',
            'type': Device.TypeChoices.IPC,
            'status': Device.StreamStatusChoices.ONLINE,
            'creator': self.user.id,
            'modifier': self.user.id
        }
        response = self.client.post(self.list_url, data)
        
        print("Response data:", response.data)  # Keep for debugging
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Device.objects.count(), 3)
        self.assertEqual(Device.objects.get(device_id='DEV003').name, 'New Device')

    def test_retrieve_device(self):
        """Test retrieving a single device"""
        response = self.client.get(self.detail_url)
        device = Device.objects.get(pk=self.device_1.pk)
        serializer = DeviceSerializer(device)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data'], serializer.data)

    def test_update_device(self):
        """Test updating a device"""
        update_data = {
            'name': 'Updated Device',
            'status': 'offline',
            'modifier': self.user.id
        }
        response = self.client.patch(self.detail_url, update_data)
        logger.error(f"test_update_device response.data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.device_1.refresh_from_db()
        self.assertEqual(self.device_1.name, 'Updated Device')
        self.assertEqual(self.device_1.status, 'offline')

    def test_delete_device(self):
        """Test deleting a device"""
        response = self.client.delete(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Device.objects.count(), 1)

    def test_batch_destroy_devices(self):
        """Test batch destroying devices"""
        device_ids = [self.device_1.id, self.device_2.id]
        response = self.client.post(self.batch_destroy_url, device_ids, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Device.objects.count(), 0)

    def test_filter_devices(self):
        """Test filtering devices"""
        # Test name filter
        response = self.client.get(self.list_url, {'name': 'Test Device 1'})
        self.assertEqual(len(response.data['data']['results']), 1)
        self.assertEqual(response.data['data']['results'][0]['name'], 'Test Device 1')

        # Test manufacturer filter
        response = self.client.get(self.list_url, {'manufacturer': 'Test'})
        self.assertEqual(len(response.data['data']['results']), 1)
        self.assertEqual(response.data['data']['results'][0]['manufacturer'], 'Test Manufacturer')

        # Test type filter
        response = self.client.get(self.list_url, {'type': Device.TypeChoices.IPC.value})
        self.assertEqual(len(response.data['data']['results']), 1)
        self.assertEqual(response.data['data']['results'][0]['type']['value'], Device.TypeChoices.IPC.value)

        # Test status filter
        response = self.client.get(self.list_url, {'status': Device.StreamStatusChoices.ONLINE.value})
        self.assertEqual(len(response.data['data']['results']), 1)
        self.assertEqual(response.data['data']['results'][0]['status']['value'], Device.StreamStatusChoices.ONLINE.value)

    def test_query_action(self):
        """Test the custom query action"""
        # Test with single value
        data = {'type': Device.TypeChoices.IPC.value}
        response = self.client.post(self.query_url, query_params=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['results']), 1)
        self.assertEqual(response.data['data']['results'][0]['type']['value'], Device.TypeChoices.IPC.value)

        # Test with multiple filters
        data = {
            'manufacturer': 'Test Manufacturer',
            'status': Device.StreamStatusChoices.ONLINE.value
        }
        response = self.client.post(self.query_url, data, query_params=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['results']), 1)
        self.assertEqual(response.data['data']['results'][0]['name'], 'Test Device 1')

    def test_export_data(self):
        """Test exporting device data"""
        # Test XLSX export
        response = self.client.get(f"{self.export_url}?type=xlsx")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/xlsx; charset=utf-8')

    def test_create_device_invalid_data(self):
        """Test creating a device with invalid data"""
        data = {
            'name': '',  # Invalid empty name
            'device_id': '',  # Invalid empty device_id
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_batch_destroy_invalid_ids(self):
        """Test batch destroy with invalid IDs"""
        invalid_ids = [999999, 888888]  # Non-existent IDs
        response = self.client.post(self.batch_destroy_url, invalid_ids, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Device.objects.count(), 2)  # No devices should be deleted

    def test_query_action_invalid_data(self):
        """Test query action with invalid data"""
        data = {'invalid_field': 'invalid_value'}
        response = self.client.post(self.query_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['results']), 2)  # Should return all devices

    def test_export_data_invalid_type(self):
        """Test export data with invalid type"""
        response = self.client.get(f"{self.export_url}?type=invalid")
        print("Response data:", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @mock.patch('common.core.oss_helper.OSSHelper')
    def test_bind_channel_success(self, mock_oss_helper):
        """Test binding a channel to a device successfully"""
        # Mock OSS helper and bucket
        mock_bucket = mock.MagicMock()
        mock_create_result = mock.MagicMock()
        mock_create_result.publish_url = 'rtmp://test.com/live/test'
        mock_create_result.play_url = 'http://test.com/live/test.m3u8'
        
        mock_bucket.create_live_channel.return_value = mock_create_result
        mock_oss_helper.return_value.get_bucket_instance.return_value = mock_bucket

        # Make the bind channel request
        bind_url = reverse('device:device-bind-channel', kwargs={'pk': self.device_1.pk})
        response = self.client.post(bind_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['data']['success'])
        
        # Verify channel was created
        channel = response.data['data']['channel']
        self.assertTrue(channel['name'].startswith('channel_DEV001_'))
        self.assertEqual(channel['status']['value'], Channel.StatusChoices.ENABLED)
        self.assertEqual(channel['stream_status']['value'], Channel.StreamStatusChoices.OFFLINE)
        
        # Verify device was updated
        self.device_1.refresh_from_db()
        self.assertTrue(self.device_1.is_bound)
        
        # Verify device channel association
        device_channel = DeviceChannel.objects.filter(device=self.device_1, is_active=True)
        self.assertEqual(device_channel.count(), 1)
        
        # Verify old channels were deactivated
        old_channels = DeviceChannel.objects.filter(device=self.device_1, is_active=False)
        self.assertEqual(old_channels.count(), 0)  # Should be 0 since this is first binding

    @mock.patch('common.core.oss_helper.OSSHelper')
    def test_bind_channel_multiple_times(self, mock_oss_helper):
        """Test binding multiple channels to a device"""
        # Mock OSS helper and bucket
        mock_bucket = mock.MagicMock()
        mock_create_result = mock.MagicMock()
        mock_create_result.publish_url = 'rtmp://test.com/live/test'
        mock_create_result.play_url = 'http://test.com/live/test.m3u8'
        
        mock_bucket.create_live_channel.return_value = mock_create_result
        mock_oss_helper.return_value.get_bucket_instance.return_value = mock_bucket

        bind_url = reverse('device:device-bind-channel', kwargs={'pk': self.device_1.pk})
        
        # First binding
        response1 = self.client.post(bind_url)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # Second binding
        response2 = self.client.post(bind_url)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        
        # Verify only one active channel
        active_channels = DeviceChannel.objects.filter(device=self.device_1, is_active=True)
        self.assertEqual(active_channels.count(), 1)
        
        # Verify one inactive channel
        inactive_channels = DeviceChannel.objects.filter(device=self.device_1, is_active=False)
        self.assertEqual(inactive_channels.count(), 1)

    @mock.patch('common.core.oss_helper.OSSHelper')
    def test_bind_channel_oss_failure(self, mock_oss_helper):
        """Test binding channel when OSS operations fail"""
        # Mock OSS helper to raise an exception
        mock_bucket = mock.MagicMock()
        mock_bucket.create_live_channel.side_effect = Exception('OSS Error')
        mock_oss_helper.return_value.get_bucket_instance.return_value = mock_bucket

        bind_url = reverse('device:device-bind-channel', kwargs={'pk': self.device_1.pk})
        response = self.client.post(bind_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'OSS Error')
        
        # Verify no channel was created
        self.assertEqual(Channel.objects.count(), 0)
        
        # Verify device was not updated
        self.device_1.refresh_from_db()
        self.assertFalse(self.device_1.is_bound)
        
        # Verify no device channel association was created
        self.assertEqual(DeviceChannel.objects.count(), 0)

    def test_bind_channel_invalid_device(self):
        """Test binding channel to non-existent device"""
        bind_url = reverse('device:device-bind-channel', kwargs={'pk': 99999})
        response = self.client.post(bind_url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) 