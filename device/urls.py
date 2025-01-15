from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeviceViewSet, ChannelViewSet, DeviceChannelViewSet
from rest_framework.routers import SimpleRouter


app_name = 'device'

router = SimpleRouter(False)

router.register('device', DeviceViewSet, basename='device')
router.register('channel', ChannelViewSet, basename='channel')
router.register('device-channel', DeviceChannelViewSet, basename='device-channel')

urlpatterns = [
]
urlpatterns += router.urls