from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from fleet.models import Vehicle
from fleet.views import dashboard_view

User = get_user_model()


class OperationsPagesTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='dispatcher1',
            email='dispatcher1@fleetpulse.local',
            password='TestPassword123!'
        )
        self.client.force_login(self.user)
        self.vehicle = Vehicle.objects.create(
            vin='1HGCR2F83HA111222',
            license_plate='TEST-100',
            make='Ford',
            model='Transit',
            year=2023,
            status=Vehicle.Status.ACTIVE
        )

    def test_unauthenticated_user_redirected_to_login(self):
        self.client.logout()
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_dashboard_client_integration(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'fleet/dashboard.html')
        self.assertIn('vehicles', response.context)
        self.assertIn('status_choices', response.context)

    def test_dashboard_request_factory_isolation(self):
        request = self.factory.get('/')
        request.user = self.user
        response = dashboard_view(request)
        self.assertEqual(response.status_code, 200)

    def test_dashboard_with_locale_header(self):
        response = self.client.get('/', HTTP_ACCEPT_LANGUAGE='fr')
        self.assertEqual(response.status_code, 200)

    def test_vehicle_list_view(self):
        response = self.client.get('/vehicles/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'fleet/vehicle_list.html')
        self.assertIn('page_obj', response.context)

    def test_vehicle_detail_view(self):
        response = self.client.get(f'/vehicles/{self.vehicle.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'fleet/vehicle_detail.html')
        self.assertEqual(response.context['vehicle'], self.vehicle)

    def test_trip_list_view(self):
        response = self.client.get('/trips/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'fleet/trip_list.html')
        self.assertIn('page_obj', response.context)

    def test_maintenance_list_view(self):
        response = self.client.get('/maintenance/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'fleet/maintenance_list.html')
        self.assertIn('page_obj', response.context)

    def test_inspection_list_view(self):
        response = self.client.get('/inspections/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'fleet/inspection_list.html')
        self.assertIn('page_obj', response.context)
