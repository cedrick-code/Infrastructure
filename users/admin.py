from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Personnel


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    fieldsets = UserAdmin.fieldsets + (
        ("Additional Information", {
            "fields": ("role",),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Additional Information", {
            "fields": ("role",),
        }),
    )

    list_display = (
        "username",
        "email",
        "role",
        "is_staff",
        "is_active",
    )

admin.site.register(Personnel)