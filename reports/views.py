from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from .models import IssueReport, ReportPhoto
from .serializers import IssueReportSerializer

class IssueReportCreateView(generics.CreateAPIView):
    queryset = IssueReport.objects.all()
    serializer_class = IssueReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        report = serializer.save(citizen=self.request.user)
        # handle multiple photo uploads sent as photo_0, photo_1, ...
        for key in self.request.FILES:
            if key.startswith('photo_'):
                ReportPhoto.objects.create(report=report, image=self.request.FILES[key])


class IssueReportListView(generics.ListAPIView):
    serializer_class = IssueReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return IssueReport.objects.all().order_by('-reported_date')

class MyIssueReportListView(generics.ListAPIView):
    serializer_class = IssueReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return IssueReport.objects.filter(citizen=self.request.user).order_by('-reported_date')