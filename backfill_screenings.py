from reports.models import IssueReport, ReportScreening

created = 0
for r in IssueReport.objects.filter(screened_date__isnull=False):
    if r.screenings.exists():
        continue

    if r.status in ('Validated', 'Needs More Info', 'Rejected'):
        result = r.status
    elif r.status == 'Pending Screening':
        # sent back for more info, then answered by the citizen
        result = 'Needs More Info'
    else:
        # already inspected, in repair, or resolved, so it passed screening
        result = 'Validated'

    s = ReportScreening.objects.create(
        report=r,
        screened_by=r.screened_by,
        screening_result=result,
        remarks=r.screening_remarks or '',
    )
    # keep the original screening time
    ReportScreening.objects.filter(pk=s.pk).update(screening_date=r.screened_date)
    created += 1

print("Screening records created:", created)