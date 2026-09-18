from django.urls import path
from .views import (
    IssueReportCreateView, IssueReportListView, MyIssueReportListView,
    ValidatedIssueReportListView, SubmitInspectionView,
)

urlpatterns = [
    path('create/', IssueReportCreateView.as_view(), name='report-create'),
    path('list/', IssueReportListView.as_view(), name='report-list'),
    path('my-reports/', MyIssueReportListView.as_view(), name='my-reports'),
    path('validated/', ValidatedIssueReportListView.as_view(), name='validated-reports'),
    path('<int:pk>/inspect/', SubmitInspectionView.as_view(), name='submit-inspection'),
]