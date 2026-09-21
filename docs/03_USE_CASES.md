# 03. Use Cases Specification — FleetPulse

## UC-01: Dispatcher Signs In with Email
- **Primary Actor**: Dispatcher / Operations Operator
- **Preconditions**: User account exists in database.
- **Trigger**: Operator navigates to `/login/`.
- **Main Success Scenario**:
  1. Operator enters registered email address (`operator@fleetpulse.local`) and password.
  2. `EmailOrUsernameModelBackend` queries user by email case-insensitively.
  3. System validates credentials and sets secure session cookie.
  4. System redirects operator to Fleet Command Center (`/`).
- **Extensions**: Invalid credentials display alert: *"Invalid credentials. Please verify your username/email and password."*

## UC-02: Password Recovery via Mailpit
- **Primary Actor**: Operator
- **Preconditions**: Account exists; Mailpit container is running on `127.0.0.1:1025`.
- **Main Success Scenario**:
  1. Operator submits email on `/password-reset/`.
  2. Django generates cryptographic token and sends reset link via SMTP to Mailpit.
  3. Operator opens Mailpit inbox (`http://localhost:8025`) and clicks reset link.
  4. Operator specifies new password on `/reset/<uidb64>/<token>/`.
  5. Password updates successfully; operator logs in with new credentials.

## UC-03: Filtering Fleet by Status and Fuel Powertrain
- **Primary Actor**: Fleet Dispatcher
- **Preconditions**: Operator is authenticated.
- **Main Success Scenario**:
  1. Dispatcher navigates to `/vehicles/`.
  2. Dispatcher selects Status: `ACTIVE` and Fuel Type: `ELECTRIC`.
  3. System evaluates filtered QuerySet with `select_related`/`prefetch_related`.
  4. Interface renders 10 records per page; pagination preserves query filters (`?status=ACTIVE&fuel=ELECTRIC&page=2`).

## UC-04: Subscribing to Live Fleet Telematics (SSE)
- **Primary Actor**: Dispatcher Dashboard Client (Browser)
- **Preconditions**: User session is active.
- **Main Success Scenario**:
  1. Front-end Alpine.js opens `new EventSource('/telematics/stream/')`.
  2. Backend generator emits `event: telematics` payloads containing speed, fuel/battery, and location every 1.5 seconds.
  3. Alpine.js catches event and updates top navbar badge and hero ticker live without page reload.

## UC-05: Reviewing Safety Inspection Audit (DVIR)
- **Primary Actor**: Safety Compliance Officer
- **Main Success Scenario**:
  1. Officer navigates to `/inspections/`.
  2. System lists inspections ordered by latest timestamp with pass/fail badges.
  3. Officer inspects brakes, tires, and fluids checklist audits for flagged defects.
