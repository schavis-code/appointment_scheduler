"""Admin registrations for appointment scheduler models."""

from django.contrib import admin

from .models import Appointment, Customer, Hairdresser, Service


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    "Admin configuration for customers."
    list_display = ("first_name", "last_name", "email", "phone", "created_at")
    search_fields = ("first_name", "last_name", "email", "phone")


@admin.register(Hairdresser)
class HairdresserAdmin(admin.ModelAdmin):
    "Admin configuration for hairdressers."
    list_display = ("first_name", "last_name", "email", "active", "created_at")
    list_filter = ("active",)
    search_fields = ("first_name", "last_name", "email")


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    "Admin configuration for services."
    list_display = ("name", "duration_minutes", "price", "active", "created_at")
    list_filter = ("active",)
    search_fields = ("name",)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    "Admin configuration for appointments."
    list_display = (
        "customer",
        "hairdresser",
        "service",
        "appointment_start",
        "appointment_end",
        "status",
    )
    list_filter = ("status", "hairdresser", "service")
    search_fields = (
        "customer__first_name",
        "customer__last_name",
        "customer__email",
        "customer__phone",
    )
