from reports.models import IssueReport, InspectionValidation

created = 0
for r in IssueReport.objects.filter(inspection_date__isnull=False):
    if r.inspection_validations.exists():
        continue

    v = InspectionValidation.objects.create(
        report=r,
        inspected_by=r.inspected_by,
        validation_result='Confirmed',
        severity_rating=r.severity_level,
        findings=r.inspection_remarks or '',
        recommended_repairs=r.recommended_action or '',
    )
    InspectionValidation.objects.filter(pk=v.pk).update(inspection_date=r.inspection_date)
    created += 1

print("Inspection records created:", created)