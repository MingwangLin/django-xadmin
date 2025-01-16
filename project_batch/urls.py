from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import ProjectBatchViewSet


app_name = 'project_batch'

router = SimpleRouter(False)

router.register('projectbatch', ProjectBatchViewSet, basename='projectbatch')

urlpatterns = [
]
urlpatterns += router.urls