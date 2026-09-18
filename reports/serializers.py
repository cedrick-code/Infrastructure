from rest_framework import serializers
from .models import IssueReport, ReportPhoto, InspectionPhoto

class ReportPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportPhoto
        fields = ['id', 'image', 'uploaded_at']


class InspectionPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionPhoto
        fields = ['id', 'image', 'uploaded_at']


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