from django.contrib.auth import authenticate, get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class AuthenticationAndTelematicsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='marcus_fleet',
            email='marcus@fleetpulse.local',
            password='SecureFleetPassword123!'
        )

    def test_dual_auth_backend_with_username(self):
        user = authenticate(username='marcus_fleet', password='SecureFleetPassword123!')
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'marcus@fleetpulse.local')

    def test_dual_auth_backend_with_email(self):
        user = authenticate(username='marcus@fleetpulse.local', password='SecureFleetPassword123!')
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'marcus_fleet')

    def test_dual_auth_backend_invalid_credentials(self):
        user = authenticate(username='marcus_fleet', password='WrongPassword!')
        self.assertIsNone(user)

    def test_login_view_with_email(self):
        response = self.client.post(reverse('fleet:login'), {
            'username': 'marcus@fleetpulse.local',
            'password': 'SecureFleetPassword123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('fleet:dashboard'))

    def test_logout_view(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('fleet:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('fleet:login'))

    def test_password_reset_dispatches_email(self):
        response = self.client.post(reverse('fleet:password_reset'), {
            'email': 'marcus@fleetpulse.local'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('fleet:password_reset_done'))
        # Check mail was routed to outbox (which in production connects to Mailpit)
        self.assertEqual(len(mail.outbox), 1)
        sent_mail = mail.outbox[0]
        self.assertIn('Reset your operator password', sent_mail.subject)
        self.assertIn('marcus@fleetpulse.local', sent_mail.to)
        self.assertIn('marcus_fleet', sent_mail.body)

    def test_telematics_stream_headers_and_payload(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('fleet:telematics_stream') + '?limit=2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/event-stream')
        self.assertEqual(response['Cache-Control'], 'no-cache, no-transform')

        # Read the first event from the streaming iterator
        chunks = []
        for chunk in response.streaming_content:
            chunks.append(chunk.decode('utf-8') if isinstance(chunk, bytes) else chunk)
            if len(chunks) >= 2:
                break
        full_content = ''.join(chunks)
        self.assertIn('event: telematics', full_content)
        self.assertIn('license_plate', full_content)
