from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import User, Personnel, Citizen
from django.contrib import messages
from datetime import date
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import ( CitizenRegisterSerializer, LoginSerializer, CitizenProfileSerializer, )
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

def login_view(request):

    if request.user.is_authenticated:

        if request.user.role == "district_engineer":
            return redirect("district_dashboard")
    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            if user.role == "district_engineer":
                return redirect("district_dashboard")

            elif user.role == "fru":
                return redirect("fru_dashboard")  

            elif user.role == "field_engineer":
                return render(request, "users/login.html", {
                    "error": "Field Engineer dashboard is under development."
                })

            elif user.role == "citizen":
                return render(request, "users/login.html", {
                    "error": "Citizen module is under development."
                })

        else:

            return render(request, "users/login.html", {
                "error": "Invalid username or password."
            })

    return render(request, "users/login.html")

@login_required
def district_dashboard(request):
    return render(request, "users/district/district_dashboard.html")

def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def add_personnel(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        contact_number = request.POST.get("contact_number")
        address = request.POST.get("address")
        position = request.POST.get("position")

        # ----------------------------
        # Validation
        # ----------------------------

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(
                request,
                "users/district/add_personnel.html"
            )

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(
                request,
                "users/district/add_personnel.html"
            )

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(
                request,
                "users/district/add_personnel.html"
            )

        # ----------------------------
        # Create User
        # ----------------------------

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=position,
        )

        # ----------------------------
        # Create Personnel
        # ----------------------------

        employee_id = generate_employee_id()

        Personnel.objects.create(
            user=user,
            employee_id=employee_id,
            contact_number=contact_number,
            address=address,
            position=position,
        )

        messages.success(
            request,
            f"Personnel added successfully. Employee ID: {employee_id}"
        )

        return redirect("personnel")

    return render(request, "users/district/add_personnel.html")


def generate_employee_id():
    """Generates the next sequential Employee ID for the current year, e.g. EMP-2026-0001."""

    year = date.today().year
    prefix = f"EMP-{year}-"

    last_personnel = (
        Personnel.objects
        .filter(employee_id__startswith=prefix)
        .order_by("-employee_id")
        .first()
    )

    if last_personnel:
        last_number = int(last_personnel.employee_id.split("-")[-1])
        next_number = last_number + 1
    else:
        next_number = 1

    return f"{prefix}{next_number:04d}"

@login_required
def personnel(request):

    personnel_list = Personnel.objects.select_related("user").all().order_by("-id")

    context = {
        "personnel_list": personnel_list,
    }

    return render(request, "users/district/personnel.html", context)

@login_required
def view_personnel(request, pk):

    person = get_object_or_404(Personnel.objects.select_related("user"), pk=pk)

    return render(request, "users/district/view_personnel.html", {
        "person": person
    })

@login_required
def delete_personnel(request, pk):

    if request.method == "POST":

        person = get_object_or_404(Personnel, pk=pk)
        person.user.delete()   # deletes the linked User; Personnel cascades if FK is CASCADE

        messages.success(request, "Personnel deleted successfully.")

        return redirect("personnel")

    return redirect("personnel")

@login_required
def edit_personnel(request, pk):

    person = get_object_or_404(Personnel.objects.select_related("user"), pk=pk)
    user = person.user

    if request.method == "POST":

        email = request.POST.get("email")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        contact_number = request.POST.get("contact_number")
        address = request.POST.get("address")
        position = request.POST.get("position")
        new_password = request.POST.get("new_password")

        # ----------------------------
        # Validation
        # ----------------------------

        if User.objects.filter(email=email).exclude(pk=user.pk).exists():

            messages.error(request, "Email already in use by another account.")
            return redirect("edit_personnel", pk=pk)

        # ----------------------------
        # Update User
        # ----------------------------

        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.role = position

        if new_password:
            user.set_password(new_password)

        user.save()

        # ----------------------------
        # Update Personnel
        # ----------------------------

        person.contact_number = contact_number
        person.address = address
        person.position = position
        person.save()

        messages.success(request, "Personnel updated successfully.")

        return redirect("personnel")

    return render(request, "users/district/edit_personnel.html", {
        "person": person
    })

@login_required
def fru_dashboard(request):

    from reports.models import IssueReport
    from django.utils import timezone

    pending_count = IssueReport.objects.filter(status="Pending Screening").count()
    screened_today = IssueReport.objects.filter(
        screened_date__date=timezone.now().date()
    ).count()

    context = {
        "pending_count": pending_count,
        "screened_today": screened_today,
        "notifications_count": 0,
    }

    return render(request, "users/fru/fru_dashboard.html", context)


@login_required
def pending_reports(request):

    from reports.models import IssueReport

    reports = IssueReport.objects.filter(
        status="Pending Screening"
    ).order_by('-reported_date')

    context = {
        "reports": reports,
    }

    return render(request, "users/fru/pending_reports.html", context)


@login_required
def screen_report(request, pk):

    from reports.models import IssueReport
    from django.utils import timezone

    report = get_object_or_404(IssueReport, pk=pk)

    if request.method == "POST":

        screening_result = request.POST.get("screening_result")
        screening_remarks = request.POST.get("screening_remarks")

        report.status = screening_result
        report.screening_remarks = screening_remarks
        report.screened_by = request.user.personnel
        report.screened_date = timezone.now()
        report.save()

        messages.success(request, "Report screened successfully.")
        return redirect("pending_reports")

    return render(request, "users/fru/screen_report.html", {
        "report": report,
    })

def validated_reports(request):
    # Placeholder for validated reports view
    return render(request, "users/district/validated_reports.html")

def work_orders(request):
    # Placeholder for work orders view
    return render(request, "users/district/work_orders.html")

def repair_monitoring(request):
    # Placeholder for repair monitoring view
    return render(request, "users/district/repair_monitoring.html")

def report_history(request):
    # Placeholder for report history view
    return render(request, "users/district/report_history.html")


def landing_page(request):
    return render(request, "users/landing_page.html")

#important dont delete
class CitizenRegisterAPIView(APIView):

    def post(self, request):
        serializer = CitizenRegisterSerializer(
            data=request.data
        )

        if serializer.is_valid():
            user = serializer.save()

            return Response({
                "message": "Citizen registered successfully.",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "role": user.role,
                }
            }, status=status.HTTP_201_CREATED)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class LoginAPIView(APIView):

    def post(self, request):
        serializer = LoginSerializer(
            data=request.data
        )

        if serializer.is_valid():
            user = serializer.validated_data["user"]

            token, created = Token.objects.get_or_create(
                user=user
            )

            return Response({
                "message": "Login successful.",
                "token": token.key,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "role": user.role,
                }
            }, status=status.HTTP_200_OK)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class CitizenProfileAPIView(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):

        user = request.user

        if user.role != "citizen":
            return Response(
                {
                    "error": "This endpoint is for citizens only."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            citizen = user.citizen_profile

        except Citizen.DoesNotExist:
            return Response(
                {
                    "error": "Citizen profile not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CitizenProfileSerializer(citizen)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )