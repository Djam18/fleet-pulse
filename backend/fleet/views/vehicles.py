from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from fleet.models import Vehicle


@login_required
def vehicle_list_view(request):
    """Searchable, filterable, and paginated vehicle directory."""
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    fuel_filter = request.GET.get('fuel', '').strip()

    vehicles = Vehicle.objects.prefetch_related('maintenance_schedules', 'trips').all()

    if query:
        vehicles = vehicles.filter(
            Q(license_plate__icontains=query) | Q(vin__icontains=query) |
            Q(make__icontains=query) | Q(model__icontains=query)
        )
    if status_filter:
        vehicles = vehicles.filter(status=status_filter)
    if fuel_filter:
        vehicles = vehicles.filter(fuel_type=fuel_filter)

    paginator = Paginator(vehicles, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
        'selected_status': status_filter,
        'selected_fuel': fuel_filter,
        'status_choices': Vehicle.Status.choices,
        'fuel_choices': Vehicle.FuelType.choices,
    }
    return render(request, 'fleet/vehicle_list.html', context)


@login_required
def vehicle_detail_view(request, pk):
    """Deep profile of a single commercial vehicle with lifetime telemetry."""
    vehicle = get_object_or_404(
        Vehicle.objects.prefetch_related('maintenance_schedules', 'trips', 'inspections'),
        pk=pk
    )
    trips = vehicle.trips.select_related('driver').order_by('-start_time')[:10]
    inspections = vehicle.inspections.select_related('inspector').order_by('-inspected_at')[:5]

    context = {
        'vehicle': vehicle,
        'trips': trips,
        'inspections': inspections,
    }
    return render(request, 'fleet/vehicle_detail.html', context)
