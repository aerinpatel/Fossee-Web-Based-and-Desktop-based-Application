from django.urls import path
from .views import DownloadPDFView

urlpatterns = [
    path('<int:dataset_id>/pdf/', DownloadPDFView.as_view(), name='download-pdf'),
]
