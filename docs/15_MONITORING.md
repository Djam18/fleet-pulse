# 15. Monitoring, Observability & Telematics — FleetPulse

## 1. Database Connection Health Checks
FleetPulse configures connection recycling and health checking in `backend/config/settings.py`:
- `conn_max_age=600`: Persists persistent database connections for up to 10 minutes.
- `CONN_HEALTH_CHECKS = True`: Evaluates whether a database connection is alive before dispatching queries, crucial for long-lived Server-Sent Events (SSE) streaming sessions.

## 2. Real-Time Telematics Telemetry Logs
- The `/telematics/stream/` endpoint tracks:
  - Sequence IDs (`seq: 1..N`)
  - Timestamp of broadcast (`H:M:S UTC`)
  - Speed, fuel/battery level, and engine temperature
  - Anomaly status flags (`HEALTHY`, `WARNING_TIRE_PRESSURE`)
- Client-side heartbeats are visualized in `top_header.html` with latency ticks.

## 3. Administrative Audit Trails & Logging
- **Immutable Historical Logs**:
  - `TripLogAdmin` marks `start_time`, `end_time`, `start_odometer`, `end_odometer`, and `distance_km` as `readonly_fields` once created, preserving legal audit trail integrity.
- **Admin History**:
  - All modifications, status overrides, and maintenance closures are tracked via Django's built-in `LogEntry` audit system.

## 4. Mailpit Inbound & Outbound Observability
- All transactional emails (user registrations, password resets, preventative maintenance warnings) are dispatched to the local Mailpit daemon (`127.0.0.1:1025`).
- Mail delivery rates, message sizes, raw MIME payloads, and HTML renders are observable via Mailpit's REST API:
  ```bash
  curl -s http://localhost:8025/api/v1/messages
  ```
- Unread counts and message latency can be monitored programmatically.
