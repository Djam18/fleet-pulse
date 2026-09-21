# 08. API & Interface Specifications — FleetPulse

## 1. Real-Time Telematics Streaming API (SSE)

### `GET /telematics/stream/`
Streams Server-Sent Events (SSE) emitting simulated or live vehicle telematics updates.

- **Authentication**: Session Required (`@login_required`)
- **Query Parameters**:
  - `limit` (integer, optional, default: `20`, max: `60`): Number of events before stream completion.
- **Headers**:
  ```http
  Content-Type: text/event-stream
  Cache-Control: no-cache, no-transform
  X-Accel-Buffering: no
  ```
- **Event Payload Schema**:
  ```http
  event: telematics
  data: {
    "timestamp": "17:20:15 UTC",
    "license_plate": "FP-1002",
    "speed_kmh": 84,
    "fuel_battery_pct": 72,
    "gps_latitude": 37.7812,
    "gps_longitude": -122.4111,
    "engine_temp_c": 91,
    "status": "HEALTHY",
    "seq": 1
  }
  ```

## 2. Web Endpoints Directory

| Route | View Method | Description | Auth Level |
| :--- | :--- | :--- | :--- |
| `/` | `dashboard_view` | Command Center with ApexCharts and fleet KPIs | Operator |
| `/vehicles/` | `vehicle_list_view` | 10-item paginated directory with status/fuel filter | Operator |
| `/vehicles/<id>/`| `vehicle_detail_view` | Deep profile with maintenance and trip log history | Operator |
| `/trips/` | `trip_list_view` | 10-item paginated trip logbook and fuel totals | Operator |
| `/maintenance/` | `maintenance_list_view` | Preventative maintenance schedules and overdue count| Operator |
| `/inspections/` | `inspection_list_view` | DVIR safety checklist compliance records | Operator |
| `/login/` | `FleetLoginView` | Non-admin login supporting username or email | Public |
| `/logout/` | `FleetLogoutView` | Destroys session and redirects to `/login/` | Operator |
| `/register/` | `FleetRegisterView` | Operator onboarding registration form | Public |
| `/password-reset/`| `FleetPasswordResetView` | Triggers token email dispatch to Mailpit | Public |
| `/reset/<u64>/<t>/`| `FleetPasswordResetConfirm`| Sets new password using cryptographic token | Public |
| `/i18n/setlanguage/`| Django i18n View | Switches session language (`en`, `fr`, `es`) | Public |
| `/admin/` | `admin.site.urls` | Staff Administration Console | Staff Only |
