"Models for the hairdresser app"
from django.db import models


class Customer(models.Model):
    "A person booking an appointment."
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        db_table = "customers"


class Hairdresser(models.Model):
    "A staff member who provides services."
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=255, blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        db_table = "hairdressers"


class Service(models.Model):
    "A bookable service."
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    duration_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "services"


class Appointment(models.Model):
    "A scheduled appointment between a customer and hairdresser."

    class Status(models.TextChoices):  # pylint: disable=too-many-ancestors
        "Allowed appointment workflow states."
        SCHEDULED = "scheduled", "Scheduled"
        CONFIRMED = "confirmed", "Confirmed"
        CHECKED_IN = "checked_in", "Checked In"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        NO_SHOW = "no_show", "No Show"

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    hairdresser = models.ForeignKey(Hairdresser, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    appointment_start = models.DateTimeField()
    appointment_end = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED,
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.customer} with {self.hairdresser} at {self.appointment_start}"

    class Meta:
        db_table = "appointments"
        indexes = [
            models.Index(fields=["appointment_start"], name="idx_appointments_start"),
            models.Index(
                fields=["hairdresser", "appointment_start"],
                name="idx_appt_hairdresser_start",
            ),
        ]
