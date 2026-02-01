from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from datasets.models import Dataset
from .utils import generate_pdf

from rest_framework import renderers

class PDFRenderer(renderers.BaseRenderer):
    """
    Custom DRF renderer for binary PDF content.
    """
    media_type = 'application/pdf'
    format = 'pdf'
    charset = None
    render_style = 'binary'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data

class DownloadPDFView(APIView):
    """
    API endpoint to trigger PDF report generation for a specific dataset.
    
    This view fetches telemetry data from the database and uses the ReportLab 
    utility to generate a formatted PDF document.
    """
    permission_classes = [permissions.AllowAny]
    renderer_classes = [PDFRenderer]

    def get(self, request, dataset_id):
        dataset = get_object_or_404(Dataset, id=dataset_id)
        
        try:
            pdf_buffer = generate_pdf(dataset)
            response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="report_{dataset.id}.pdf"'
            return response
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
