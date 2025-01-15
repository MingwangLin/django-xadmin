#!/usr/bin/env python
# -*- coding:utf-8 -*-

from django.urls import path, include
URLPATTERNS = [
    path('api/device/', include('device.urls')),
]
PERMISSION_WHITE_REURL = []
