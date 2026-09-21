from django.conf import settings
from django.db import models
from django.utils import timezone

from .vehicle import Vehicle


class InspectionReport(models.Model):
    """
    Pre-trip safety and physical inspection report.
    Document upload uses DEFAULT_FILE_STORAGE in 4.2 LTS (STORAGES in 5.1).
    """

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='inspections')
    inspector = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='conducted_inspections')
    inspected_at = models.DateTimeField('Inspection Date & Time', default=timezone.now)
    odometer_reading = models.PositiveIntegerField('Odometer at Inspection (km)')
    brakes_passed = models.BooleanField('Brakes Passed', default=True)
    tires_passed = models.BooleanField('Tires Passed', default=True)
    lights_passed = models.BooleanField('Lights & Signals Passed', default=True)
    fluids_passed = models.BooleanField('Fluids Checked', default=True)
    overall_passed = models.BooleanField('Overall Safety Passed', default=True)
    notes = models.TextField('Inspector Notes', blank=True)
    document = models.FileField(
        'Inspection Photo / Sheet',
        upload_to='inspections/%Y/%m/',
        blank=True,
        null=True
    )

    class Meta:
        ordering = ['-inspected_at']
        verbose_name = 'Inspection Report'
        verbose_name_plural = 'Inspection Reports'

    def __str__(self) -> str:
        status_text = "PASSED" if self.overall_passed else "FAILED"
        return f"Inspection #{self.pk or 'new'} - {self.vehicle.license_plate} ({status_text})"
