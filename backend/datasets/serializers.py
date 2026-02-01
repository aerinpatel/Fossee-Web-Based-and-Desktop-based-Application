from rest_framework import serializers
from .models import Dataset

class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = '__all__'
        read_only_fields = ['total_equipment', 'avg_flowrate', 'avg_pressure', 'avg_temperature', 'avg_health_score', 'equipment_type_distribution', 'health_scores', 'equipment_data']
