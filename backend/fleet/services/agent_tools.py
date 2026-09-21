from django.contrib.auth import get_user_model
from django.utils import timezone
from fleet.models import Notification, StatusChangeRequest, TripLog, Vehicle

User = get_user_model()


def evaluate_and_approve_request(request_id: int) -> dict:
    """
    Autonomous decision function: AI agent evaluates a pending status change request.
    If safety-critical (brakes, tires, engine, urgent), auto-approves to MAINTENANCE.
    """
    try:
        req = StatusChangeRequest.objects.select_related('vehicle', 'requested_by').get(id=request_id)
    except StatusChangeRequest.DoesNotExist:
        return {'success': False, 'message': f"Request #{request_id} not found."}

    if req.status != StatusChangeRequest.RequestStatus.PENDING:
        return {'success': False, 'message': f"Request #{request_id} is already resolved ({req.get_status_display()})."}

    # Evaluate safety criteria
    safety_triggers = ['brake', 'frein', 'tire', 'pneu', 'leak', 'fuite', 'moteur', 'engine', 'defect', 'warning', 'urgent']
    reason_lower = req.reason.lower()
    is_safety_urgent = (
        req.priority in [StatusChangeRequest.Priority.CRITICAL, StatusChangeRequest.Priority.HIGH]
        or any(trigger in reason_lower for trigger in safety_triggers)
    )

    if req.requested_status == Vehicle.Status.MAINTENANCE and is_safety_urgent:
        # Autonomous safety approval
        req.vehicle.status = Vehicle.Status.MAINTENANCE
        req.vehicle.save(update_fields=['status'])
        req.status = StatusChangeRequest.RequestStatus.AI_APPROVED
        req.decided_at = timezone.now()
        req.decision_notes = "Auto-approved autonomously by FleetPulse AI Safety Agent (Policy: High-Severity Safety Defect)."
        req.save(update_fields=['status', 'decided_at', 'decision_notes'])

        Notification.objects.create(
            recipient=req.requested_by,
            title=f"AI Agent Approved: {req.vehicle.license_plate}",
            message=f"Vehicle {req.vehicle.license_plate} was autonomously shifted to MAINTENANCE for safety precaution."
        )
        return {
            'success': True,
            'approved': True,
            'vehicle': req.vehicle.license_plate,
            'new_status': 'MAINTENANCE',
            'rationale': req.decision_notes
        }

    # Escalate to human manager if non-critical
    req.decision_notes = "Evaluated by AI Agent: Routine request flagged for human administrator review."
    req.save(update_fields=['decision_notes'])
    return {
        'success': True,
        'approved': False,
        'vehicle': req.vehicle.license_plate,
        'rationale': req.decision_notes
    }


def query_vehicle_telematics(plate: str) -> dict:
    """Returns detailed specifications, odometer, and service status for an asset."""
    v = Vehicle.objects.filter(license_plate__iexact=plate.strip()).first()
    if not v:
        return {'error': f"Vehicle with plate '{plate}' was not found in registry."}
    schedules = v.maintenance_schedules.all()
    overdue = [s.get_service_code_display() for s in schedules if s.is_due]
    return {
        'plate': v.license_plate,
        'make_model': f"{v.make} {v.model} ({v.year})",
        'vin': v.vin,
        'status': v.get_status_display(),
        'fuel_type': v.get_fuel_type_display(),
        'odometer_km': v.current_odometer,
        'overdue_services': overdue,
    }


def check_fleet_readiness() -> dict:
    """Calculates operational readiness ratio and status distribution across the fleet."""
    total = Vehicle.objects.count()
    active = Vehicle.objects.filter(status=Vehicle.Status.ACTIVE).count()
    maintenance = Vehicle.objects.filter(status=Vehicle.Status.MAINTENANCE).count()
    ratio = round((active / total * 100), 1) if total else 0.0
    return {
        'total_vehicles': total,
        'active_units': active,
        'in_maintenance': maintenance,
        'readiness_pct': f"{ratio}%",
    }


def create_quick_trip(plate: str, distance_km: int, driver_username: str, purpose: str = "Dispatched transit run") -> dict:
    """Logs a completed trip for a vehicle and advances its odometer."""
    v = Vehicle.objects.filter(license_plate__iexact=plate.strip()).first()
    if not v:
        return {'error': f"Vehicle with plate '{plate}' was not found."}

    driver = User.objects.filter(username__iexact=driver_username.strip()).first()
    start_odo = v.current_odometer
    end_odo = start_odo + int(distance_km)
    fuel_l = round(distance_km * 0.12, 2)
    fuel_c = round(fuel_l * 1.80, 2)

    trip = TripLog.objects.create(
        vehicle=v,
        driver=driver,
        start_time=timezone.now() - timezone.timedelta(hours=2),
        end_time=timezone.now(),
        start_odometer=start_odo,
        end_odometer=end_odo,
        distance_km=int(distance_km),
        fuel_liters=fuel_l,
        fuel_cost=fuel_c,
        purpose=purpose
    )
    v.current_odometer = end_odo
    v.save(update_fields=['current_odometer'])

    return {
        'success': True,
        'trip_id': trip.id,
        'vehicle': v.license_plate,
        'new_odometer': end_odo,
        'distance_logged': distance_km
    }
