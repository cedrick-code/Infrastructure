from rest_framework import serializers
from .models import IssueReport, ReportPhoto

class ReportPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportPhoto
        fields = ['id', 'image', 'uploaded_at']


class IssueReportSerializer(serializers.ModelSerializer):
    photos = ReportPhotoSerializer(many=True, read_only=True)

    class Meta:
        model = IssueReport
        fields = [
            'id', 'citizen', 'title', 'description', 'infrastructure_type',
            'severity_level', 'status', 'latitude', 'longitude',
            'geographic_address', 'location_method',
            'reported_date', 'updated_date', 'photos',
        ]
        read_only_fields = ['citizen', 'status', 'reported_date', 'updated_date']