from django.urls import path
from .views import DatasetUploadView, DatasetListView, DatasetDetailView, LatestDatasetView

urlpatterns = [
    path('upload/', DatasetUploadView.as_view(), name='dataset-upload'),
    path('history/', DatasetListView.as_view(), name='dataset-history'),
    path('latest/', LatestDatasetView.as_view(), name='dataset-latest'),
    path('<int:id>/', DatasetDetailView.as_view(), name='dataset-detail'),
]
