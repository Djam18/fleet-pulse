from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from fleet.models import MaintenanceSchedule, TripLog, Vehicle


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
    list_per_page = 10
    inlines = [TripLogInLine, MaintenanceScheduleInLine]

    fieldsets = (
        ('Vehicle Identification', {'fields': ('vin', 'license_plate', 'make', 'model', 'year')}),
        ('Operations & Status', {'fields': ('status', 'fuel_type', 'current_odometer')}),
    )

    def get_queryset(self, request):
        """Optimizes queries by annotating trips and prefetching maintenance schedules."""
        return super().get_queryset(request).annotate(
            annotated_trips=Count('trips')
        ).prefetch_related('maintenance_schedules')

    def make_model_display(self, obj):
        return f"{obj.make} {obj.model}"
    make_model_display.short_description = "Make & Model"

    def current_odometer_display(self, obj):
        return f"{obj.current_odometer:,} km"
    current_odometer_display.short_description = "Odometer"

    def status_badge(self, obj):
        badge_map = {
            Vehicle.Status.ACTIVE: 'badge-active',
            Vehicle.Status.MAINTENANCE: 'badge-maintenance',
            Vehicle.Status.RETIRED: 'badge-retired'
        }
        return format_html('<span class="badge {}">{}</span>', badge_map.get(obj.status, 'badge-active'), obj.get_status_display())
    status_badge.short_description = "Status"

    def trips_count(self, obj):
        return getattr(obj, 'annotated_trips', obj.trips.count())
    trips_count.short_description = "Total Trips"
    trips_count.admin_order_field = 'annotated_trips'

    def pending_maintenance_badge(self, obj):
        overdue_count = sum(1 for m in obj.maintenance_schedules.all() if m.is_due)
        if overdue_count > 0:
            return format_html('<span class="badge badge-failed">⚠️ {} Overdue</span>', overdue_count)
        return format_html('<span class="badge badge-passed">All Clear</span>')
    pending_maintenance_badge.short_description = "Maintenance Health"
