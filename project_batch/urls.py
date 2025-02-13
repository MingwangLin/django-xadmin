from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import ProjectBatchViewSet, ProjectBatchPreviewViewSet


app_name = 'project_batch'

router = SimpleRouter(False)

router.register('projectbatch', ProjectBatchViewSet, basename='projectbatch')
router.register('projectbatch-preview', ProjectBatchPreviewViewSet, basename='projectbatch-preview')

urlpatterns = [
]
urlpatterns += router.urls