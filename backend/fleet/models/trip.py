from django.conf import settings
from django.db import models
from django.utils import timezone

from .vehicle import Vehicle


class TripLog(models.Model):
    """
    Records an operational trip completed by a driver.
    Distance computed in save() for Django 4.2 LTS baseline.
    """

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='trips')
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='driven_trips'
    )
    start_time = models.DateTimeField('Start Time', default=timezone.now)
    end_time = models.DateTimeField('End Time', null=True, blank=True)
    start_odometer = models.PositiveIntegerField('Start Odometer (km)')
    end_odometer = models.PositiveIntegerField('End Odometer (km)', null=True, blank=True)
    distance_km = models.PositiveIntegerField('Distance (km)', default=0)
    fuel_liters = models.DecimalField('Fuel (L)', max_digits=6, decimal_places=2, default=0.0)
    fuel_cost = models.DecimalField('Fuel Cost ($)', max_digits=8, decimal_places=2, default=0.0)
    purpose = models.CharField('Trip Purpose', max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_time']
        verbose_name = 'Trip Log'
        verbose_name_plural = 'Trip Logs'
        indexes = [
            models.Index(fields=['vehicle', '-start_time'], name='idx_trip_veh_start'),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_odometer__isnull=True) | models.Q(end_odometer__gte=models.F('start_odometer')),
                name='check_trip_end_gte_start'
            )
        ]

    def __str__(self) -> str:
        return f"Trip #{self.pk or 'new'} - {self.vehicle.license_plate} ({self.distance_km} km)"

    def save(self, *args, **kwargs):
        if self.end_odometer is not None and self.start_odometer is not None:
            self.distance_km = max(0, self.end_odometer - self.start_odometer)
            if self.vehicle and self.end_odometer > self.vehicle.current_odometer:
                self.vehicle.current_odometer = self.end_odometer
                self.vehicle.save(update_fields=['current_odometer', 'updated_at'])
        super().save(*args, **kwargs)
