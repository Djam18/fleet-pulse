# 07. Data Model & Entity Specifications — FleetPulse

## 1. Entity-Relationship Model (ERD)

```
┌──────────────────┐               ┌──────────────────┐
│     Vehicle      │1            * │     TripLog      │
├──────────────────┼───────────────┼──────────────────┤
│ id (PK)          │               │ id (PK)          │
│ vin (Unique)     │               │ vehicle_id (FK)  │
│ license_plate(UQ)│               │ driver_id (FK)   │
│ make, model, year│               │ start_time       │
│ status, fuel_type│               │ end_time         │
│ current_odometer │               │ distance_km      │
└────────┬─────────┘               │ fuel_cost, liters│
         │                         └──────────────────┘
         │1
         │
         ├─────────────────────────┐
         │*                        │*
┌────────┴──────────────┐  ┌───────┴──────────────┐
│  MaintenanceSchedule  │  │   InspectionReport   │
├───────────────────────┤  ├──────────────────────┤
│ id (PK)               │  │ id (PK)              │
│ vehicle_id (FK)       │  │ vehicle_id (FK)      │
│ service_code          │  │ inspector_id (FK)    │
│ interval_km           │  │ inspected_at         │
│ last_service_odometer │  │ odometer_reading     │
│ last_service_date     │  │ brakes_passed (bool) │
└───────────────────────┘  │ tires_passed (bool)  │
                           │ overall_passed (bool)│
                           └──────────────────────┘
```

## 2. Model Detail Specifications

### Vehicle (`fleet.models.Vehicle`)
- **Indexes**: `idx_vehicle_status_fuel` on `(status, fuel_type)`.
- **QuerySet Helpers**: `.active()`, `.in_maintenance()`, `.retired()`.
- **Choices**:
  - `Status`: `ACTIVE` (*Active & Operational*), `MAINTENANCE` (*In Maintenance*), `RETIRED` (*Retired*).
  - `FuelType`: `DIESEL`, `PETROL`, `ELECTRIC`, `HYBRID`.

### TripLog (`fleet.models.TripLog`)
- **Indexes**: `idx_trip_veh_start` on `(vehicle, start_time)`.
- **Constraints**:
  - `check_trip_end_gte_start`: `CheckConstraint(check=Q(end_time__gte=F('start_time')))`

### MaintenanceSchedule (`fleet.models.MaintenanceSchedule`)
- **Constraints**:
  - `uniq_veh_service_code`: `UniqueConstraint(fields=['vehicle', 'service_code'])`
- **Computed Properties**: `is_due`, `km_until_due`, `days_until_due`.

### InspectionReport (`fleet.models.InspectionReport`)
- **Fields**: `brakes_passed`, `tires_passed`, `lights_passed`, `fluids_passed`, `overall_passed`, `odometer_reading`.
- **Audit Association**: Foreign key to `auth.User` as `inspector`.
