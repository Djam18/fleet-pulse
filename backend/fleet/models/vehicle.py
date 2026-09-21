from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


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
        ACTIVE = 'ACTIVE', _('Active & Operational')
        MAINTENANCE = 'MAINTENANCE', _('In Maintenance')
        RETIRED = 'RETIRED', _('Retired')

    class FuelType(models.TextChoices):
        DIESEL = 'DIESEL', _('Diesel')
        PETROL = 'PETROL', _('Petrol')
        ELECTRIC = 'ELECTRIC', _('Electric')
        HYBRID = 'HYBRID', _('Hybrid')

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

    @property
    def overdue_schedules(self):
        return [s for s in self.maintenance_schedules.all() if s.is_due]

    @property
    def has_overdue_maintenance(self) -> bool:
        return any(s.is_due for s in self.maintenance_schedules.all())
