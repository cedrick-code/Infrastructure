from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.utils import timezone
from .models import IssueReport, ReportPhoto, InspectionPhoto, WorkOrder, RepairUpdate, RepairUpdatePhoto
from .serializers import IssueReportSerializer, WorkOrderSerializer, RepairUpdateSerializer

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

class InspectedReportListView(generics.ListAPIView):
    """For District Engineer: reports ready for a work order."""
    serializer_class = IssueReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role != 'district_engineer':
            return IssueReport.objects.none()
        return IssueReport.objects.filter(status='Inspected').order_by('-inspection_date')


class CreateWorkOrderView(generics.CreateAPIView):
    """For District Engineer: create + assign a work order."""
    queryset = WorkOrder.objects.all()
    serializer_class = WorkOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.role != 'district_engineer':
            raise PermissionError('Only district engineers can create work orders.')

        work_order = serializer.save(issued_by=self.request.user.personnel)
        report = work_order.report
        report.status = 'Work Order Issued'
        report.save()


class MyWorkOrderListView(generics.ListAPIView):
    """For Field Engineer: work orders assigned to them."""
    serializer_class = WorkOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role != 'field_engineer':
            return WorkOrder.objects.none()
        return WorkOrder.objects.filter(
            assigned_field_engineer=self.request.user.personnel
        ).order_by('-date_issued')


class FieldEngineerListView(generics.ListAPIView):
    """For District Engineer: pick which field engineer to assign."""
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        from users.models import Personnel
        engineers = Personnel.objects.filter(position='field_engineer').select_related('user')
        data = [
            {
                'id': eng.id,
                'name': eng.user.get_full_name(),
                'employee_id': eng.employee_id,
            }
            for eng in engineers
        ]
        return Response(data)

class SubmitRepairUpdateView(generics.CreateAPIView):
    """For Field Engineer: submit a progress update on their work order."""
    queryset = RepairUpdate.objects.all()
    serializer_class = RepairUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        if self.request.user.role != 'field_engineer':
            raise PermissionError('Only field engineers can submit repair updates.')

        work_order = serializer.validated_data['work_order']

        if work_order.assigned_field_engineer != self.request.user.personnel:
            raise PermissionError('This work order is not assigned to you.')

        repair_update = serializer.save(submitted_by=self.request.user.personnel)

        for key in self.request.FILES:
            if key.startswith('repair_photo_'):
                RepairUpdatePhoto.objects.create(repair_update=repair_update, image=self.request.FILES[key])

        work_order.status = repair_update.status_update
        work_order.update_requested = False
        work_order.update_request_message = None
        if repair_update.status_update == 'Completed':
            work_order.date_completed = timezone.now()
            work_order.report.status = 'Resolved'
            work_order.report.save()
        elif repair_update.status_update == 'In Progress':
            work_order.report.status = 'In Progress'
            work_order.report.save()
        work_order.save()