from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import translation

from fleet.models import Vehicle

User = get_user_model()


class LocalizationIntegrationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='dispatcher_intl',
            email='intl@fleetpulse.local',
            password='IntlPassword123!'
        )
        self.client.force_login(self.user)

    def test_french_translation_rendering_in_trip_list(self):
        response = self.client.get(reverse('fleet:trip_list'), HTTP_ACCEPT_LANGUAGE='fr')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Journal de bord commercial')
        self.assertContains(
            response,
            'Télémétrie historique complète sur plus de 3 000 trajets effectués.'
        )
        self.assertContains(response, 'Total enregistré')

    def test_spanish_translation_rendering_in_trip_list(self):
        response = self.client.get(reverse('fleet:trip_list'), HTTP_ACCEPT_LANGUAGE='es')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Libro de registro de viajes comerciales')
        self.assertContains(
            response,
            'Telemetría histórica completa en más de 3.000 viajes completados.'
        )
        self.assertContains(response, 'Total registrado')

    def test_language_switch_endpoint(self):
        response = self.client.post(reverse('set_language'), {
            'language': 'fr',
            'next': reverse('fleet:dashboard')
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.cookies.get('django_language').value, 'fr')

    def test_model_choice_gettext_lazy_translation(self):
        with translation.override('fr'):
            self.assertEqual(str(Vehicle.Status.ACTIVE.label), 'Actif et opérationnel')
            self.assertEqual(str(Vehicle.Status.MAINTENANCE.label), 'En maintenance')
            self.assertEqual(str(Vehicle.FuelType.ELECTRIC.label), 'Électrique')

        with translation.override('es'):
            self.assertEqual(str(Vehicle.Status.ACTIVE.label), 'Activo y operativo')
            self.assertEqual(str(Vehicle.Status.MAINTENANCE.label), 'En mantenimiento')
            self.assertEqual(str(Vehicle.FuelType.DIESEL.label), 'Diésel')
