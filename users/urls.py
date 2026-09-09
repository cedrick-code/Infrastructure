from django.urls import path
from . import views
from .views import CitizenRegisterAPIView, LoginAPIView, CitizenProfileAPIView

urlpatterns = [
    path("", views.landing_page, name="landing_page"),
    path("login/", views.login_view, name="login"),
    path("district-dashboard/", views.district_dashboard, name="district_dashboard"),
    path("logout/", views.logout_view, name="logout"),
    path("personnel/add/", views.add_personnel, name="add_personnel"),
    path("personnel/", views.personnel, name="personnel"),
    path("personnel/<int:pk>/view/", views.view_personnel, name="view_personnel"),
    path("personnel/<int:pk>/edit/", views.edit_personnel, name="edit_personnel"),
    path("personnel/<int:pk>/delete/", views.delete_personnel, name="delete_personnel"),
    path("validated-reports/", views.validated_reports, name="validated_reports"),
    path("work-orders/", views.work_orders, name="work_orders"),
    path("repair-monitoring/", views.repair_monitoring, name="repair_monitoring"),
    path("report-history/", views.report_history, name="report_history"),
    path("map/", views.map, name="map"),
    path("fru-dashboard/", views.fru_dashboard, name="fru_dashboard"),
    path("pending-reports/", views.pending_reports, name="pending_reports"),
    path("pending-reports/<int:pk>/screen/", views.screen_report, name="screen_report"),
    #dont delete
    path("api/citizen/register/", CitizenRegisterAPIView.as_view(), name="citizen_register"),
    path("api/login/", LoginAPIView.as_view(), name="login",),
    path("api/citizen/profile/", CitizenProfileAPIView.as_view(), name="citizen-profile",),
]