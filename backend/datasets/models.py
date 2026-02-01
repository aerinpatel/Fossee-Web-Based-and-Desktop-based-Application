from django.db import models

class Dataset(models.Model):
    """
    Represents a telemetry dataset uploaded to the system.
    
    This model stores the original CSV file along with pre-calculated 
    summary statistics and distribution data to optimize dashboard performance.
    
    Fields:
        name (str): Original filename or a custom identifier.
        csv_file (file): Path to the uploaded raw CSV file.
        uploaded_at (datetime): Timestamp of publication.
        total_equipment (int): Total number of items in the dataset.
        avg_flowrate (float): Mean flowrate across all equipment.
        avg_pressure (float): Mean pressure across all equipment.
        avg_temperature (float): Mean temperature across all equipment.
        avg_health_score (float): Calculated health index average.
        equipment_type_distribution (json): Breakdown of counts per equipment type.
        health_scores (json): Flat list of equipment names and their health scores.
        equipment_data (json): Full serialized representation of the dataset for visualizations.
    """
    name = models.CharField(max_length=255)
    csv_file = models.FileField(upload_to="uploads/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # Computed fields
    total_equipment = models.IntegerField(null=True, blank=True)
    avg_flowrate = models.FloatField(null=True, blank=True)
    avg_pressure = models.FloatField(null=True, blank=True)
    avg_temperature = models.FloatField(null=True, blank=True)
    avg_health_score = models.FloatField(null=True, blank=True)
    equipment_type_distribution = models.JSONField(null=True, blank=True)
    health_scores = models.JSONField(null=True, blank=True)
    equipment_data = models.JSONField(null=True, blank=True) # Storing full parsed data for scatter/line charts

    def __str__(self):
        return self.name
