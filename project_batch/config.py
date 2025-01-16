#!/usr/bin/env python
# -*- coding:utf-8 -*-

from django.urls import path, include
URLPATTERNS = [
    path('api/project-batch/', include('project_batch.urls')),
]
PERMISSION_WHITE_REURL = []
