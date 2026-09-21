# 09. Testing Strategy & Test Suite — FleetPulse

## 1. Test Architecture & Execution
FleetPulse incorporates automated tests across unit, integration, and security layers.
Tests are executed using Django's test runner with Python warning validation enabled:
```bash
python -Wd manage.py test fleet
```

## 2. Test Suite Matrix (32 Tests)

### Domain Models & Constraints (`test_models.py`)
- `test_vehicle_string_representation`: Plate, make, model formatting.
- `test_is_operational_property`: `is_operational` boolean validation.
- `test_custom_queryset_filters`: `.active()`, `.in_maintenance()`, `.retired()`.
- `test_vin_unique_constraint`: 17-character uniqueness check.
- `test_ordering_by_license_plate`: Default alphabetical ordering.
- `test_trip_log_string_representation`: Human-readable log string.
- `test_check_constraint_trip_end_gte_start`: DB `CheckConstraint` validation.
- `test_is_due_by_odometer`: Odometer-based maintenance trigger.
- `test_is_due_by_date`: Time-based maintenance expiration.
- `test_unique_constraint_vehicle_service_code`: Unique service code constraint.

### Admin Console & Performance (`test_admin.py`)
- `test_vehicle_admin_queryset_optimization`: Validates prefetching & annotations.
- `test_vehicle_admin_custom_actions`: Bulk state transitions.
- `test_trip_admin_readonly_fields`: Immutability of telematics fields.
- `test_maintenance_admin_due_badge`: Status pill rendering.
- `test_inspection_admin_badge_display`: Pass/fail badge display.

### Operations Views & Pagination (`test_views.py`)
- `test_unauthenticated_user_redirected_to_login`: Route protection.
- `test_dashboard_client_integration`: Context and chart payload assertions.
- `test_dashboard_request_factory_isolation`: Direct RequestFactory execution.
- `test_dashboard_with_locale_header`: i18n HTTP accept header test.
- `test_vehicle_list_view`, `test_vehicle_detail_view`: 10-item pagination & search.
- `test_trip_list_view`, `test_maintenance_list_view`, `test_inspection_list_view`: 10-item pagination & stats.

### Auth, Mailpit & Telematics (`test_auth.py`)
- `test_dual_auth_backend_with_username` / `test_dual_auth_backend_with_email`: Dual login.
- `test_dual_auth_backend_invalid_credentials`: Credential rejection.
- `test_login_view_with_email`, `test_logout_view`: Session lifecycle.
- `test_password_reset_dispatches_email`: Mailpit email outbox delivery.
- `test_telematics_stream_headers_and_payload`: SSE streaming headers & payloads.

### Localization & i18n (`test_localization.py`)
- `test_french_translation_rendering_in_trip_list`: French catalog assertions.
- `test_spanish_translation_rendering_in_trip_list`: Spanish catalog assertions.
- `test_language_switch_endpoint`: Cookie persistence.
- `test_model_choice_gettext_lazy_translation`: `gettext_lazy` choice translation.

### Seeder Command (`test_commands.py`)
- `test_seed_fleet_management_command`: Bulk data generation (3,000+ rows).
