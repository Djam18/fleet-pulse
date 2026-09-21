from django.db.models import Sum
from django.shortcuts import render

from .models import InspectionReport, TripLog, Vehicle


def dashboard_view(request):
    """
    FleetPulse Overview Dashboard View.
    Displays fleet KPIs, vehicle availability, and recent operational logs.
    """
    vehicles = Vehicle.objects.prefetch_related('maintenance_schedules', 'trips').all()

    total_vehicles = vehicles.count()
    active_vehicles = sum(1 for v in vehicles if v.status == Vehicle.Status.ACTIVE)
    maintenance_vehicles = sum(1 for v in vehicles if v.status == Vehicle.Status.MAINTENANCE)
    retired_vehicles = sum(1 for v in vehicles if v.status == Vehicle.Status.RETIRED)

    total_trips = TripLog.objects.count()
    total_distance_km = TripLog.objects.aggregate(total=Sum('distance_km'))['total'] or 0

    recent_trips = TripLog.objects.select_related('vehicle', 'driver').order_by('-start_time')[:5]
    recent_inspections = InspectionReport.objects.select_related('vehicle', 'inspector').order_by('-inspected_at')[:5]

    context = {
        'vehicles': vehicles,
        'total_vehicles': total_vehicles,
        'active_vehicles': active_vehicles,
        'maintenance_vehicles': maintenance_vehicles,
        'retired_vehicles': retired_vehicles,
        'total_trips': total_trips,
        'total_distance_km': total_distance_km,
        'recent_trips': recent_trips,
        'recent_inspections': recent_inspections,
    }
    return render(request, 'fleet/dashboard.html', context)
