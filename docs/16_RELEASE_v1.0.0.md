# FleetPulse Release v1.0.0 — Official Release Notes

**Release Date**: September 21, 2026  
**Target Runtime**: Python 3.12 & Django 4.2.30 LTS  
**Git Tag**: `v1.0.0`  

---

## 1. Executive Summary

FleetPulse `v1.0.0` delivers a dual-tier commercial fleet operations and telematics platform with role-differentiated workspaces (Executive Fleet Command Center vs. Dedicated Driver Space), 20 seeded enterprise personas, feature-flagged autonomous services, and strict adherence to enterprise code constraints.

---

## 2. Key Deliverables & Features

### A. Role-Differentiated User Experience
- **Executive Fleet Command Center (`is_staff = True`)**:
  - Real-time fleet metrics: 20 commercial vehicles, 15 active units, fleet health status.
  - Interactive ApexCharts: odometer telemetry distribution and availability breakdown.
  - Full vehicle registry with pagination and direct admin console navigation.
- **Espace Chauffeur (`is_staff = False`)**:
  - Personalized driver header with assigned vehicle telematics.
  - 4 Driver KPIs: Véhicule Opéré, Mes Trajets, Distance Parcourue, Mes Demandes.
  - Personal recent trips history and ticket approval workflow tracking.
  - Staff admin navigation links automatically guarded and hidden.

### B. Enterprise Seeding (20 Personas)
- Default presentation password: `fleetpulse2026!`
- **5 Super Admins**: `admin`, `superadmin_clara`, `superadmin_marc`, `superadmin_hugo`, `superadmin_sophie`.
- **5 Staff Admins**: `manager_lucas`, `manager_emma`, `manager_karim`, `manager_julie`, `manager_thomas`.
- **10 Field Drivers**: `alex_m`, `sarah_c`, `marcus_w`, `elena_r`, `nicolas_p`, `camille_d`, `youssef_b`, `antoine_m`, `lea_f`, `david_k`.
- **3,000+ historical trips** and **350+ safety inspections** spanning 2023–2026.

### C. Feature Toggling & Architecture
- **Environment Toggle**: `ENABLE_AI_COPILOT=False` default in `.env` and `.env.example`.
- All AI chat drawers, floating launchers, and navbar buttons are decoupled and hidden when inactive.
- Fast operational modals: Quick Trip Logging (`#quickTripModal`) and Status Reporting (`#statusRequestModal`).

---

## 3. Git Branch Topology

| Branch Name | Role & Target Purpose |
| :--- | :--- |
| `main` | Production-ready stable release baseline. |
| `develop` | Ongoing integration branch for feature development. |
| `django-4.2-lts` | Production LTS maintenance branch (Current). |
| `django-5.0` | Step 1 migration branch (`GeneratedField`, `db_default`). |
| `django-5.1` | Step 2 feature branch (middleware & authentication updates). |
| `django-5.2-lts` | Next Long-Term Support target release branch. |

---

## 4. Verification & Quality Assurance

- **Unit Test Suite**: 49/49 automated unit tests passing (`OK`).
- **File Size Constraint**: Every source file verified strictly $\le 150$ lines.
- **Internationalization**: Full dual-language catalog support (French & English).
