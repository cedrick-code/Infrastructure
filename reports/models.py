from django.db import models
from django.conf import settings

class IssueReport(models.Model):
    SEVERITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]
    STATUS_CHOICES = [
        ('Pending Screening', 'Pending Screening'),
        ('Validated', 'Validated'),
        ('Rejected', 'Rejected'),
        ('Needs More Info', 'Needs More Information'),
        ('Inspected', 'Inspected'),
        ('For Work Order', 'For Work Order'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
    ]
    LOCATION_METHOD_CHOICES = [
        ('GPS', 'GPS'),
        ('Manual', 'Manual'),
    ]
    INFRASTRUCTURE_TYPE_CHOICES = [
        ('Road', 'Road'),
        ('Bridge', 'Bridge'),
        ('Drainage', 'Drainage'),
    ]

    citizen = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports')
    title = models.CharField(max_length=255)
    description = models.TextField()
    infrastructure_type = models.CharField(max_length=20, choices=INFRASTRUCTURE_TYPE_CHOICES)
    severity_level = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending Screening')
    latitude = models.DecimalField(max_digits=12, decimal_places=7)
    longitude = models.DecimalField(max_digits=12, decimal_places=7)
    geographic_address = models.CharField(max_length=500, blank=True, null=True)
    location_method = models.CharField(max_length=10, choices=LOCATION_METHOD_CHOICES, default='GPS')
    reported_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    screened_by = models.ForeignKey(
        'users.Personnel', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='screened_reports'
    )
    screening_remarks = models.TextField(blank=True, null=True)
    screened_date = models.DateTimeField(null=True, blank=True)
    inspected_by = models.ForeignKey(
        'users.Personnel', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='inspected_reports'
    )
    inspection_remarks = models.TextField(blank=True, null=True)
    recommended_action = models.TextField(blank=True, null=True)
    inspection_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.status})"


class ReportPhoto(models.Model):
    report = models.ForeignKey(IssueReport, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='report_photos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)



class InspectionPhoto(models.Model):
    report = models.ForeignKey(IssueReport, on_delete=models.CASCADE, related_name='inspection_photos')
    image = models.ImageField(upload_to='inspection_photos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)