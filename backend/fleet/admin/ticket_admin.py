from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from fleet.models import Notification, StatusChangeRequest


@admin.register(StatusChangeRequest)
class StatusChangeRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'vehicle', 'requested_by', 'requested_status', 'priority_badge', 'status_badge', 'created_at']
    list_filter = ['status', 'priority', 'requested_status']
    search_fields = ['vehicle__license_plate', 'vehicle__vin', 'requested_by__username', 'reason']
    actions = ['approve_requests', 'reject_requests']

    def priority_badge(self, obj):
        colors = {
            StatusChangeRequest.Priority.LOW: '#64748b',
            StatusChangeRequest.Priority.MEDIUM: '#0284c7',
            StatusChangeRequest.Priority.HIGH: '#f59e0b',
            StatusChangeRequest.Priority.CRITICAL: '#ef4444',
        }
        color = colors.get(obj.priority, '#64748b')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 9999px; font-weight: 600; font-size: 0.72rem;">{}</span>',
            color, obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'

    def status_badge(self, obj):
        colors = {
            StatusChangeRequest.RequestStatus.PENDING: '#f59e0b',
            StatusChangeRequest.RequestStatus.AI_APPROVED: '#8b5cf6',
            StatusChangeRequest.RequestStatus.ADMIN_APPROVED: '#10b981',
            StatusChangeRequest.RequestStatus.REJECTED: '#ef4444',
        }
        color = colors.get(obj.status, '#64748b')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 9999px; font-weight: 600; font-size: 0.72rem;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    @admin.action(description='Approve selected requests (Update Vehicle Status)')
    def approve_requests(self, request, queryset):
        for req in queryset.filter(status=StatusChangeRequest.RequestStatus.PENDING):
            req.vehicle.status = req.requested_status
            req.vehicle.save(update_fields=['status'])
            req.status = StatusChangeRequest.RequestStatus.ADMIN_APPROVED
            req.decided_by = request.user
            req.decided_at = timezone.now()
            req.decision_notes = 'Approved by administrator'
            req.save(update_fields=['status', 'decided_by', 'decided_at', 'decision_notes'])
            Notification.objects.create(
                recipient=req.requested_by,
                title=f'Request Approved: {req.vehicle.license_plate}',
                message=f'Your request to set {req.vehicle.license_plate} to {req.get_requested_status_display()} was approved by {request.user.username}.'
            )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'recipient', 'title', 'is_read', 'created_at']
    list_filter = ['is_read']
    search_fields = ['recipient__username', 'title', 'message']
