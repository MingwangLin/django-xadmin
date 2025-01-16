from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import ProjectBatchViewSet


app_name = 'project_batch'

router = SimpleRouter(False)

router.register('project-batch', ProjectBatchViewSet, basename='project-batch')

urlpatterns = [
]
urlpatterns += router.urls