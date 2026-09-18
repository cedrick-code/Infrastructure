from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.utils import timezone
from .models import IssueReport, ReportPhoto, InspectionPhoto
from .serializers import IssueReportSerializer

class IssueReportCreateView(generics.CreateAPIView):
    queryset = IssueReport.objects.all()
    serializer_class = IssueReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        report = serializer.save(citizen=self.request.user)
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


class ValidatedIssueReportListView(generics.ListAPIView):
    serializer_class = IssueReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role != 'field_engineer':
            return IssueReport.objects.none()
        return IssueReport.objects.filter(status='Validated').order_by('-reported_date')


class SubmitInspectionView(generics.UpdateAPIView):
    queryset = IssueReport.objects.all()
    serializer_class = IssueReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def update(self, request, *args, **kwargs):
        if request.user.role != 'field_engineer':
            return Response({'error': 'Only field engineers can submit inspections.'}, status=403)

        report = self.get_object()
        report.inspection_remarks = request.data.get('inspection_remarks', '')
        report.recommended_action = request.data.get('recommended_action', '')
        report.inspected_by = request.user.personnel
        report.inspection_date = timezone.now()
        report.status = 'Inspected'
        report.save()

        for key in request.FILES:
            if key.startswith('inspection_photo_'):
                InspectionPhoto.objects.create(report=report, image=request.FILES[key])

        serializer = self.get_serializer(report)
        return Response(serializer.data)