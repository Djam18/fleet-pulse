from django.contrib import admin

from fleet.models import TripLog


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
