import io

from django.core.management import call_command
from django.test import TestCase

from fleet.models import Vehicle


class SeedFleetCommandTests(TestCase):
    def test_seed_fleet_management_command(self):
        out = io.StringIO()
        call_command('seed_fleet', stdout=out)
        output = out.getvalue()
        self.assertIn('FleetPulse database successfully seeded', output)
        self.assertTrue(Vehicle.objects.count() >= 5)
