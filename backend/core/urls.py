from django.urls import path
from .views import UploadView, HistoryView, ReportView

urlpatterns = [
    path('upload/', UploadView.as_view(), name='upload'),
    path('history/', HistoryView.as_view(), name='history'),
    path('report/<int:pk>/', ReportView.as_view(), name='report'),
]
