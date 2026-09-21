# FleetPulse — Smart Vehicle & Logistics Tracker

FleetPulse is a vehicle fleet operations and maintenance tracking system designed to showcase modern backend architecture, progressive framework migrations, and full-stack integration (Django + Angular).

The project is intentionally structured to begin on **Django 4.2 LTS** and progressively upgrade through **Django 5.0**, **Django 5.1**, and **Django 5.2 LTS**, systematically resolving deprecations, modernizing ORM structures, and adopting new capabilities at each milestone.

---

## 🚀 Key Features

* **Fleet Inventory & Status Management**: Track vehicle profiles, VINs, license plates, fuel types, and operational states (Active, In Service, Retired).
* **Trip & Fuel Logging**: Record start/end odometer readings, fuel purchases, and route data.
* **Driver Safety & Inspection Reports**: Driver pre-trip checklist with receipt/photo uploads.
* **Scheduled Maintenance & Work Orders**: Service schedules and maintenance tickets.
* **Dual Interface**:
  * Traditional server-rendered Django administrative portal (with customized widgets & facet filters).
  * Decoupled **Angular SPA** client interacting with Django REST APIs for driver and dispatcher workflows.

---

## 🏗️ Technology Stack

* **Backend**: Python (3.10+), Django (starting at 4.2 LTS $\rightarrow$ upgrading to 5.2 LTS), Django REST Framework (DRF)
* **Frontend**: Angular (Standalone Components, RxJS, Angular Signals)
* **Database**: SQLite (local development) / PostgreSQL (production target)
* **Code Modernization Tooling**: `django-upgrade`, `pytest-django`, `ruff`

---

## 📁 Repository Structure

```text
.
├── README.md                  # Project overview & quickstart
├── docs/
│   ├── ARCHITECTURE.md        # System design, data models & API specs
│   └── UPGRADE_ROADMAP.md     # Step-by-step 4.2 -> 5.x migration guide
├── backend/                   # Django backend (to be initialized)
│   ├── manage.py
│   ├── config/                # Project settings & WSGI/ASGI entrypoints
│   ├── apps/
│   │   ├── vehicles/          # Vehicle registry & status tracking
│   │   ├── trips/             # Trip logs, mileage, and fuel metrics
│   │   └── maintenance/       # Work orders and inspection uploads
│   └── requirements/
│       ├── base.txt           # Core dependencies
│       └── local.txt          # Development & test tools
└── frontend/                  # Angular SPA (optional decoupled frontend)
```

---

## 🔄 Progressive Upgrade Strategy

Rather than jumping directly to the latest version, FleetPulse follows the official Django progressive release methodology:

1. **Django 4.2 LTS (Baseline)**: Established baseline with legacy storage settings, manual form rendering, and Python-computed defaults.
2. **Django 5.0**: Introduce `Field.db_default`, `GeneratedField` for computed odometer and fuel metrics, and `as_field_group` form rendering.
3. **Django 5.1**: Migrate legacy `DEFAULT_FILE_STORAGE` to the modern `STORAGES` dictionary, adopt `LoginRequiredMiddleware`, and use `{% querystring %}` for catalog pagination.
4. **Django 5.2 LTS**: Incorporate composite primary keys for maintenance schedules and finalize long-term production readiness.

See [`docs/UPGRADE_ROADMAP.md`](docs/UPGRADE_ROADMAP.md) for full commands, deprecation flags, and checklist.

---

## 📖 Documentation Index

* [System Architecture & Data Models](docs/ARCHITECTURE.md)
* [Progressive Upgrade Roadmap & Deprecations](docs/UPGRADE_ROADMAP.md)
