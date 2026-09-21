# 13. Domain & Technical Glossary — FleetPulse

## 1. Fleet & Logistics Terminology
- **Asset**: A motorized commercial vehicle (truck, van, electric cargo hauler) tracked in the fleet registry.
- **VIN (Vehicle Identification Number)**: Standardized 17-character unique identifier for motorized road vehicles.
- **Odometer**: Instrument measuring the cumulative distance traveled by an asset in kilometers (km).
- **DVIR (Driver Vehicle Inspection Report)**: Federally mandated pre-trip and post-trip safety audit recording the condition of vehicle systems (brakes, tires, lights, fluids).
- **Preventative Maintenance (PM)**: Scheduled servicing routines triggered by cumulative distance or elapsed calendar intervals to prevent mechanical breakdown.
- **Powertrain**: Mechanism transmitting drive from engine/motor to road (Diesel, Gasoline, Electric, Hybrid).

## 2. Technical & Architecture Terminology
- **Django 4.2 LTS**: Long-Term Support release of Django supported through April 2026, offering extended stability.
- **STORAGES**: Modern storage dictionary introduced in Django 4.2 replacing deprecated `DEFAULT_FILE_STORAGE`.
- **Server-Sent Events (SSE)**: Unidirectional streaming protocol over standard HTTP allowing servers to push real-time events to browsers.
- **Mailpit**: Open-source local email testing server offering an SMTP listener and a webmail inspection UI.
- **GNU gettext**: Internationalization framework utilizing `.po` (Portable Object) translation files and compiled `.mo` (Machine Object) binary catalogs.
- **Elided Pagination**: Pagination strategy rendering a fixed window of page numbers with ellipses (`1 ... 4 5 [6] 7 8 ... 301`) to maintain clean UI layout.
- **Dual Authentication**: Authentication mechanism enabling users to log in using either a registered username or a valid email address.
- **N+1 Query Problem**: Performance anti-pattern where an application executes one query to fetch parent records and $N$ additional queries to fetch children.
