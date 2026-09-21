from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from fleet.models import InspectionReport, MaintenanceSchedule, TripLog, Vehicle

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds initial demonstration data for vehicles, maintenance schedules, and trip logs.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Beginning FleetPulse database seeding...'))

        # 1. Superuser / Demo Users
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@fleetpulse.local',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Created default superuser: admin / admin123'))
        else:
            self.stdout.write('Superuser "admin" already exists.')

        driver1, _ = User.objects.get_or_create(
            username='driver_sarah',
            defaults={'email': 'sarah@fleetpulse.local', 'first_name': 'Sarah', 'last_name': 'Connor'}
        )
        driver2, _ = User.objects.get_or_create(
            username='driver_alex',
            defaults={'email': 'alex@fleetpulse.local', 'first_name': 'Alex', 'last_name': 'Murphy'}
        )

        # 2. Vehicles
        vehicles_data = [
            {
                'vin': '1FTFW1ED4KFC12345',
                'license_plate': 'VAN-101',
                'make': 'Ford',
                'model': 'Transit Cargo 250',
                'year': 2023,
                'status': Vehicle.Status.ACTIVE,
                'fuel_type': Vehicle.FuelType.DIESEL,
                'current_odometer': 34500,
            },
            {
                'vin': 'WD3PF4CD8KP987654',
                'license_plate': 'VAN-202',
                'make': 'Mercedes-Benz',
                'model': 'Sprinter High Roof',
                'year': 2022,
                'status': Vehicle.Status.MAINTENANCE,
                'fuel_type': Vehicle.FuelType.DIESEL,
                'current_odometer': 62100,
            },
            {
                'vin': '4UZAA2AK3MC456789',
                'license_plate': 'TRK-303',
                'make': 'Freightliner',
                'model': 'M2 106 Box Truck',
                'year': 2021,
                'status': Vehicle.Status.ACTIVE,
                'fuel_type': Vehicle.FuelType.DIESEL,
                'current_odometer': 118400,
            },
            {
                'vin': '5YJSA1E21HF334455',
                'license_plate': 'EV-404',
                'make': 'Rivian',
                'model': 'Commercial Van EDV',
                'year': 2023,
                'status': Vehicle.Status.ACTIVE,
                'fuel_type': Vehicle.FuelType.ELECTRIC,
                'current_odometer': 14200,
            },
            {
                'vin': '1FDXE4FN8KDA11223',
                'license_plate': 'OLD-909',
                'make': 'Ford',
                'model': 'E-350 Super Duty',
                'year': 2018,
                'status': Vehicle.Status.RETIRED,
                'fuel_type': Vehicle.FuelType.PETROL,
                'current_odometer': 245000,
            },
        ]

        created_vehicles = []
        for v_data in vehicles_data:
            vehicle, created = Vehicle.objects.get_or_create(
                vin=v_data['vin'],
                defaults=v_data
            )
            created_vehicles.append(vehicle)
            if created:
                self.stdout.write(f"Created vehicle: {vehicle.license_plate} ({vehicle.make} {vehicle.model})")

        # 3. Maintenance Schedules
        v1 = created_vehicles[0]  # VAN-101 (34,500 km)
        v2 = created_vehicles[1]  # VAN-202 (62,100 km)
        v3 = created_vehicles[2]  # TRK-303 (118,400 km)

        MaintenanceSchedule.objects.get_or_create(
            vehicle=v1,
            service_code=MaintenanceSchedule.ServiceCode.OIL_CHANGE,
            defaults={
                'interval_km': 10000,
                'last_service_odometer': 30000,
                'last_service_date': date.today() - timedelta(days=45),
                'description': 'Full synthetic 5W-30 + oil filter replacement'
            }
        )

        MaintenanceSchedule.objects.get_or_create(
            vehicle=v2,
            service_code=MaintenanceSchedule.ServiceCode.BRAKE_SERVICE,
            defaults={
                'interval_km': 25000,
                'last_service_odometer': 35000,  # 27,100 km ago -> OVERDUE!
                'last_service_date': date.today() - timedelta(days=180),
                'description': 'Front brake pads worn, rotor resurfacing needed'
            }
        )

        MaintenanceSchedule.objects.get_or_create(
            vehicle=v3,
            service_code=MaintenanceSchedule.ServiceCode.ANNUAL_INSPECTION,
            defaults={
                'interval_km': 50000,
                'last_service_odometer': 80000,  # 38,400 km ago -> due in 11,600 km
                'last_service_date': date.today() - timedelta(days=90),
                'description': 'Commercial DOT safety certificate renewal'
            }
        )

        # 4. Trip Logs
        now = timezone.now()
        TripLog.objects.get_or_create(
            vehicle=v1,
            start_time=now - timedelta(days=2, hours=8),
            defaults={
                'end_time': now - timedelta(days=2, hours=3),
                'start_odometer': 34120,
                'end_odometer': 34500,
                'distance_km': 380,
                'fuel_liters': 48.0,
                'fuel_cost': 86.40,
                'purpose': 'Metro regional package delivery route',
                'driver': driver1
            }
        )

        TripLog.objects.get_or_create(
            vehicle=v3,
            start_time=now - timedelta(days=1, hours=6),
            defaults={
                'end_time': now - timedelta(days=1, hours=1),
                'start_odometer': 117850,
                'end_odometer': 118400,
                'distance_km': 550,
                'fuel_liters': 115.0,
                'fuel_cost': 218.50,
                'purpose': 'Interstate freight shipment transfer',
                'driver': driver2
            }
        )

        # 5. Inspection Reports
        InspectionReport.objects.get_or_create(
            vehicle=v1,
            inspected_at=now - timedelta(days=2, hours=9),
            defaults={
                'inspector': admin_user,
                'odometer_reading': 34120,
                'brakes_passed': True,
                'tires_passed': True,
                'lights_passed': True,
                'fluids_passed': True,
                'overall_passed': True,
                'notes': 'Pre-shift circle check verified. All lights and fluids nominal.'
            }
        )

        InspectionReport.objects.get_or_create(
            vehicle=v2,
            inspected_at=now - timedelta(days=1),
            defaults={
                'inspector': admin_user,
                'odometer_reading': 62100,
                'brakes_passed': False,
                'tires_passed': True,
                'lights_passed': True,
                'fluids_passed': True,
                'overall_passed': False,
                'notes': 'Brake pad squeal reported by driver. Flagged for workshop service.'
            }
        )

        self.stdout.write(self.style.SUCCESS('FleetPulse database successfully seeded with sample data!'))
