from django.db import models
from django.urls import reverse


class VehicleQuerySet(models.QuerySet):
    """Custom QuerySet providing domain-specific filter methods."""

    def active(self):
        return self.filter(status=Vehicle.Status.ACTIVE)

    def in_maintenance(self):
        return self.filter(status=Vehicle.Status.MAINTENANCE)

    def retired(self):
        return self.filter(status=Vehicle.Status.RETIRED)


class Vehicle(models.Model):
    """Represents a commercial vehicle within the fleet."""

    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active & Operational'
        MAINTENANCE = 'MAINTENANCE', 'In Maintenance'
        RETIRED = 'RETIRED', 'Retired'

    class FuelType(models.TextChoices):
        DIESEL = 'DIESEL', 'Diesel'
        PETROL = 'PETROL', 'Petrol'
        ELECTRIC = 'ELECTRIC', 'Electric'
        HYBRID = 'HYBRID', 'Hybrid'

    vin = models.CharField('VIN', max_length=17, unique=True, help_text='17-character VIN')
    license_plate = models.CharField('License Plate', max_length=15, unique=True)
    make = models.CharField('Make', max_length=50)
    model = models.CharField('Model', max_length=50)
    year = models.PositiveIntegerField('Model Year')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    fuel_type = models.CharField(max_length=20, choices=FuelType.choices, default=FuelType.DIESEL)
    current_odometer = models.PositiveIntegerField('Current Odometer (km)', default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = VehicleQuerySet.as_manager()

    class Meta:
        ordering = ['license_plate']
        verbose_name = 'Vehicle'
        verbose_name_plural = 'Vehicles'
        indexes = [
            models.Index(fields=['status', 'fuel_type'], name='idx_vehicle_status_fuel'),
        ]

    def __str__(self) -> str:
        return f"{self.license_plate} — {self.make} {self.model} ({self.year})"

    def get_absolute_url(self) -> str:
        return reverse('fleet:vehicle_detail', args=[self.pk])

    @property
    def is_operational(self) -> bool:
        return self.status == self.Status.ACTIVE
