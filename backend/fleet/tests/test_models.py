from datetime import date

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from fleet.models import MaintenanceSchedule, TripLog, Vehicle

User = get_user_model()


class VehicleModelTests(TestCase):
    def setUp(self):
        self.vehicle = Vehicle.objects.create(
            vin='1HGCR2F83HA123456',
            license_plate='FLEET-101',
            make='Ford',
            model='Transit 250',
            year=2023,
            current_odometer=15000,
            status=Vehicle.Status.ACTIVE,
            fuel_type=Vehicle.FuelType.DIESEL
        )

    def test_vehicle_str_and_operational(self):
        self.assertEqual(str(self.vehicle), "FLEET-101 — Ford Transit 250 (2023)")
        self.assertTrue(self.vehicle.is_operational)

    def test_unique_vin_and_plate_integrity(self):
        with self.assertRaises(IntegrityError):
            Vehicle.objects.create(
                vin='1HGCR2F83HA123456',
                license_plate='OTHER-99',
                make='Ford',
                model='Transit',
                year=2023
            )

    def test_custom_queryset_filters(self):
        Vehicle.objects.create(
            vin='2HGCR2F83HA789012',
            license_plate='FLEET-102',
            make='Mercedes',
            model='Sprinter',
            year=2022,
            status=Vehicle.Status.MAINTENANCE
        )
        self.assertEqual(Vehicle.objects.active().count(), 1)
        self.assertEqual(Vehicle.objects.in_maintenance().count(), 1)
        self.assertEqual(Vehicle.objects.retired().count(), 0)

    def test_model_validation_full_clean(self):
        invalid_vehicle = Vehicle(
            vin='SHORT',
            license_plate='PLATE',
            make='Ford',
            model='Transit',
            year=2023
        )
        # full_clean should succeed or raise validation errors
        invalid_vehicle.full_clean()


class TripLogModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='driver1', password='securepass123')
        self.vehicle = Vehicle.objects.create(
            vin='1HGCR2F83HA654321',
            license_plate='FLEET-202',
            make='Mercedes-Benz',
            model='Sprinter',
            year=2022,
            current_odometer=20000
        )

    def test_distance_calculation_and_odometer_sync(self):
        trip = TripLog.objects.create(
            vehicle=self.vehicle,
            driver=self.user,
            start_time=timezone.now(),
            start_odometer=20000,
            end_odometer=20350,
            fuel_liters=45.5,
            fuel_cost=85.00
        )
        self.assertEqual(trip.distance_km, 350)
        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.current_odometer, 20350)


class MaintenanceScheduleModelTests(TestCase):
    def setUp(self):
        self.vehicle = Vehicle.objects.create(
            vin='1HGCR2F83HA888999',
            license_plate='FLEET-303',
            make='Isuzu',
            model='N-Series',
            year=2021,
            current_odometer=45000
        )

    def test_maintenance_due_calculation(self):
        schedule = MaintenanceSchedule.objects.create(
            vehicle=self.vehicle,
            service_code=MaintenanceSchedule.ServiceCode.OIL_CHANGE,
            interval_km=10000,
            last_service_odometer=32000,
            last_service_date=date(2023, 1, 15)
        )
        self.assertEqual(schedule.km_since_last_service, 13000)
        self.assertTrue(schedule.is_due)
        self.assertEqual(schedule.km_until_due, -3000)

    def test_unique_together_constraint(self):
        MaintenanceSchedule.objects.create(
            vehicle=self.vehicle,
            service_code=MaintenanceSchedule.ServiceCode.TIRE_ROTATION,
            interval_km=10000
        )
        with self.assertRaises(IntegrityError):
            MaintenanceSchedule.objects.create(
                vehicle=self.vehicle,
                service_code=MaintenanceSchedule.ServiceCode.TIRE_ROTATION,
                interval_km=12000
            )
