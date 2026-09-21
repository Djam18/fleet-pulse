# 02. Software Requirements Specification (SRS) — FleetPulse

## 1. System Overview
FleetPulse is built using **Python 3.12** and **Django 4.2 LTS** (`4.2.30`). It adheres strictly to modular separation of concerns, defensive database constraints, and modern responsive UI patterns.

## 2. Functional Requirements (FR)

### FR-01: Authentication & Authorization
- The system must support authentication using either **username** or **email address** via `EmailOrUsernameModelBackend`.
- Non-admin operational routes must require active session authentication (`@login_required`).
- Password reset workflows must dispatch tokenized confirmation links via an SMTP backend connected to Mailpit (`127.0.0.1:1025`).

### FR-02: Asset Management
- Every vehicle must possess a globally unique 17-character VIN and unique license plate.
- Vehicles must be categorized by status (`ACTIVE`, `MAINTENANCE`, `RETIRED`) and fuel type (`DIESEL`, `PETROL`, `ELECTRIC`, `HYBRID`).

### FR-03: Trip Logging & Constraints
- A trip log must record starting odometer, ending odometer, total distance, fuel cost, and assigned driver.
- The database must reject any trip log where `end_time < start_time` via a database-level `CheckConstraint`.

### FR-04: Preventative Maintenance
- Maintenance schedules must calculate overdue status dynamically: `is_due = (current_odometer >= last_service_odometer + interval_km) or (today >= last_service_date + interval_days)`.
- Vehicles must not have duplicate schedules for the same service code (`UniqueConstraint`).

### FR-05: Real-Time Telematics Streaming
- The system must expose `/telematics/stream/` streaming Server-Sent Events (`text/event-stream`) using `StreamingHttpResponse`.

## 3. Non-Functional Requirements (NFR)

### NFR-01: Usability & Responsiveness
- The application layout must be responsive across mobile ($< 768\text{px}$), tablet ($768\text{px} - 991\text{px}$), and desktop ($\ge 992\text{px}$) utilizing Bootstrap 5.3's `.offcanvas-lg` navigation.

### NFR-02: Internationalization (i18n)
- The system must provide 100% complete localization for English (`en`), French (`fr`), and Spanish (`es`) with zero missing `msgstr` entries.

### NFR-03: Code Architecture
- Hard limit: No source code, template, or documentation file may exceed 150 lines.
