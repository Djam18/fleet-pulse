from django.core.management import call_command
from django.test import Client, RequestFactory, TestCase
from fleet.models import JobQueue
from fleet.services.queue import enqueue_job, process_pending_jobs
from fleet.views.errors import (
    bad_request_view,
    page_not_found_view,
    permission_denied_view,
    server_error_view,
)


class QueueAndErrorHandlersTestCase(TestCase):
    """Tests for asynchronous JobQueue processing and custom HTTP error handlers."""

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()

    def test_job_queue_enqueue_and_process(self):
        job = enqueue_job('recalc_maintenance_due', payload={'test': True})
        self.assertEqual(job.status, JobQueue.Status.PENDING)
        self.assertEqual(job.task_name, 'recalc_maintenance_due')

        processed = process_pending_jobs()
        self.assertEqual(processed, 1)

        job.refresh_from_db()
        self.assertEqual(job.status, JobQueue.Status.COMPLETED)
        self.assertIsNotNone(job.completed_at)

    def test_job_queue_unhandled_task_failure(self):
        job = enqueue_job('non_existent_task', payload={})
        processed = process_pending_jobs()
        self.assertEqual(processed, 0)

        job.refresh_from_db()
        self.assertEqual(job.status, JobQueue.Status.FAILED)
        self.assertIn("No handler registered", job.error_message)

    def test_process_jobs_management_command(self):
        enqueue_job('recalc_maintenance_due', payload={})
        call_command('process_jobs', once=True)
        self.assertFalse(JobQueue.objects.filter(status=JobQueue.Status.PENDING).exists())

    def test_custom_404_view(self):
        request = self.factory.get('/non-existent-page/')
        response = page_not_found_view(request)
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, '404', status_code=404)

    def test_custom_403_view(self):
        request = self.factory.get('/forbidden/')
        response = permission_denied_view(request)
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, '403', status_code=403)

    def test_custom_400_view(self):
        request = self.factory.get('/bad-request/')
        response = bad_request_view(request)
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, '400', status_code=400)

    def test_custom_500_view(self):
        request = self.factory.get('/server-error/')
        response = server_error_view(request)
        self.assertEqual(response.status_code, 500)
        self.assertContains(response, '500', status_code=500)
