from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render

from fleet.models import InspectionReport


@login_required
def inspection_list_view(request):
    """DVIR pre-trip and post-trip safety checklists with pass/fail tracking."""
    inspections = InspectionReport.objects.select_related('vehicle', 'inspector').order_by('-inspected_at')

    paginator = Paginator(inspections, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'fleet/inspection_list.html', context)
