from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render

from fleet.models import MaintenanceSchedule


@login_required
def maintenance_list_view(request):
    """Overview of all recurring fleet maintenance work orders and status."""
    schedules = MaintenanceSchedule.objects.select_related('vehicle').order_by('vehicle', 'service_code')

    overdue_count = sum(1 for s in schedules if s.is_due)

    paginator = Paginator(schedules, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'overdue_count': overdue_count,
        'total_count': schedules.count(),
    }
    return render(request, 'fleet/maintenance_list.html', context)
