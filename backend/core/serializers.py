from rest_framework import serializers
from .models import FileUpload, Equipment

class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = '__all__'

class FileUploadSerializer(serializers.ModelSerializer):
    equipment_data = EquipmentSerializer(many=True, read_only=True)

    class Meta:
        model = FileUpload
        fields = ['id', 'file', 'uploaded_at', 'summary_statistics', 'equipment_data']
