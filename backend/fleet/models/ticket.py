from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from .vehicle import Vehicle


class StatusChangeRequest(models.Model):
    """
    Formal request submitted by normal operators to change vehicle status.
    Can be reviewed by an Admin or autonomously approved by the AI Agent when admins are offline.
    """

    class Priority(models.TextChoices):
        LOW = 'LOW', _('Low — Cosmetic / Non-Urgent')
        MEDIUM = 'MEDIUM', _('Medium — Scheduled Interval')
        HIGH = 'HIGH', _('High — Performance Issue')
        CRITICAL = 'CRITICAL', _('Critical — Safety Defect (Brakes, Tires)')

    class RequestStatus(models.TextChoices):
        PENDING = 'PENDING', _('Pending Review')
        AI_APPROVED = 'AI_APPROVED', _('Auto-Approved by AI Agent')
        ADMIN_APPROVED = 'ADMIN_APPROVED', _('Approved by Staff Admin')
        REJECTED = 'REJECTED', _('Rejected')

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='status_requests')
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='requested_status_changes')
    requested_status = models.CharField(max_length=20, choices=Vehicle.Status.choices)
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM)
    reason = models.TextField(_('Operational Reason / Observed Defect'))
    status = models.CharField(max_length=20, choices=RequestStatus.choices, default=RequestStatus.PENDING)
    decision_notes = models.TextField(_('Decision Rationale'), blank=True, default='')
    decided_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='decided_status_changes')
    decided_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Status Change Request')
        verbose_name_plural = _('Status Change Requests')

    def __str__(self):
        return f"Request #{self.id}: {self.vehicle.license_plate} -> {self.get_requested_status_display()} ({self.get_status_display()})"


class Notification(models.Model):
    """In-app alert notification sent to dispatchers and technicians."""
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fleet_notifications')
    title = models.CharField(max_length=150)
    message = models.TextField()
    link_url = models.CharField(max_length=255, blank=True, default='')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')

    def __str__(self):
        return f"To {self.recipient.username}: {self.title}"
