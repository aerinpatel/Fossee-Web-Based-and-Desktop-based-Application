import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import FileUpload, Equipment
from .serializers import FileUploadSerializer
import json
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated

class UploadView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['file']
        
        # Save the file object first
        file_upload = FileUpload.objects.create(file=file)
        
        try:
            # Read CSV using Pandas
            # Note: file.file is the underlying file object
            df = pd.read_csv(file_upload.file.path)
            
            # Expected columns: Equipment Name, Type, Flowrate, Pressure, Temperature
            required_cols = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
            if not all(col in df.columns for col in required_cols):
                 file_upload.delete()
                 return Response({'error': f'Missing columns. Required: {required_cols}'}, status=status.HTTP_400_BAD_REQUEST)

            # Calculate Statistics
            total_count = len(df)
            avg_flowrate = df['Flowrate'].mean()
            avg_pressure = df['Pressure'].mean()
            avg_temperature = df['Temperature'].mean()
            type_distribution = df['Type'].value_counts().to_dict()

            stats = {
                'total_count': int(total_count),
                'average_flowrate': float(avg_flowrate),
                'average_pressure': float(avg_pressure),
                'average_temperature': float(avg_temperature),
                'type_distribution': type_distribution
            }
            
            file_upload.summary_statistics = stats
            file_upload.save()

            # Save Equipment Data
            equipment_list = []
            for _, row in df.iterrows():
                equipment_list.append(Equipment(
                    file_upload=file_upload,
                    name=row['Equipment Name'],
                    equipment_type=row['Type'],
                    flowrate=row['Flowrate'],
                    pressure=row['Pressure'],
                    temperature=row['Temperature']
                ))
            
            Equipment.objects.bulk_create(equipment_list)

            serializer = FileUploadSerializer(file_upload)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            file_upload.delete()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class HistoryView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        # Return last 5 uploads
        uploads = FileUpload.objects.order_by('-uploaded_at')[:5]
        serializer = FileUploadSerializer(uploads, many=True)
        return Response(serializer.data)

class ReportView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk, format=None):
        try:
            upload = FileUpload.objects.get(pk=pk)
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="report_{pk}.pdf"'
            
            p = canvas.Canvas(response)
            p.setFont("Helvetica-Bold", 16)
            p.drawString(100, 800, f"Analysis Report for Upload #{pk}")
            
            p.setFont("Helvetica", 12)
            p.drawString(100, 780, f"Uploaded at: {upload.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')}")
            
            y = 750
            p.drawString(100, y, "Summary Statistics:")
            y -= 20
            
            stats = upload.summary_statistics
            if stats:
                for key, value in stats.items():
                    if isinstance(value, dict):
                         p.drawString(120, y, f"{key}:")
                         y -= 20
                         for subk, subv in value.items():
                             p.drawString(140, y, f"{subk}: {subv}")
                             y -= 20
                    else:
                        p.drawString(120, y, f"{key.replace('_', ' ').capitalize()}: {value}")
                        y -= 20
            
            p.showPage()
            p.save()
            return response
        except FileUpload.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
