from django.contrib import admin
from .models import Infrastructure


@admin.register(Infrastructure)
class InfrastructureAdmin(admin.ModelAdmin):
    list_display = (
        "infrastructure_id",
        "infra_name",
        "infra_type",
        "road_classification",
        "status",
        "managed_by",
        "date_added",
    )

    list_filter = (
        "infra_type",
        "status",
    )

    search_fields = (
        "infra_name",
        "location_description",
    )