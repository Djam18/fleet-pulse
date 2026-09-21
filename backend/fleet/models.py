from django.conf import settings
from django.db import models
from django.utils import timezone


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

    vin = models.CharField('VIN', max_length=17, unique=True, help_text='17-character Vehicle Identification Number')
    license_plate = models.CharField('License Plate', max_length=15, unique=True)
    make = models.CharField('Make', max_length=50)
    model = models.CharField('Model', max_length=50)
    year = models.PositiveIntegerField('Model Year')
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        help_text='Current operational state of the vehicle'
    )
    fuel_type = models.CharField(
        max_length=20,
        choices=FuelType.choices,
        default=FuelType.DIESEL
    )
    current_odometer = models.PositiveIntegerField(
        'Current Odometer (km)',
        default=0,
        help_text='Latest recorded odometer reading in kilometers'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['license_plate']
        verbose_name = 'Vehicle'
        verbose_name_plural = 'Vehicles'

    def __str__(self) -> str:
        return f"{self.license_plate} — {self.make} {self.model} ({self.year})"

    @property
    def is_operational(self) -> bool:
        return self.status == self.Status.ACTIVE


class TripLog(models.Model):
    """
    Records an operational trip completed by a driver.

    NOTE for Django 5.0 migration:
    In Django 4.2 LTS, 'distance_km' is computed and persisted via Python's save() method.
    In Django 5.0, this field will be migrated to a native database GeneratedField.
    """

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='trips'
    )
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
    distance_km = models.PositiveIntegerField(
        'Distance (km)',
        default=0,
        help_text='Calculated in Python save() in Django 4.2 (migrates to GeneratedField in Django 5.0)'
    )
    fuel_liters = models.DecimalField(
        'Fuel Purchased (Liters)',
        max_digits=6,
        decimal_places=2,
        default=0.0
    )
    fuel_cost = models.DecimalField(
        'Fuel Cost ($)',
        max_digits=8,
        decimal_places=2,
        default=0.0
    )
    purpose = models.CharField('Trip Purpose / Route', max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_time']
        verbose_name = 'Trip Log'
        verbose_name_plural = 'Trip Logs'

    def __str__(self) -> str:
        return f"Trip #{self.pk or 'new'} - {self.vehicle.license_plate} ({self.distance_km} km)"

    def save(self, *args, **kwargs):
        # Calculate distance traveled
        if self.end_odometer is not None and self.start_odometer is not None:
            self.distance_km = max(0, self.end_odometer - self.start_odometer)
            # Synchronize vehicle odometer if higher
            if self.vehicle and self.end_odometer > self.vehicle.current_odometer:
                self.vehicle.current_odometer = self.end_odometer
                self.vehicle.save(update_fields=['current_odometer', 'updated_at'])
        super().save(*args, **kwargs)


class MaintenanceSchedule(models.Model):
    """
    Recurring maintenance schedule per vehicle.

    NOTE for Django 5.2 LTS migration:
    In Django 4.2 LTS, uniqueness is enforced via unique_together = ('vehicle', 'service_code').
    In Django 5.2 LTS, this model will adopt models.CompositePrimaryKey('vehicle_id', 'service_code').
    """

    class ServiceCode(models.TextChoices):
        OIL_CHANGE = 'OIL_CHANGE', 'Oil & Filter Change'
        TIRE_ROTATION = 'TIRE_ROTATION', 'Tire Rotation & Alignment'
        BRAKE_SERVICE = 'BRAKE_SERVICE', 'Brake Pad & Rotor Service'
        TRANSMISSION = 'TRANSMISSION', 'Transmission Fluid Flush'
        ANNUAL_INSPECTION = 'ANNUAL_INSPECTION', 'Annual Safety Certification'

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='maintenance_schedules'
    )
    service_code = models.CharField(
        'Service Code',
        max_length=50,
        choices=ServiceCode.choices
    )
    description = models.TextField('Notes & Specifications', blank=True)
    interval_km = models.PositiveIntegerField(
        'Interval (km)',
        default=10000,
        help_text='Required maintenance interval in kilometers'
    )
    last_service_odometer = models.PositiveIntegerField(
        'Last Serviced At (km)',
        default=0
    )
    last_service_date = models.DateField('Last Serviced Date', default=timezone.now)

    class Meta:
        ordering = ['vehicle', 'service_code']
        unique_together = ('vehicle', 'service_code')
        verbose_name = 'Maintenance Schedule'
        verbose_name_plural = 'Maintenance Schedules'

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


class InspectionReport(models.Model):
    """
    Pre-trip safety and physical inspection report.

    NOTE for Django 5.1 migration:
    The 'document' field uses DEFAULT_FILE_STORAGE in Django 4.2 LTS.
    In Django 5.1, this setting is removed and handled by the STORAGES dict.
    """

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='inspections'
    )
    inspector = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conducted_inspections'
    )
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
        null=True,
        help_text='Upload signed inspection sheet or checklist image'
    )

    class Meta:
        ordering = ['-inspected_at']
        verbose_name = 'Inspection Report'
        verbose_name_plural = 'Inspection Reports'

    def __str__(self) -> str:
        status_text = "PASSED" if self.overall_passed else "FAILED"
        return f"Inspection #{self.pk or 'new'} - {self.vehicle.license_plate} ({status_text})"
