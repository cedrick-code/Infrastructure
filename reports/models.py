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
        ('Work Order Issued', 'Work Order Issued'),
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

class WorkOrder(models.Model):
    STATUS_CHOICES = [
        ('Issued', 'Issued'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]

    report = models.OneToOneField(
        IssueReport, on_delete=models.CASCADE, related_name='work_order'
    )
    issued_by = models.ForeignKey(
        'users.Personnel', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='issued_work_orders'
    )
    assigned_field_engineer = models.ForeignKey(
        'users.Personnel', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assigned_work_orders'
    )
    work_order_details = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Issued')
    date_issued = models.DateTimeField(auto_now_add=True)
    date_completed = models.DateTimeField(null=True, blank=True)
    update_requested = models.BooleanField(default=False)
    update_request_message = models.TextField(blank=True, null=True)
    update_requested_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Work Order #{self.id} - {self.report.title}"

class RepairUpdate(models.Model):
    STATUS_CHOICES = [
        ('Not Started', 'Not Started'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]

    work_order = models.ForeignKey(
        WorkOrder, on_delete=models.CASCADE, related_name='repair_updates'
    )
    submitted_by = models.ForeignKey(
        'users.Personnel', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='repair_updates'
    )
    status_update = models.CharField(max_length=20, choices=STATUS_CHOICES)
    progress_remarks = models.TextField(blank=True, null=True)
    delay_reason = models.TextField(blank=True, null=True)
    completion_details = models.TextField(blank=True, null=True)
    update_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Update for WO#{self.work_order_id} - {self.status_update}"


class RepairUpdatePhoto(models.Model):
    repair_update = models.ForeignKey(RepairUpdate, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='repair_photos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class InfoRequest(models.Model):
    report = models.ForeignKey(IssueReport, on_delete=models.CASCADE, related_name='info_requests')
    requested_by = models.ForeignKey(
        'users.Personnel', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='info_requests'
    )
    request_message = models.TextField(blank=True, null=True)
    requested_date = models.DateTimeField(auto_now_add=True)
    response_message = models.TextField(blank=True, null=True)
    response_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['requested_date']

    def __str__(self):
        return f"Info request for report #{self.report_id}"

class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications'
    )
    report = models.ForeignKey(
        IssueReport, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications'
    )
    kind = models.CharField(max_length=40)
    title = models.CharField(max_length=255)
    message = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} -> {self.recipient}"

class Feedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='feedbacks')
    report = models.OneToOneField('IssueReport', on_delete=models.CASCADE, related_name='feedback')
    comment = models.TextField(blank=True)
    rating = models.PositiveSmallIntegerField()  # 1 to 5
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback on report #{self.report_id} ({self.rating}/5)"