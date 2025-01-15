from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeviceViewSet
from rest_framework.routers import SimpleRouter


app_name = 'device'

router = SimpleRouter(False)

router.register('device', DeviceViewSet, basename='device')

urlpatterns = [
]
urlpatterns += router.urls