from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import User, Personnel 
from django.contrib import messages

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
                return render(request, "users/login.html", {
                    "error": "FRU dashboard is under development."
                })

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

        employee_id = request.POST.get("employee_id")
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
            return redirect("add_personnel")

        if User.objects.filter(username=username).exists():

            messages.error(request, "Username already exists.")
            return redirect("add_personnel")

        if User.objects.filter(email=email).exists():

            messages.error(request, "Email already exists.")
            return redirect("add_personnel")

        if Personnel.objects.filter(employee_id=employee_id).exists():

            messages.error(request, "Employee ID already exists.")
            return redirect("add_personnel")
            

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

        Personnel.objects.create(
            user=user,
            employee_id=employee_id,
            contact_number=contact_number,
            address=address,
            position=position,
        )

        messages.success(request, "Personnel added successfully.")

        return redirect("personnel")

    return render(request, "users/district/add_personnel.html")

@login_required
def personnel(request):
    return render(request, "users/district/personnel.html")