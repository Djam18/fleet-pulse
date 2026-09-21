from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class JobQueue(models.Model):
    """
    Lightweight, database-backed asynchronous task queue for FleetPulse.
    Handles background processing (emails, maintenance audits, telematics batching)
    without requiring external message broker dependencies.
    """

    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        RUNNING = 'RUNNING', _('Running')
        COMPLETED = 'COMPLETED', _('Completed')
        FAILED = 'FAILED', _('Failed')

    task_name = models.CharField(max_length=100)
    payload = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    attempts = models.PositiveIntegerField(default=0)
    max_attempts = models.PositiveIntegerField(default=3)
    scheduled_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['scheduled_at', 'id']
        verbose_name = _('Job Queue Item')
        verbose_name_plural = _('Job Queue Items')
        indexes = [
            models.Index(fields=['status', 'scheduled_at'], name='idx_job_status_scheduled'),
        ]

    def __str__(self):
        return f"Job #{self.id}: {self.task_name} [{self.get_status_display()}]"
