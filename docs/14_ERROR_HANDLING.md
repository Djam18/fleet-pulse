# 14. Error Handling & Resilience Architecture — FleetPulse

## 1. Defensive Database Constraints
Integrity errors are prevented and intercepted at both application and database layers:
- **`IntegrityError` Prevention**: Unique constraints (`vin`, `license_plate`, `(vehicle, service_code)`) provide descriptive error messages (`violation_error_message`).
- **`CheckConstraint` Violations**: In the event of a negative or corrupted trip interval, the database engine enforces `check_trip_end_gte_start` before saving.

## 2. Form & Authentication Resilience
- **Invalid Credentials**:
  - The login view displays clear user-facing alerts without revealing whether the username or password was incorrect, guarding against user enumeration attacks.
- **Expired Password Reset Tokens**:
  - `PasswordResetConfirmView` validates token age and validity. If expired or already consumed, the template displays an explicit warning message with a direct link to request a fresh token.
- **Mail Server Resilience**:
  - If the Mailpit container is temporarily unreachable during password reset, Django catches socket connection timeouts gracefully and prevents server process termination.

## 3. Real-Time Streaming (SSE) Fault Tolerance
- **Automatic Reconnection**:
  - Front-end Alpine.js `EventSource` handles connection interruptions natively. On disconnect, the browser attempts an exponential backoff reconnect.
- **Top Header Status Indicator**:
  - When connection is active, the status dot pulses green with the text *"Live"*.
  - On connection drop, `evtSource.onerror` catches the event, sets `connected = false`, and changes the status badge to warning orange (*"Reconnecting"*).

## 4. HTTP 404 & Empty State Handling
- `get_object_or_404` protects single-asset views (`vehicle_detail_view`).
- All data tables (`vehicle_list.html`, `trip_list.html`, `maintenance_list.html`, `inspection_list.html`) contain clean `{% empty %}` fallback blocks informing operators when search queries or filters yield zero records.
