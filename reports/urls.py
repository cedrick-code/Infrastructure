from django.urls import path
from .views import (
    IssueReportCreateView, IssueReportListView, MyIssueReportListView,
    ValidatedIssueReportListView, SubmitInspectionView,
    InspectedReportListView, CreateWorkOrderView, MyWorkOrderListView,
    FieldEngineerListView, SubmitRepairUpdateView, RespondToInfoRequestView,
    NotificationListView, UnreadNotificationCountView,
    MarkNotificationReadView, MarkAllNotificationsReadView, SubmitFeedbackView,
)

urlpatterns = [
    path('create/', IssueReportCreateView.as_view(), name='report-create'),
    path('list/', IssueReportListView.as_view(), name='report-list'),
    path('my-reports/', MyIssueReportListView.as_view(), name='my-reports'),
    path('validated/', ValidatedIssueReportListView.as_view(), name='validated-reports'),
    path('<int:pk>/inspect/', SubmitInspectionView.as_view(), name='submit-inspection'),
    path('<int:pk>/respond/', RespondToInfoRequestView.as_view(), name='respond-info-request'),
    path('inspected/', InspectedReportListView.as_view(), name='inspected-reports'),
    path('work-orders/create/', CreateWorkOrderView.as_view(), name='work-order-create'),
    path('work-orders/my-orders/', MyWorkOrderListView.as_view(), name='my-work-orders'),
    path('field-engineers/', FieldEngineerListView.as_view(), name='field-engineers'),
    path('work-orders/repair-update/', SubmitRepairUpdateView.as_view(), name='submit-repair-update'),
    path('notifications/', NotificationListView.as_view(), name='notifications-list'),
    path('notifications/unread-count/', UnreadNotificationCountView.as_view(), name='notifications-unread-count'),
    path('notifications/read-all/', MarkAllNotificationsReadView.as_view(), name='notifications-read-all'),
    path('notifications/<int:pk>/read/', MarkNotificationReadView.as_view(), name='notification-read'),
    path('feedback/', SubmitFeedbackView.as_view(), name='submit-feedback'),
]