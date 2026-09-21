from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum
from django.shortcuts import render

from fleet.models import InspectionReport, StatusChangeRequest, TripLog, Vehicle


@login_required
def dashboard_view(request):
    """Command Center for Admins, Driver Workspace for normal users."""
    status_choices = [
        {'value': choice[0], 'label': choice[1]}
        for choice in Vehicle.Status.choices
    ]
    all_vehicles = Vehicle.objects.filter(status=Vehicle.Status.ACTIVE)

    if not request.user.is_staff:
        driver_trips_qs = TripLog.objects.filter(driver=request.user)
        driver_trips_count = driver_trips_qs.count()
        driver_distance_km = driver_trips_qs.aggregate(Sum('distance_km'))['distance_km__sum'] or 0
        driver_recent_trips = list(driver_trips_qs.select_related('vehicle').order_by('-start_time')[:8])
        driver_recent_vehicle = driver_recent_trips[0].vehicle if driver_recent_trips else all_vehicles.first()
        driver_requests = StatusChangeRequest.objects.filter(requested_by=request.user).select_related('vehicle').order_by('-created_at')[:5]
        driver_pending_requests = StatusChangeRequest.objects.filter(
            requested_by=request.user, status=StatusChangeRequest.RequestStatus.PENDING
        ).count()

        context = {
            'is_driver_dashboard': True,
            'driver_trips_count': driver_trips_count,
            'driver_distance_km': driver_distance_km,
            'driver_recent_trips': driver_recent_trips,
            'driver_recent_vehicle': driver_recent_vehicle,
            'driver_requests': driver_requests,
            'driver_pending_requests': driver_pending_requests,
            'vehicles': all_vehicles,
            'status_choices': status_choices,
        }
        return render(request, 'fleet/dashboard.html', context)

    vehicles = Vehicle.objects.prefetch_related('maintenance_schedules', 'trips').all()
    fleet_stats = Vehicle.objects.aggregate(
        total=Count('id'),
        active=Count('id', filter=Q(status=Vehicle.Status.ACTIVE)),
        maintenance=Count('id', filter=Q(status=Vehicle.Status.MAINTENANCE)),
        retired=Count('id', filter=Q(status=Vehicle.Status.RETIRED)),
    )
    trip_stats = TripLog.objects.aggregate(
        total_trips=Count('id'),
        total_distance=Sum('distance_km'),
        total_fuel_cost=Sum('fuel_cost')
    )
    top_vehicles = list(
        Vehicle.objects.order_by('-current_odometer')[:6].values('license_plate', 'current_odometer')
    )
    chart_payload = {
        'mileage_labels': [v['license_plate'] for v in top_vehicles],
        'mileage_series': [v['current_odometer'] for v in top_vehicles],
        'status_labels': [str(s.label) for s in Vehicle.Status],
        'status_series': [
            fleet_stats['active'] or 0,
            fleet_stats['maintenance'] or 0,
            fleet_stats['retired'] or 0,
        ],
    }
    recent_trips = TripLog.objects.select_related('vehicle', 'driver').order_by('-start_time')[:5]
    recent_inspections = InspectionReport.objects.select_related('vehicle', 'inspector').order_by('-inspected_at')[:5]

    paginator = Paginator(vehicles, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'is_driver_dashboard': False,
        'page_obj': page_obj,
        'vehicles': page_obj,
        'status_choices': status_choices,
        'total_vehicles': fleet_stats['total'] or 0,
        'active_vehicles': fleet_stats['active'] or 0,
        'maintenance_vehicles': fleet_stats['maintenance'] or 0,
        'retired_vehicles': fleet_stats['retired'] or 0,
        'total_trips': trip_stats['total_trips'] or 0,
        'total_distance_km': trip_stats['total_distance'] or 0,
        'total_fuel_cost': trip_stats['total_fuel_cost'] or 0.0,
        'chart_payload': chart_payload,
        'recent_trips': recent_trips,
        'recent_inspections': recent_inspections,
    }
    return render(request, 'fleet/dashboard.html', context)
