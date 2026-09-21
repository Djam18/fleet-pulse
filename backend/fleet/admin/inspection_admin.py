from django.contrib import admin
from django.utils.html import format_html

from fleet.models import InspectionReport


@admin.register(InspectionReport)
class InspectionReportAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'vehicle',
        'inspector',
        'inspected_at',
        'odometer_reading',
        'status_badge',
        'has_attachment'
    )
    list_filter = ('overall_passed', 'inspected_at', 'brakes_passed', 'tires_passed')
    search_fields = ('vehicle__license_plate', 'inspector__username', 'notes')
    date_hierarchy = 'inspected_at'
    readonly_fields = ('document_preview',)

    def status_badge(self, obj):
        if obj.overall_passed:
            return format_html('<span class="badge badge-passed">✓ PASSED</span>')
        return format_html('<span class="badge badge-failed">✗ FAILED</span>')
    status_badge.short_description = "Inspection Result"

    def has_attachment(self, obj):
        if obj.document:
            return format_html('<a href="{}" target="_blank">📄 View File</a>', obj.document.url)
        return "-"
    has_attachment.short_description = "Attachment"

    def document_preview(self, obj):
        if obj.document:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" style="max-height: 200px; border-radius: 4px; border: 1px solid #ccc;"/></a>',
                obj.document.url,
                obj.document.url
            )
        return "No document uploaded."
    document_preview.short_description = "Document Preview"
