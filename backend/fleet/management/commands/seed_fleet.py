from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from fleet.models import MaintenanceSchedule, Vehicle

from .seed_data import VEHICLES_DATA
from .seed_generator import generate_fleet_inspections, generate_fleet_trips

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds 3,000+ fleet records (trips, maintenance, inspections) from 2023-2026.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting large-scale FleetPulse database seeding (3,000+ rows)...'))

        # 1. Staff Admin, Dispatcher & Drivers
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@fleetpulse.local', 'is_staff': True, 'is_superuser': True}
        )
        admin_user.set_password('admin123')
        admin_user.save()

        dispatcher_user, _ = User.objects.get_or_create(
            username='dispatcher',
            defaults={'email': 'dispatcher@fleetpulse.local', 'first_name': 'David', 'last_name': 'Dispatch'}
        )
        dispatcher_user.set_password('dispatch123')
        dispatcher_user.save()

        driver_names = [('sarah_c', 'Sarah Connor'), ('alex_m', 'Alex Murphy'), ('marcus_w', 'Marcus Wright'), ('elena_r', 'Elena Rostova')]
        drivers = []
        for username, full_name in driver_names:
            first, last = full_name.split()
            d, _ = User.objects.get_or_create(username=username, defaults={'first_name': first, 'last_name': last, 'email': f'{username}@fleetpulse.local'})
            d.set_password('driver123')
            d.save()
            drivers.append(d)

        # 2. Vehicle Registry
        vehicles = []
        for v_data in VEHICLES_DATA:
            v, _ = Vehicle.objects.get_or_create(vin=v_data['vin'], defaults=v_data)
            vehicles.append(v)

        # 3. Maintenance Schedules per vehicle
        codes = [MaintenanceSchedule.ServiceCode.OIL_CHANGE, MaintenanceSchedule.ServiceCode.TIRE_ROTATION, MaintenanceSchedule.ServiceCode.BRAKE_SERVICE, MaintenanceSchedule.ServiceCode.ANNUAL_INSPECTION]
        for v in vehicles:
            for code in codes:
                MaintenanceSchedule.objects.get_or_create(
                    vehicle=v,
                    service_code=code,
                    defaults={'interval_km': 15000, 'last_service_odometer': max(0, v.current_odometer - 12000), 'last_service_date': date.today() - timedelta(days=60)}
                )

        # 4. Generate 3,000+ Trips & 350 Inspections via bulk_create
        self.stdout.write('Generating 3,000+ historical trips spanning 2023–2026...')
        generate_fleet_trips(vehicles, drivers, target_count=3000)

        self.stdout.write('Generating 350+ safety inspection reports...')
        generate_fleet_inspections(vehicles, [admin_user] + drivers, target_count=350)

        self.stdout.write(self.style.SUCCESS('FleetPulse database successfully seeded with 3,000+ operational records!'))
