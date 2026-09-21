from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from fleet.models import Notification, StatusChangeRequest, TripLog, Vehicle
from fleet.services.agent_tools import (
    check_fleet_readiness,
    create_quick_trip,
    evaluate_and_approve_request,
    query_vehicle_telematics,
)

User = get_user_model()


class AIAgentAndActionsTestCase(TestCase):
    """Tests for autonomous AI agent actions, offline auto-approval, and chat endpoints."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='driver_jean', password='password123', email='jean@fleet.com')
        self.vehicle = Vehicle.objects.create(
            vin='1HGCR2F83HA009999',
            license_plate='AB-999-CD',
            make='Renault',
            model='Master E-Tech',
            year=2023,
            status=Vehicle.Status.ACTIVE,
            fuel_type=Vehicle.FuelType.ELECTRIC,
            current_odometer=45000
        )

    def test_status_request_creation_and_non_critical_pending(self):
        self.client.login(username='driver_jean', password='password123')
        resp = self.client.post(reverse('fleet:status_request_create'), {
            'vehicle_id': self.vehicle.id,
            'requested_status': Vehicle.Status.MAINTENANCE,
            'priority': StatusChangeRequest.Priority.LOW,
            'reason': 'Léger bruit aérodynamique rétroviseur droit'
        })
        self.assertEqual(resp.status_code, 302)
        req = StatusChangeRequest.objects.get(vehicle=self.vehicle)
        self.assertEqual(req.status, StatusChangeRequest.RequestStatus.PENDING)
        self.assertEqual(self.vehicle.status, Vehicle.Status.ACTIVE)

    def test_ai_agent_autonomous_approval_safety_defect(self):
        req = StatusChangeRequest.objects.create(
            vehicle=self.vehicle,
            requested_by=self.user,
            requested_status=Vehicle.Status.MAINTENANCE,
            priority=StatusChangeRequest.Priority.CRITICAL,
            reason='Alerte système : défaillance plaquettes de frein et voyant rouge stop'
        )
        result = evaluate_and_approve_request(req.id)
        self.assertTrue(result.get('approved'))
        self.assertIn('autonomously', result.get('rationale', '').lower())

        self.vehicle.refresh_from_db()
        req.refresh_from_db()
        self.assertEqual(self.vehicle.status, Vehicle.Status.MAINTENANCE)
        self.assertEqual(req.status, StatusChangeRequest.RequestStatus.AI_APPROVED)
        self.assertTrue(Notification.objects.filter(recipient=self.user).exists())

    def test_query_vehicle_telematics_tool(self):
        data = query_vehicle_telematics('AB-999-CD')
        self.assertEqual(data['plate'], 'AB-999-CD')
        self.assertEqual(data['status'], 'Active & Operational')
        self.assertEqual(data['odometer_km'], 45000)

    def test_check_fleet_readiness_tool(self):
        readiness = check_fleet_readiness()
        self.assertGreaterEqual(readiness['total_vehicles'], 1)
        self.assertGreaterEqual(readiness['active_units'], 1)

    def test_create_quick_trip_tool_and_view(self):
        res = create_quick_trip('AB-999-CD', 85, self.user.username, 'Navette client express')
        self.assertTrue(res.get('success'))
        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.current_odometer, 45085)

        self.client.login(username='driver_jean', password='password123')
        resp = self.client.post(reverse('fleet:quick_trip_create'), {
            'license_plate': 'AB-999-CD',
            'distance_km': 15,
            'purpose': 'Transfert dépôt'
        })
        self.assertEqual(resp.status_code, 302)
        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.current_odometer, 45100)
        self.assertEqual(TripLog.objects.filter(vehicle=self.vehicle).count(), 2)

    def test_ai_chat_streaming_endpoint(self):
        self.client.login(username='driver_jean', password='password123')
        url = reverse('fleet:ai_chat') + '?prompt=flotte'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'text/event-stream')
        chunks = b"".join(resp.streaming_content).decode('utf-8')
        self.assertIn('data:', chunks)
        self.assertIn('event: done', chunks)

    def test_mark_notification_read_view(self):
        notif = Notification.objects.create(
            recipient=self.user,
            title='Alerte',
            message='Test notification'
        )
        self.client.login(username='driver_jean', password='password123')
        resp = self.client.get(reverse('fleet:mark_notification_read', kwargs={'pk': notif.id}))
        self.assertEqual(resp.status_code, 302)
        notif.refresh_from_db()
        self.assertTrue(notif.is_read)
