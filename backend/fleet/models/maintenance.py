from django.db import models
from django.utils import timezone

from .vehicle import Vehicle


class MaintenanceSchedule(models.Model):
    """
    Recurring maintenance schedule per vehicle.
    Enforces unique_together in 4.2 LTS (CompositePrimaryKey in 5.2 LTS).
    """

    class ServiceCode(models.TextChoices):
        OIL_CHANGE = 'OIL_CHANGE', 'Oil & Filter Change'
        TIRE_ROTATION = 'TIRE_ROTATION', 'Tire Rotation & Alignment'
        BRAKE_SERVICE = 'BRAKE_SERVICE', 'Brake Pad & Rotor Service'
        TRANSMISSION = 'TRANSMISSION', 'Transmission Fluid Flush'
        ANNUAL_INSPECTION = 'ANNUAL_INSPECTION', 'Annual Safety Certification'

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='maintenance_schedules')
    service_code = models.CharField('Service Code', max_length=50, choices=ServiceCode.choices)
    description = models.TextField('Notes & Specifications', blank=True)
    interval_km = models.PositiveIntegerField('Interval (km)', default=10000)
    last_service_odometer = models.PositiveIntegerField('Last Serviced At (km)', default=0)
    last_service_date = models.DateField('Last Serviced Date', default=timezone.now)

    class Meta:
        ordering = ['vehicle', 'service_code']
        verbose_name = 'Maintenance Schedule'
        verbose_name_plural = 'Maintenance Schedules'
        constraints = [
            models.UniqueConstraint(fields=['vehicle', 'service_code'], name='uniq_veh_service_code')
        ]

    def __str__(self) -> str:
        return f"{self.vehicle.license_plate} — {self.get_service_code_display()}"

    @property
    def km_since_last_service(self) -> int:
        return max(0, self.vehicle.current_odometer - self.last_service_odometer)

    @property
    def km_until_due(self) -> int:
        return self.interval_km - self.km_since_last_service

    @property
    def is_due(self) -> bool:
        return self.km_since_last_service >= self.interval_km
