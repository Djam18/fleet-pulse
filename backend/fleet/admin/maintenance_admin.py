from django.contrib import admin
from django.utils.html import format_html

from fleet.models import MaintenanceSchedule


@admin.register(MaintenanceSchedule)
class MaintenanceScheduleAdmin(admin.ModelAdmin):
    list_display = (
        'vehicle',
        'service_code',
        'interval_display',
        'last_service_odometer',
        'status_indicator'
    )
    list_filter = ('service_code', 'vehicle__status')
    search_fields = ('vehicle__license_plate', 'service_code', 'description')
    list_per_page = 10

    def interval_display(self, obj):
        return f"Every {obj.interval_km:,} km"
    interval_display.short_description = "Interval"

    def status_indicator(self, obj):
        if obj.is_due:
            return format_html('<span class="badge badge-failed">DUE (Over by {} km)</span>', abs(obj.km_until_due))
        return format_html('<span class="badge badge-passed">OK (Due in {} km)</span>', obj.km_until_due)
    status_indicator.short_description = "Service Status"
