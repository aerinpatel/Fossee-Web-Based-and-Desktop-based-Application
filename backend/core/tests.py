from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import FileUpload, Equipment
import os

class APITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        
        # Create a sample CSV file
        csv_content = b"""Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-1,Pump,120,5.2,110
Valve-1,Valve,60,4.1,105
"""
        self.file = SimpleUploadedFile("test_data.csv", csv_content, content_type="text/csv")

    def test_upload_csv(self):
        response = self.client.post('/api/upload/', {'file': self.file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('summary_statistics', response.data)
        self.assertEqual(response.data['summary_statistics']['total_count'], 2)
        
        # Check database
        self.assertEqual(FileUpload.objects.count(), 1)
        self.assertEqual(Equipment.objects.count(), 2)

    def test_history_endpoint(self):
        # Create a dummy upload
        response = self.client.post('/api/upload/', {'file': self.file}, format='multipart')
        
        response = self.client.get('/api/history/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_report_endpoint(self):
        upload_response = self.client.post('/api/upload/', {'file': self.file}, format='multipart')
        upload_id = upload_response.data['id']
        
        response = self.client.get(f'/api/report/{upload_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
