# 06. Technical Architecture — FleetPulse

## 1. High-Level Architectural Stack
FleetPulse follows a clean 3-tier modular MVC/MVT architecture deployed on **Django 4.2 LTS** (`4.2.30`):

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                       │
│  - Bootstrap 5.3 (Responsive .offcanvas-lg Navigation)      │
│  - Alpine.js 3.14 (Reactive State & SSE Dispatch)           │
│  - ApexCharts 3.46 (Mileage & Fleet Health Visualizations)  │
│  - Componentized Templates (backend/templates/)             │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / SSE Stream
┌──────────────────────────────▼──────────────────────────────┐
│                    Application Layer                        │
│  - Modular Views: dashboard, vehicles, trips, maintenance   │
│  - Real-Time Streaming: telematics_stream_view (SSE)        │
│  - Dual-Auth Backend: EmailOrUsernameModelBackend           │
│  - Django i18n: LocaleMiddleware (en, fr, es catalogs)      │
│  - Custom Templatetags: url_replace, smart_page_range       │
└──────────────────────────────┬──────────────────────────────┘
                               │ Django 4.2 ORM
┌──────────────────────────────▼──────────────────────────────┐
│                     Persistence Layer                       │
│  - SQLite (Local Dev) / PostgreSQL (Production)             │
│  - Models: Vehicle, TripLog, MaintenanceSchedule, Inspection│
│  - Database Constraints & Compound Indexes                  │
│  - Mailpit SMTP Container (localhost:1025)                  │
└─────────────────────────────────────────────────────────────┘
```

## 2. Directory Structure & Modular Organization
```
django/
├── backend/
│   ├── config/              # Core project settings, WSGI, URLs
│   │   ├── settings.py      # STORAGES, Mailpit, Auth Backends
│   │   └── urls.py          # Root routing & i18n endpoints
│   ├── fleet/               # Core FleetPulse application domain
│   │   ├── admin/           # Modular ModelAdmin implementations
│   │   ├── models/          # Modular domain models (Vehicle, Trip, etc.)
│   │   ├── views/           # Modular Class/Function views
│   │   ├── templatetags/    # Pagination & query URL replacement tags
│   │   └── tests/           # 32 comprehensive tests (models, views, etc.)
│   ├── locale/              # Compiled .po & .mo catalogs (en, fr, es)
│   ├── static/css/          # Midnight/Cyan admin custom stylesheets
│   └── templates/           # Componentized UI partials & pages
├── docs/                    # 15 technical documentation files
└── .gitattributes           # Universal diff and linguist rules
```

## 3. Real-Time Telematics Streaming Engine
- **Protocol**: Server-Sent Events (SSE) via HTTP/1.1 or HTTP/2.
- **Backend**: Django 4.2 `StreamingHttpResponse` utilizing an asynchronous generator.
- **Client**: Native browser `EventSource` initialized by Alpine.js in `top_header.html`, broadcasting window-level custom events to reactive UI cards.
