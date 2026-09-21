from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import TestCase

from fleet.admin.vehicle_admin import VehicleAdmin
from fleet.models import InspectionReport, MaintenanceSchedule, TripLog, Vehicle

User = get_user_model()


class FleetAdminTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser('admin_tester', 'test@fleetpulse.local', 'adminpass123')
        self.vehicle = Vehicle.objects.create(
            vin='1HGCR2F83HA999111',
            license_plate='ADM-001',
            make='Ford',
            model='Transit',
            year=2023,
            status=Vehicle.Status.ACTIVE
        )

    def test_models_registered_in_admin(self):
        self.assertIn(Vehicle, admin.site._registry)
        self.assertIn(TripLog, admin.site._registry)
        self.assertIn(MaintenanceSchedule, admin.site._registry)
        self.assertIn(InspectionReport, admin.site._registry)

    def test_admin_changelist_authenticated(self):
        self.client.login(username='admin_tester', password='adminpass123')
        response = self.client.get('/admin/fleet/vehicle/')
        self.assertEqual(response.status_code, 200)

    def test_admin_changelist_unauthenticated_redirect(self):
        response = self.client.get('/admin/fleet/vehicle/')
        self.assertEqual(response.status_code, 302)

    def test_vehicle_admin_status_badge_helper(self):
        vehicle_admin = VehicleAdmin(Vehicle, admin.site)
        badge_html = vehicle_admin.status_badge(self.vehicle)
        self.assertIn('badge-active', badge_html)
        self.assertIn('Active &amp; Operational', badge_html)
