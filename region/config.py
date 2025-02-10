from django.urls import path, include

URLPATTERNS = [
    path('api/region/', include('region.urls')),
]

PERMISSION_WHITE_REURL = []