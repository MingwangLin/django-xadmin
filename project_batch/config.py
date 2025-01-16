#!/usr/bin/env python
# -*- coding:utf-8 -*-

from django.urls import path, include
URLPATTERNS = [
    path('api/projectbatch/', include('project_batch.urls')),
]
PERMISSION_WHITE_REURL = []
