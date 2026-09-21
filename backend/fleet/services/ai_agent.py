import json
import re
import time
from fleet.models import StatusChangeRequest
from .agent_tools import (
    check_fleet_readiness,
    create_quick_trip,
    evaluate_and_approve_request,
    query_vehicle_telematics,
)


def _generate_agent_stream(prompt: str, user):
    """Core generator resolving tool invocations for the prompt."""
    p_lower = prompt.lower()

    # 1. Autonomous Approval of Pending Requests (Offline Admin Mode)
    if any(w in p_lower for w in ['approve', 'approuve', 'pending', 'demande', 'en attente', 'offline']):
        pending = list(StatusChangeRequest.objects.filter(status=StatusChangeRequest.RequestStatus.PENDING)[:3])
        if not pending:
            yield "data: " + json.dumps({'text': "🤖 **Agent IA FleetPulse** : Aucune demande de changement de statut n'est en attente pour le moment."}) + "\n\n"
            return

        yield "data: " + json.dumps({'text': f"🤖 **Agent IA FleetPulse (Mode Décision Autonome)** : Examen de {len(pending)} demande(s) en attente...\n\n"}) + "\n\n"
        time.sleep(0.3)

        for req in pending:
            res = evaluate_and_approve_request(req.id)
            if res.get('approved'):
                msg = f"- ✅ **Demande #{req.id} ({res['vehicle']}) : APPROUVÉE AUTONOMEMENT**\n  - *Nouveau statut* : `MAINTENANCE`\n  - *Motif* : {res['rationale']}\n"
            else:
                msg = f"- ⏳ **Demande #{req.id} ({res['vehicle']}) : EN ATTENTE ADMIN**\n  - *Raison* : {res['rationale']}\n"
            yield "data: " + json.dumps({'text': msg}) + "\n\n"
            time.sleep(0.3)
        return

    # 2. Vehicle Telematics Query
    plate_match = re.search(r'(fp-\d{4}|test-\d{3}|[a-z]{1,4}-\d{3,4})', p_lower)
    if plate_match or any(w in p_lower for w in ['vehicule', 'vehicle', 'camion', 'truck']):
        target_plate = plate_match.group(1).upper() if plate_match else 'FP-1001'
        info = query_vehicle_telematics(target_plate)
        if 'error' in info:
            yield "data: " + json.dumps({'text': f"🤖 {info['error']}"}) + "\n\n"
        else:
            resp = (
                f"🤖 **Télémétrie Véhicule `{info['plate']}`** :\n\n"
                f"- **Modèle** : {info['make_model']}\n"
                f"- **Statut** : `{info['status']}`\n"
                f"- **Compteur** : {info['odometer_km']} km\n"
                f"- **Énergie** : {info['fuel_type']}\n"
            )
            if info['overdue_services']:
                resp += f"- ⚠️ **Alertes entretien** : {', '.join(info['overdue_services'])}\n"
            else:
                resp += "- ✅ **Entretien** : Tous les systèmes sont nominaux.\n"
            yield "data: " + json.dumps({'text': resp}) + "\n\n"
        return

    # 3. Fleet Health & Readiness Ratio
    if any(w in p_lower for w in ['fleet', 'flotte', 'readiness', 'disponib', 'sante', 'health']):
        stats = check_fleet_readiness()
        resp = (
            f"🤖 **Rapport de Disponibilité Flotte** :\n\n"
            f"- **Taux de préparation** : **{stats['readiness_pct']}**\n"
            f"- **Unités actives en service** : {stats['active_units']} / {stats['total_vehicles']}\n"
            f"- **Unités en maintenance / atelier** : {stats['in_maintenance']}\n"
        )
        yield "data: " + json.dumps({'text': resp}) + "\n\n"
        return

    # 4. Quick Trip Logging
    if any(w in p_lower for w in ['log trip', 'enregistre trajet', 'nouveau trajet']):
        dist_match = re.search(r'(\d+)\s*(?:km)?', p_lower)
        dist = int(dist_match.group(1)) if dist_match else 75
        plate = plate_match.group(1).upper() if plate_match else 'FP-1001'
        res = create_quick_trip(plate, dist, user.username)
        if res.get('success'):
            resp = f"🤖 ✅ **Trajet enregistré avec succès !**\n\n- **Trajet ID** : #{res['trip_id']}\n- **Véhicule** : {res['vehicle']}\n- **Distance** : {res['distance_logged']} km\n- **Nouveau compteur** : {res['new_odometer']} km"
            yield "data: " + json.dumps({'text': resp}) + "\n\n"
            return

    # Default Advisory Response
    yield "data: " + json.dumps({'text': "🤖 **Copilote FleetPulse** : Je peux vous aider à :\n1. **Approuver les demandes** de statut en attente quand les administrateurs sont absents (*ex : 'Vérifie et approuve les demandes'*).\n2. **Consulter la télémétrie** d'un véhicule (*ex : 'Statut du camion FP-1002'*).\n3. **Analyser la préparation** globale de la flotte (*ex : 'Disponibilité de la flotte'*).\n4. **Enregistrer un trajet** directement en direct."}) + "\n\n"


def run_local_agent_stream(prompt: str, user):
    """
    Intelligent autonomous agent engine executing operational tools
    and streaming responses over Server-Sent Events (SSE).
    """
    try:
        yield from _generate_agent_stream(prompt, user)
    finally:
        yield "event: done\ndata: [DONE]\n\n"

