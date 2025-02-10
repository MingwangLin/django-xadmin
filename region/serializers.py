from rest_framework import serializers

from common.core.serializers import BaseModelSerializer
from region import models


class RegionSerializer(BaseModelSerializer):
    class Meta:
        model = models.Region
        fields = [
            'id', 'code', 'name', 'full_name', 'parent_id', 'type', 'sort_order',
            'description', 'status', 'tree_code', 'is_capital',
            'created_time', 'updated_time'
        ]
        table_fields = fields
        extra_kwargs = {
            'id': {'read_only': True},
        } 