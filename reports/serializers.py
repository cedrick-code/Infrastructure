from rest_framework import serializers
from .models import IssueReport, ReportPhoto, InspectionPhoto, WorkOrder, RepairUpdate, RepairUpdatePhoto

class ReportPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportPhoto
        fields = ['id', 'image', 'uploaded_at']


class InspectionPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionPhoto
        fields = ['id', 'image', 'uploaded_at']


class RepairUpdatePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepairUpdatePhoto
        fields = ['id', 'image', 'uploaded_at']


class RepairUpdateSerializer(serializers.ModelSerializer):
    photos = RepairUpdatePhotoSerializer(many=True, read_only=True)
    submitted_by_name = serializers.SerializerMethodField()

    class Meta:
        model = RepairUpdate
        fields = [
            'id', 'work_order', 'submitted_by', 'submitted_by_name',
            'status_update', 'progress_remarks', 'delay_reason',
            'completion_details', 'update_date', 'photos',
        ]
        read_only_fields = ['submitted_by', 'update_date']

    def get_submitted_by_name(self, obj):
        if obj.submitted_by:
            return obj.submitted_by.user.get_full_name()
        return None


class IssueReportSerializer(serializers.ModelSerializer):
    photos = ReportPhotoSerializer(many=True, read_only=True)
    inspection_photos = InspectionPhotoSerializer(many=True, read_only=True)

    class Meta:
        model = IssueReport
        fields = [
            'id', 'citizen', 'title', 'description', 'infrastructure_type',
            'severity_level', 'status', 'latitude', 'longitude',
            'geographic_address', 'location_method',
            'reported_date', 'updated_date', 'photos',
            'screened_by', 'screening_remarks', 'screened_date',
            'inspected_by', 'inspection_remarks', 'recommended_action',
            'inspection_date', 'inspection_photos',
        ]
        read_only_fields = [
            'citizen', 'status', 'reported_date', 'updated_date',
            'screened_by', 'screening_remarks', 'screened_date',
            'inspected_by', 'inspection_remarks', 'recommended_action', 'inspection_date',
        ]


class WorkOrderSerializer(serializers.ModelSerializer):
    report_title = serializers.CharField(source='report.title', read_only=True)
    report_id = serializers.IntegerField(source='report.id', read_only=True)
    assigned_field_engineer_name = serializers.SerializerMethodField()
    repair_updates = RepairUpdateSerializer(many=True, read_only=True)

    class Meta:
        model = WorkOrder
        fields = [
            'id', 'report', 'report_id', 'report_title',
            'issued_by', 'assigned_field_engineer', 'assigned_field_engineer_name',
            'work_order_details', 'status', 'date_issued', 'date_completed',
            'update_requested', 'update_request_message', 'update_requested_date',
            'repair_updates',
        ]
        read_only_fields = ['issued_by', 'date_issued', 'status', 'date_completed']

    def get_assigned_field_engineer_name(self, obj):
        if obj.assigned_field_engineer:
            return obj.assigned_field_engineer.user.get_full_name()
        return None