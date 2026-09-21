from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from fleet.models import Notification, StatusChangeRequest, Vehicle
from fleet.services.agent_tools import create_quick_trip, evaluate_and_approve_request


@login_required
def status_request_create_view(request):
    """Handles submission of a status change request by normal users."""
    if request.method == 'POST':
        vehicle_id = request.POST.get('vehicle_id')
        license_plate = request.POST.get('license_plate', '').strip()
        requested_status = request.POST.get('requested_status')
        priority = request.POST.get('priority', StatusChangeRequest.Priority.MEDIUM)
        reason = request.POST.get('reason', '').strip()

        if vehicle_id:
            vehicle = get_object_or_404(Vehicle, pk=vehicle_id)
        elif license_plate:
            vehicle = get_object_or_404(Vehicle, license_plate__iexact=license_plate)
        else:
            messages.error(request, "Veuillez désigner un véhicule.")
            return redirect(request.POST.get('next') or reverse('fleet:dashboard'))

        req = StatusChangeRequest.objects.create(
            vehicle=vehicle,
            requested_by=request.user,
            requested_status=requested_status,
            priority=priority,
            reason=reason
        )

        # Autonomous AI Agent Evaluation (Offline Admin mode)
        decision = evaluate_and_approve_request(req.id)
        if decision.get('approved'):
            messages.success(
                request,
                f"✅ Demande approuvée par l'Agent IA FleetPulse : {vehicle.license_plate} a été basculé en MAINTENANCE pour sécurité !"
            )
        else:
            messages.info(
                request,
                f"Demande #{req.id} enregistrée. Transmise pour examen aux administrateurs."
            )

    return redirect(request.POST.get('next') or reverse('fleet:dashboard'))


@login_required
def quick_trip_create_view(request):
    """Direct web action allowing operators to log a trip without admin access."""
    if request.method == 'POST':
        plate = request.POST.get('license_plate')
        dist = int(request.POST.get('distance_km', 50))
        purpose = request.POST.get('purpose', 'Commercial transit run')

        res = create_quick_trip(plate, dist, request.user.username, purpose)
        if res.get('success'):
            messages.success(request, f"Trajet #{res['trip_id']} enregistré pour {plate} ({dist} km).")
        else:
            messages.error(request, res.get('error', 'Erreur lors de la création du trajet.'))

    return redirect(request.POST.get('next') or reverse('fleet:trip_list'))


@login_required
def mark_notification_read_view(request, pk):
    """Marks an in-app notification as read."""
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.is_read = True
    notif.save(update_fields=['is_read'])
    return redirect(request.GET.get('next') or reverse('fleet:dashboard'))
