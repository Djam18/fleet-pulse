# 04. Business Rules — FleetPulse

## BR-01: Vehicle Identification & Integrity
- **Rule 1.1**: Every vehicle must have a valid 17-character Vehicle Identification Number (VIN). Duplicate VINs are rejected at the database level (`unique=True`).
- **Rule 1.2**: Vehicle license plates must be unique within the registry.
- **Rule 1.3**: When an asset is marked `RETIRED`, it cannot be scheduled for new transit trips.

## BR-02: Trip Chronology & Odometer Continuity
- **Rule 2.1**: A trip's ending timestamp must always be greater than or equal to its starting timestamp. Enforced via database constraint `check_trip_end_gte_start`.
- **Rule 2.2**: The ending odometer of a completed trip must equal `start_odometer + distance_km`.
- **Rule 2.3**: Completing a trip updates the associated vehicle's `current_odometer` monotonically.

## BR-03: Preventative Maintenance Triggers
- **Rule 3.1**: An asset triggers an **Overdue Alert** if either of the following conditions is satisfied:
  $$\text{Current Odometer} \ge \text{Last Service Odometer} + \text{Interval Km}$$
  $$\text{Current Date} \ge \text{Last Service Date} + \text{Interval Days}$$
- **Rule 3.2**: A vehicle cannot have duplicate active maintenance schedules for the same `service_code`. Enforced via database constraint `uniq_veh_service_code`.
- **Rule 3.3**: Standard service codes include: `OIL_CHANGE` (15,000 km), `TIRE_ROTATION` (20,000 km), `BRAKE_SERVICE` (30,000 km), and `ANNUAL_INSPECTION` (365 days).

## BR-04: Safety Inspection Compliance (DVIR)
- **Rule 4.1**: An inspection receives an overall **PASSED** rating if and only if all audited sub-systems (`brakes_passed`, `tires_passed`, `lights_passed`, `fluids_passed`) are confirmed true.
- **Rule 4.2**: Any failed sub-system marks the overall inspection as **DEFECTS FOUND**, triggering an immediate workshop notification.

## BR-05: Access Control & Route Guarding
- **Rule 5.1**: All operational endpoints (`/`, `/vehicles/`, `/trips/`, `/maintenance/`, `/inspections/`, `/telematics/stream/`) require authenticated user sessions.
- **Rule 5.2**: Unauthenticated requests are immediately redirected to `/login/?next=<path>`.
- **Rule 5.3**: Staff members with `is_staff=True` can access the Django Admin console at `/admin/`.
