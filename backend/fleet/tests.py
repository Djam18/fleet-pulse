from datetime import date

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from .models import InspectionReport, MaintenanceSchedule, TripLog, Vehicle

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

    def test_unique_vin_and_plate(self):
        with self.assertRaises(IntegrityError):
            Vehicle.objects.create(
                vin='1HGCR2F83HA123456',
                license_plate='OTHER-99',
                make='Ford',
                model='Transit',
                year=2023
            )


class TripLogTests(TestCase):
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
        """
        Verifies that in Django 4.2 LTS, save() properly calculates distance_km
        and updates the parent vehicle's current_odometer.
        """
        trip = TripLog.objects.create(
            vehicle=self.vehicle,
            driver=self.user,
            start_time=timezone.now(),
            start_odometer=20000,
            end_odometer=20350,
            fuel_liters=45.5,
            fuel_cost=85.00,
            purpose='Downtown deliveries'
        )

        self.assertEqual(trip.distance_km, 350)
        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.current_odometer, 20350)


class MaintenanceScheduleTests(TestCase):
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
            last_service_odometer=32000,  # 13,000 km since last service
            last_service_date=date(2023, 1, 15)
        )

        self.assertEqual(schedule.km_since_last_service, 13000)
        self.assertTrue(schedule.is_due)
        self.assertEqual(schedule.km_until_due, -3000)

    def test_unique_together_vehicle_service(self):
        MaintenanceSchedule.objects.create(
            vehicle=self.vehicle,
            service_code=MaintenanceSchedule.ServiceCode.TIRE_ROTATION,
            interval_km=12000,
            last_service_odometer=40000
        )
        with self.assertRaises(IntegrityError):
            MaintenanceSchedule.objects.create(
                vehicle=self.vehicle,
                service_code=MaintenanceSchedule.ServiceCode.TIRE_ROTATION,
                interval_km=15000,
                last_service_odometer=42000
            )


class InspectionReportTests(TestCase):
    def setUp(self):
        self.inspector = User.objects.create_user(username='inspector1', password='securepass123')
        self.vehicle = Vehicle.objects.create(
            vin='1HGCR2F83HA111222',
            license_plate='FLEET-404',
            make='Volvo',
            model='VHD',
            year=2020,
            current_odometer=90000
        )

    def test_inspection_report_creation(self):
        report = InspectionReport.objects.create(
            vehicle=self.vehicle,
            inspector=self.inspector,
            odometer_reading=90000,
            brakes_passed=True,
            tires_passed=True,
            lights_passed=True,
            fluids_passed=True,
            overall_passed=True,
            notes='Pre-trip inspection passed without defects.'
        )
        self.assertIn("PASSED", str(report))


class DashboardViewTests(TestCase):
    def test_dashboard_renders_successfully(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'fleet/dashboard.html')
        self.assertIn('vehicles', response.context)
        self.assertIn('total_vehicles', response.context)
