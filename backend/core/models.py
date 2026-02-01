from django.db import models

class FileUpload(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    summary_statistics = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Upload {self.id} at {self.uploaded_at}"

class Equipment(models.Model):
    file_upload = models.ForeignKey(FileUpload, on_delete=models.CASCADE, related_name='equipment_data')
    name = models.CharField(max_length=255)
    equipment_type = models.CharField(max_length=100)
    flowrate = models.FloatField()
    pressure = models.FloatField()
    temperature = models.FloatField()

    def __str__(self):
        return self.name
