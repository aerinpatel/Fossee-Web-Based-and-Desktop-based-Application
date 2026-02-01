from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Dataset
from .serializers import DatasetSerializer
from .services import analyze_csv

class DatasetUploadView(APIView):
    """
    Handles CSV file uploads and triggers the analysis engine.
    
    Accepts: multipart/form-data with a 'csv_file' and 'name'.
    Process: Saves the file, runs analysis, updates the model instance with results.
    """
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_serializer = DatasetSerializer(data=request.data)
        if file_serializer.is_valid():
            dataset = file_serializer.save()
            
            # Perform Analysis
            try:
                stats = analyze_csv(dataset.csv_file.path)
                
                # Update dataset with stats
                dataset.total_equipment = stats['total_equipment']
                dataset.avg_flowrate = stats['avg_flowrate']
                dataset.avg_pressure = stats['avg_pressure']
                dataset.avg_temperature = stats['avg_temperature']
                dataset.avg_health_score = stats['avg_health_score']
                dataset.equipment_type_distribution = stats['equipment_type_distribution']
                dataset.health_scores = stats['health_scores']
                dataset.equipment_data = stats['equipment_data']
                dataset.save()
                
                return Response(DatasetSerializer(dataset).data, status=status.HTTP_201_CREATED)
            except Exception as e:
                import traceback
                with open('debug_errors.log', 'w') as f:
                    f.write(str(e))
                    f.write(traceback.format_exc())
                dataset.delete() # Cleanup if analysis fails
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DatasetListView(generics.ListAPIView):
    """
    Retrieves the history of telemetry uploads.
    Optimized to return the last 5 datasets for the dashboard.
    """
    queryset = Dataset.objects.all().order_by('-uploaded_at')[:5] # Keep last 5 logic
    serializer_class = DatasetSerializer

class DatasetDetailView(generics.RetrieveDestroyAPIView):
    """
    Provides detailed metrics for a single dataset or allows its deletion.
    """
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer
    lookup_field = 'id'

class LatestDatasetView(APIView):
    """
    Specialized endpoint to fetch only the most recently uploaded equipment telemetry.
    Used for live dashboard initialization.
    """
    def get(self, request):
        latest = Dataset.objects.last()
        if latest:
            return Response(DatasetSerializer(latest).data)
        return Response({'detail': 'No datasets found'}, status=status.HTTP_404_NOT_FOUND)
