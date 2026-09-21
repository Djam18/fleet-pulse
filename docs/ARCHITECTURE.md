# FleetPulse — System Architecture & Implementation Design

This document details the software architecture, domain models, REST API design, and frontend integration strategy for FleetPulse.

---

## 1. Domain Architecture & Core Data Models

The system is organized into three bounded contexts: **Vehicles**, **Trips**, and **Maintenance**.

```mermaid
erDiagram
    VEHICLE ||--o{ TRIP_LOG : "records"
    VEHICLE ||--o{ MAINTENANCE_SCHEDULE : "has"
    VEHICLE ||--o{ INSPECTION_REPORT : "undergoes"
    USER ||--o{ TRIP_LOG : "drives"
    USER ||--o{ INSPECTION_REPORT : "conducts"

    VEHICLE {
        int id PK
        string vin UK
        string license_plate UK
        string make
        string model
        int year
        string status
        int current_odometer
    }

    TRIP_LOG {
        int id PK
        int vehicle_id FK
        int driver_id FK
        datetime start_time
        datetime end_time
        int start_odometer
        int end_odometer
        decimal fuel_liters
        decimal fuel_cost
        int distance_calculated "Python save() in 4.2 -> GeneratedField in 5.0"
    }

    MAINTENANCE_SCHEDULE {
        int id PK "Becomes CompositePrimaryKey (vehicle_id, service_code) in 5.2"
        int vehicle_id FK
        string service_code
        string description
        int interval_km
        int last_service_odometer
    }

    INSPECTION_REPORT {
        int id PK
        int vehicle_id FK
        int inspector_id FK
        datetime inspected_at
        boolean passed
        text notes
        file document "Uses DEFAULT_FILE_STORAGE in 4.2 -> STORAGES in 5.1"
    }
```

---

## 2. API & Frontend Integration (Django + Angular)

FleetPulse supports both traditional server-rendered templates and a decoupled Angular Single-Page Application (SPA):

### A. Django REST Framework API Layer
- `/api/v1/vehicles/`: CRUD operations for vehicle records with facet filtering (by status, make, mileage).
- `/api/v1/trips/`: Trip submission, odometer validation, and mileage aggregation endpoints.
- `/api/v1/maintenance/`: Scheduled work orders and inspection document uploads.
- `/api/v1/auth/`: Token-based or session-based authentication for drivers and fleet managers.

### B. Angular Frontend Application
- **Role**: Client application tailored for mobile drivers (trip start/stop, pre-trip vehicle checklist, photo upload) and fleet managers (interactive real-time dashboards).
- **Communication**: Angular `HttpClient` communicates with Django's REST endpoints over JSON.
- **CORS & CSRF**: Django `django-cors-headers` middleware configured with `django.middleware.csrf.CsrfViewMiddleware` to safeguard API requests.

---

## 3. Database Strategy
- **Development**: Local SQLite engine (`django.db.backends.sqlite3`) for fast iteration.
- **Production**: PostgreSQL (`django.db.backends.postgresql`), which fully supports Django 5.x database features (`Field.db_default`, `GeneratedField`, and connection pooling in 5.1).
