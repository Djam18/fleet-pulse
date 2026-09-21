import json
import random
import time
from datetime import datetime, timezone

from django.contrib.auth.decorators import login_required
from django.http import StreamingHttpResponse

from fleet.models import Vehicle


def generate_telematics_events(max_events=30):
    """
    Yields real-time Server-Sent Events (SSE) carrying simulated fleet telemetry.
    Supports a max_events limit to prevent worker thread starvation.
    """
    vehicles = list(Vehicle.objects.filter(status=Vehicle.Status.ACTIVE)[:5])
    plates = [v.license_plate for v in vehicles] or ['FP-1001', 'FP-1002', 'FP-1003']
    iteration = 0

    while iteration < max_events:
        iteration += 1
        target_plate = random.choice(plates)
        payload = {
            'timestamp': datetime.now(timezone.utc).strftime('%H:%M:%S UTC'),
            'license_plate': target_plate,
            'speed_kmh': random.randint(45, 110),
            'fuel_battery_pct': random.randint(18, 98),
            'gps_latitude': round(37.7749 + random.uniform(-0.05, 0.05), 5),
            'gps_longitude': round(-122.4194 + random.uniform(-0.05, 0.05), 5),
            'engine_temp_c': random.randint(82, 98),
            'status': 'HEALTHY' if random.random() > 0.08 else 'WARNING_TIRE_PRESSURE',
            'seq': iteration,
        }
        yield f"event: telematics\ndata: {json.dumps(payload)}\n\n"
        time.sleep(1.5)


@login_required
def telematics_stream_view(request):
    """
    Django 4.2 Streaming Server-Sent Events (SSE) endpoint for live fleet telematics.
    """
    limit_param = request.GET.get('limit')
    try:
        max_events = min(int(limit_param), 60) if limit_param else 20
    except (ValueError, TypeError):
        max_events = 20

    response = StreamingHttpResponse(
        generate_telematics_events(max_events=max_events),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache, no-transform'
    response['X-Accel-Buffering'] = 'no'
    return response
