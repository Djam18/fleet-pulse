import random
from datetime import datetime, timedelta, timezone

from fleet.models import InspectionReport, TripLog


def generate_fleet_trips(vehicles, drivers, target_count=3000):
    """
    Generates target_count trips chronologically from Jan 2023 to Sep 2026.
    Ensures valid odometer progressions and realistic fuel metrics.
    """
    start_date = datetime(2023, 1, 15, 8, 0, tzinfo=timezone.utc)
    end_date = datetime(2026, 9, 20, 18, 0, tzinfo=timezone.utc)
    total_seconds = int((end_date - start_date).total_seconds())

    trips_to_create = []
    # Track current odometer per vehicle in-memory during generation
    vehicle_odometers = {v.id: v.current_odometer for v in vehicles}

    purposes = [
        'Regional logistics delivery',
        'Metro distribution run',
        'Interstate warehouse transfer',
        'Direct store replenishment',
        'Urgent parts delivery',
        'Scheduled cargo transit'
    ]

    for i in range(target_count):
        v = random.choice(vehicles)
        curr_odo = vehicle_odometers[v.id]
        dist = random.randint(45, 420)
        end_odo = curr_odo + dist
        vehicle_odometers[v.id] = end_odo

        # Random timestamp along the timeline
        trip_start = start_date + timedelta(seconds=random.randint(0, total_seconds - 36000))
        trip_duration_hours = max(1, dist // random.randint(50, 75))
        trip_end = trip_start + timedelta(hours=trip_duration_hours)

        # Fuel calculation based on fuel type
        if v.fuel_type == 'ELECTRIC':
            fuel_l, fuel_c = 0.0, round(dist * 0.08, 2)
        else:
            fuel_l = round(dist * random.uniform(0.11, 0.16), 2)
            fuel_c = round(fuel_l * random.uniform(1.65, 1.95), 2)

        trips_to_create.append(TripLog(
            vehicle=v,
            driver=random.choice(drivers) if drivers else None,
            start_time=trip_start,
            end_time=trip_end,
            start_odometer=curr_odo,
            end_odometer=end_odo,
            distance_km=dist,
            fuel_liters=fuel_l,
            fuel_cost=fuel_c,
            purpose=random.choice(purposes)
        ))

    # Bulk create in batches of 1000 for high performance
    TripLog.objects.bulk_create(trips_to_create, batch_size=1000)

    # Sync vehicle final odometers
    for v in vehicles:
        v.current_odometer = vehicle_odometers[v.id]
        v.save(update_fields=['current_odometer'])


def generate_fleet_inspections(vehicles, inspectors, target_count=350):
    """Generates historical safety inspection reports."""
    reports = []
    start_date = datetime(2023, 2, 1, 7, 0, tzinfo=timezone.utc)
    for _ in range(target_count):
        v = random.choice(vehicles)
        insp_time = start_date + timedelta(days=random.randint(1, 1300))
        passed = random.random() > 0.15
        reports.append(InspectionReport(
            vehicle=v,
            inspector=random.choice(inspectors),
            inspected_at=insp_time,
            odometer_reading=max(0, v.current_odometer - random.randint(500, 25000)),
            brakes_passed=passed or random.random() > 0.5,
            tires_passed=passed or random.random() > 0.4,
            lights_passed=True,
            fluids_passed=True,
            overall_passed=passed,
            notes='All systems verified' if passed else 'Minor defect logged for workshop review'
        ))
    InspectionReport.objects.bulk_create(reports, batch_size=500)
