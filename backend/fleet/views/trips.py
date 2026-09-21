from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Sum
from django.shortcuts import render

from fleet.models import TripLog


@login_required
def trip_list_view(request):
    """Paginated trip logbook handling thousands of historical records."""
    trips = TripLog.objects.select_related('vehicle', 'driver').order_by('-start_time')

    stats = trips.aggregate(
        total_count=Count('id'),
        total_distance=Sum('distance_km'),
        total_fuel=Sum('fuel_cost')
    )

    paginator = Paginator(trips, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'stats': stats,
    }
    return render(request, 'fleet/trip_list.html', context)
