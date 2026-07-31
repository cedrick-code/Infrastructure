from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_view, name="login"),
     path("district-dashboard/", views.district_dashboard, name="district_dashboard"),
     path("logout/", views.logout_view, name="logout"),
     path("personnel/add/", views.add_personnel, name="add_personnel"),
     path("personnel/", views.personnel, name="personnel"),
        
]