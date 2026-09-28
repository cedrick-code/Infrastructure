from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import (
    IssueReport, ReportPhoto, InspectionPhoto, WorkOrder,
    RepairUpdate, RepairUpdatePhoto, InfoRequest, Notification,
)
from .serializers import (
    IssueReportSerializer, WorkOrderSerializer, RepairUpdateSerializer,
    NotificationSerializer,
)
from .notifications import notify_users, notify_role


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

        notify_role(
            'fru', 'report_submitted', 'New report submitted',
            f'"{report.title}" is waiting for screening.', report,
        )


class IssueReportListView(generics.ListAPIView):
    serializer_class = IssueReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'citizen':
            return IssueReport.objects.filter(citizen=self.request.user).order_by('-reported_date')
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

        notify_role(
            'district_engineer', 'report_inspected', 'Inspection completed',
            f'"{report.title}" was inspected and is ready for a work order.', report,
        )
        notify_users(
            [report.citizen], 'report_inspected', 'Your report was inspected',
            f'A field engineer inspected "{report.title}".', report,
        )

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

        previous_status = work_order.status
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

        report = work_order.report
        notify_role(
            'district_engineer', 'repair_update', 'Repair update submitted',
            f'{repair_update.status_update}: "{report.title}"', report,
        )

        # Only tell the citizen when the status actually changed
        if repair_update.status_update != previous_status:
            if repair_update.status_update == 'Completed':
                notify_users(
                    [report.citizen], 'report_resolved', 'Your report was resolved',
                    f'The repair for "{report.title}" is complete.', report,
                )
            elif repair_update.status_update == 'In Progress':
                notify_users(
                    [report.citizen], 'repair_progress', 'Repair in progress',
                    f'Work has started on "{report.title}".', report,
                )


class RespondToInfoRequestView(generics.GenericAPIView):
    """For Citizen: send the extra information FRU asked for."""
    queryset = IssueReport.objects.all()
    serializer_class = IssueReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, pk):
        report = get_object_or_404(IssueReport, pk=pk, citizen=request.user)

        if report.status != 'Needs More Info':
            return Response({'error': 'This report is not waiting for more information.'}, status=400)

        response_message = request.data.get('response_message', '').strip()
        if not response_message:
            return Response({'error': 'Please provide the additional information.'}, status=400)

        info_request = report.info_requests.filter(
            response_date__isnull=True
        ).order_by('-requested_date').first()

        if info_request is None:
            info_request = InfoRequest.objects.create(
                report=report,
                request_message=report.screening_remarks or '',
            )

        info_request.response_message = response_message
        info_request.response_date = timezone.now()
        info_request.save()

        for key in request.FILES:
            if key.startswith('photo_'):
                ReportPhoto.objects.create(report=report, image=request.FILES[key])

        report.status = 'Pending Screening'
        report.save()

        notify_role(
            'fru', 'info_provided', 'Citizen replied',
            f'More information was added to "{report.title}". It is ready for re-screening.', report,
        )

        return Response(self.get_serializer(report).data)


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)[:50]


class UnreadNotificationCountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return Response({'count': count})


class MarkNotificationReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        return Response({'status': 'ok'})


class MarkAllNotificationsReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return Response({'status': 'ok'})