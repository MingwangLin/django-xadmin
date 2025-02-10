from rest_framework.routers import SimpleRouter

from region.views import RegionViewSet

app_name = 'region'

router = SimpleRouter(False)  # Set to False to remove trailing slashes

router.register('region', RegionViewSet, basename='region')

urlpatterns = [
]
urlpatterns += router.urls 