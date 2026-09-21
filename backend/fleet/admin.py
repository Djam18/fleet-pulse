from django.contrib import admin
from django.utils.html import format_html

from .models import InspectionReport, MaintenanceSchedule, TripLog, Vehicle


class TripLogInLine(admin.TabularInline):
    """Shows recent trips directly within the Vehicle detail page."""
    model = TripLog
    extra = 0
    fields = ('start_time', 'end_time', 'start_odometer', 'end_odometer', 'distance_km', 'fuel_liters', 'fuel_cost', 'driver')
    readonly_fields = ('distance_km',)
    ordering = ('-start_time',)
    show_change_link = True


class MaintenanceScheduleInLine(admin.TabularInline):
    """Shows scheduled services directly within the Vehicle detail page."""
    model = MaintenanceSchedule
    extra = 1
    fields = ('service_code', 'interval_km', 'last_service_odometer', 'last_service_date', 'status_preview')
    readonly_fields = ('status_preview',)

    def status_preview(self, obj):
        if not obj.pk:
            return "-"
        if obj.is_due:
            return format_html('<span class="badge badge-failed">OVERDUE ({} km)</span>', abs(obj.km_until_due))
        return format_html('<span class="badge badge-passed">OK (in {} km)</span>', obj.km_until_due)
    status_preview.short_description = "Status"


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = (
        'license_plate',
        'make_model_display',
        'year',
        'status_badge',
        'fuel_type',
        'current_odometer_display',
        'trips_count',
        'pending_maintenance_badge'
    )
    list_filter = ('status', 'fuel_type', 'make', 'year')
    search_fields = ('license_plate', 'vin', 'make', 'model')
    ordering = ('license_plate',)
    inlines = [TripLogInLine, MaintenanceScheduleInLine]

    fieldsets = (
        ('Vehicle Identification', {
            'fields': ('vin', 'license_plate', 'make', 'model', 'year')
        }),
        ('Operations & Status', {
            'fields': ('status', 'fuel_type', 'current_odometer')
        }),
    )

    def make_model_display(self, obj):
        return f"{obj.make} {obj.model}"
    make_model_display.short_description = "Make & Model"

    def current_odometer_display(self, obj):
        return f"{obj.current_odometer:,} km"
    current_odometer_display.short_description = "Odometer"

    def status_badge(self, obj):
        css_class = {
            Vehicle.Status.ACTIVE: 'badge-active',
            Vehicle.Status.MAINTENANCE: 'badge-maintenance',
            Vehicle.Status.RETIRED: 'badge-retired'
        }.get(obj.status, 'badge-active')
        return format_html('<span class="badge {}">{}</span>', css_class, obj.get_status_display())
    status_badge.short_description = "Status"

    def trips_count(self, obj):
        return obj.trips.count()
    trips_count.short_description = "Total Trips"

    def pending_maintenance_badge(self, obj):
        overdue_count = sum(1 for m in obj.maintenance_schedules.all() if m.is_due)
        if overdue_count > 0:
            return format_html('<span class="badge badge-failed">⚠️ {} Overdue</span>', overdue_count)
        return format_html('<span class="badge badge-passed">All Clear</span>')
    pending_maintenance_badge.short_description = "Maintenance Health"


@admin.register(TripLog)
class TripLogAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'vehicle',
        'driver',
        'start_time',
        'start_odometer',
        'end_odometer',
        'distance_display',
        'fuel_cost_display'
    )
    list_filter = ('start_time', 'vehicle__status', 'vehicle__make')
    search_fields = ('vehicle__license_plate', 'vehicle__vin', 'driver__username', 'purpose')
    date_hierarchy = 'start_time'
    readonly_fields = ('distance_km', 'created_at')

    def distance_display(self, obj):
        return f"{obj.distance_km:,} km"
    distance_display.short_description = "Distance Traveled"

    def fuel_cost_display(self, obj):
        return f"${obj.fuel_cost:.2f}"
    fuel_cost_display.short_description = "Fuel Cost"


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

    def interval_display(self, obj):
        return f"Every {obj.interval_km:,} km"
    interval_display.short_description = "Interval"

    def status_indicator(self, obj):
        if obj.is_due:
            return format_html('<span class="badge badge-failed">DUE (Over by {} km)</span>', abs(obj.km_until_due))
        return format_html('<span class="badge badge-passed">OK (Due in {} km)</span>', obj.km_until_due)
    status_indicator.short_description = "Service Status"


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
