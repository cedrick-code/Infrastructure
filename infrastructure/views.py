from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.shortcuts import render, redirect, get_object_or_404
from .models import Infrastructure
from django.contrib import messages

def infrastructure_list(request):

    infrastructures = Infrastructure.objects.all()

    return render(
        request,
        "infrastructure/infrastructure_list.html",
        {
            "infrastructures": infrastructures
        }
    )


@login_required
def add_infrastructure(request):

    # Only District Engineer can add infrastructure
    if request.user.role != "district_engineer":
        return HttpResponseForbidden(
            "Only District Engineer can manage infrastructure."
        )

    if request.method == "POST":

        infra_name = request.POST.get("infra_name")
        infra_type = request.POST.get("infra_type")
        road_classification = request.POST.get("road_classification")
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")
        location_description = request.POST.get("location_description")
        status = request.POST.get("status")

        # Validation

        if not infra_name:
            return render(
                request,
                "infrastructure/add_infrastructure.html",
                {
                    "error": "Infrastructure name is required."
                }
            )

        if not infra_type:
            return render(
                request,
                "infrastructure/add_infrastructure.html",
                {
                    "error": "Infrastructure type is required."
                }
            )

        if not latitude or not longitude:
            return render(
                request,
                "infrastructure/add_infrastructure.html",
                {
                    "error": "Latitude and longitude are required."
                }
            )

        if not status:
            return render(
                request,
                "infrastructure/add_infrastructure.html",
                {
                    "error": "Status is required."
                }
            )

        # Create infrastructure

        Infrastructure.objects.create(
            managed_by=request.user.personnel,
            infra_name=infra_name,
            infra_type=infra_type,
            road_classification=road_classification,
            latitude=latitude,
            longitude=longitude,
            location_description=location_description,
            status=status,
        )

        return redirect("infrastructure_list")

    return render(
        request,
        "infrastructure/add_infrastructure.html"
    )

@login_required
def edit_infrastructure(request, infrastructure_id):

    # Only District Engineer can edit infrastructure
    if request.user.role != "district_engineer":
        return HttpResponseForbidden(
            "Only District Engineer can manage infrastructure."
        )

    infrastructure = get_object_or_404(
        Infrastructure,
        infrastructure_id=infrastructure_id
    )

    if request.method == "POST":

        infrastructure.infra_name = request.POST.get("infra_name")
        infrastructure.infra_type = request.POST.get("infra_type")
        infrastructure.road_classification = request.POST.get(
            "road_classification"
        )
        infrastructure.latitude = request.POST.get("latitude")
        infrastructure.longitude = request.POST.get("longitude")
        infrastructure.location_description = request.POST.get(
            "location_description"
        )
        infrastructure.status = request.POST.get("status")

        infrastructure.save()

        return redirect("infrastructure_list")

    return render(
        request,
        "infrastructure/edit_infrastructure.html",
        {
            "infrastructure": infrastructure
        }
    )

@login_required
def view_infrastructure(request, infrastructure_id):

    if request.user.role != "district_engineer":
        return HttpResponseForbidden(
            "Only District Engineer can view infrastructure details."
        )

    infrastructure = get_object_or_404(
        Infrastructure,
        infrastructure_id=infrastructure_id
    )

    return render(
        request,
        "infrastructure/view_infrastructure.html",
        {
            "infrastructure": infrastructure
        }
    )

@login_required
def delete_infrastructure(request, infrastructure_id):

    if request.method == "POST":

        infrastructure = get_object_or_404(
            Infrastructure,
            infrastructure_id=infrastructure_id
        )

        infrastructure.delete()

        messages.success(
            request,
            "Infrastructure deleted successfully."
        )

        return redirect("infrastructure_list")

    return redirect("infrastructure_list")