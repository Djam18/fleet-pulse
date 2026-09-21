from datetime import date, timedelta
import random
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from fleet.models import MaintenanceSchedule, StatusChangeRequest, Vehicle

from .seed_data import VEHICLES_DATA
from .seed_generator import generate_fleet_inspections, generate_fleet_trips
from .seed_users_data import NORMAL_DRIVERS_DATA, STAFF_ADMINS_DATA, SUPER_ADMINS_DATA

User = get_user_model()
DEMO_PASSWORD = 'fleetpulse2026!'


class Command(BaseCommand):
    help = 'Seeds 20 users (5 Super Admins, 5 Admins, 10 Drivers) & 3,000+ fleet operational records.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Seeding 20 demo users (Super Admins, Admins, Drivers)...'))

        # 1. Super Admins (5 users)
        super_admins = []
        for u in SUPER_ADMINS_DATA:
            user, _ = User.objects.get_or_create(
                username=u['username'],
                defaults={'email': u['email'], 'first_name': u['first_name'], 'last_name': u['last_name'], 'is_staff': True, 'is_superuser': True}
            )
            user.set_password(DEMO_PASSWORD)
            user.save()
            super_admins.append(user)

        # 2. Staff Admins (5 users)
        staff_admins = []
        for u in STAFF_ADMINS_DATA:
            user, _ = User.objects.get_or_create(
                username=u['username'],
                defaults={'email': u['email'], 'first_name': u['first_name'], 'last_name': u['last_name'], 'is_staff': True, 'is_superuser': False}
            )
            user.set_password(DEMO_PASSWORD)
            user.save()
            staff_admins.append(user)

        # 3. Normal Drivers (10 users)
        drivers = []
        for u in NORMAL_DRIVERS_DATA:
            user, _ = User.objects.get_or_create(
                username=u['username'],
                defaults={'email': u['email'], 'first_name': u['first_name'], 'last_name': u['last_name'], 'is_staff': False, 'is_superuser': False}
            )
            user.set_password(DEMO_PASSWORD)
            user.save()
            drivers.append(user)

        # 4. Vehicle Registry (20 units)
        vehicles = []
        for v_data in VEHICLES_DATA:
            v, _ = Vehicle.objects.get_or_create(vin=v_data['vin'], defaults=v_data)
            vehicles.append(v)

        # 5. Maintenance Schedules per vehicle
        codes = [
            MaintenanceSchedule.ServiceCode.OIL_CHANGE,
            MaintenanceSchedule.ServiceCode.TIRE_ROTATION,
            MaintenanceSchedule.ServiceCode.BRAKE_SERVICE,
            MaintenanceSchedule.ServiceCode.ANNUAL_INSPECTION
        ]
        for v in vehicles:
            for code in codes:
                MaintenanceSchedule.objects.get_or_create(
                    vehicle=v,
                    service_code=code,
                    defaults={'interval_km': 15000, 'last_service_odometer': max(0, v.current_odometer - 12000), 'last_service_date': date.today() - timedelta(days=60)}
                )

        # 6. Generate 3,000+ Trips across the 10 drivers
        self.stdout.write('Generating 3,000+ historical trips across 10 drivers...')
        generate_fleet_trips(vehicles, drivers, target_count=3000)

        # 7. Generate 350 Inspections
        self.stdout.write('Generating 350+ safety inspection reports...')
        generate_fleet_inspections(vehicles, staff_admins + super_admins, target_count=350)

        # 8. Seed Status Change Requests for Drivers
        self.stdout.write('Seeding realistic status change requests...')
        statuses = [
            StatusChangeRequest.RequestStatus.PENDING,
            StatusChangeRequest.RequestStatus.AI_APPROVED,
            StatusChangeRequest.RequestStatus.ADMIN_APPROVED,
            StatusChangeRequest.RequestStatus.REJECTED,
        ]
        reasons = [
            'Bruit suspect au niveau du train avant lors du freinage',
            'Voyant moteur allumé après le dernier trajet longue distance',
            'Pression pneumatique anormale sur l essieu arrière droit',
            'Révision périodique des 50 000 km requise par le constructeur',
        ]
        for d in drivers:
            v = random.choice(vehicles)
            StatusChangeRequest.objects.get_or_create(
                vehicle=v,
                requested_by=d,
                defaults={
                    'requested_status': Vehicle.Status.MAINTENANCE,
                    'reason': random.choice(reasons),
                    'status': random.choice(statuses),
                }
            )

        self.stdout.write(self.style.SUCCESS(
            'FleetPulse database successfully seeded with 3,000+ operational records! '
            f'20 Users ({len(super_admins)} SuperAdmins, {len(staff_admins)} Admins, {len(drivers)} Drivers). '
            'Default password: fleetpulse2026!'
        ))
