# Progressive Django Upgrade Roadmap (4.2 LTS $\rightarrow$ 5.2 LTS)

This guide documents the progressive migration path for FleetPulse across major and feature releases, including deprecation markers, automated refactoring with `django-upgrade`, and verification commands.

---

## Upgrade Philosophy

Django projects should **never** skip intermediate feature releases when jumping across major versions. The official path is:
$$\text{Django 4.2 LTS} \longrightarrow \text{Django 5.0} \longrightarrow \text{Django 5.1} \longrightarrow \text{Django 5.2 LTS}$$

This ensures that:
1. Deprecation warnings are surfaced before the underlying feature is removed.
2. Database schema migrations run cleanly without conflicting ORM states.
3. Third-party packages (e.g. Django REST Framework) maintain compatibility at each step.

---

## Phase 1: Django 4.2 LTS Baseline

### Characteristics
- Python environment: Python 3.10 – 3.12.
- Settings: Legacy storage settings (`DEFAULT_FILE_STORAGE`, `STATICFILES_STORAGE`).
- ORM: Trip distance and fuel economy computed in Python `save()`.
- Forms: Explicit field loops rendered in HTML.
- Views: Decorated individually with `@login_required`.

### Pre-Upgrade Audit Command
Before upgrading to Django 5.0, run the test suite with deprecation warnings enabled:
```bash
python -Wd manage.py test
python -Wd manage.py check
```

---

## Phase 2: Upgrading to Django 5.0

### Key Changes & Features
1. **`Field.db_default`**:
   - Model fields can define database-level defaults (`db_default="ACTIVE"`), evaluated in SQL rather than Python.
2. **`GeneratedField`**:
   - Trip distance (`end_odometer - start_odometer`) is migrated from Python `save()` calculations to a native database `GeneratedField(expression=..., output_field=models.IntegerField(), db_persist=True)`.
3. **Form Field Groups**:
   - Forms adopt `{{ form.field.as_field_group }}` for simplified template markup with automated `aria-describedby` accessibility attributes.
4. **Settings Cleanup**:
   - Verify `USE_TZ = True` is used. Note that `USE_L10N` and `pytz` are removed in 5.0 in favor of Python's standard `zoneinfo`.

### Automated Modernization
```bash
pip install django-upgrade
django-upgrade --target-version 5.0 **/*.py
```

### Upgrade Command
```bash
pip install "Django~=5.0.0"
python manage.py makemigrations
python manage.py migrate
python -Wd manage.py test
```

---

## Phase 3: Upgrading to Django 5.1

### Key Changes & Breaking Deprecations
1. **`DEFAULT_FILE_STORAGE` & `STATICFILES_STORAGE` Removed**:
   - *Breaking Change*: These settings are completely removed in 5.1.
   - *Fix*: Migrate to the `STORAGES` dictionary in `settings.py`:
     ```python
     STORAGES = {
         "default": {
             "BACKEND": "django.core.files.storage.FileSystemStorage",
         },
         "staticfiles": {
             "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
         },
     }
     ```
2. **`LoginRequiredMiddleware`**:
   - Replace manual view `@login_required` decorators across the backend with global `LoginRequiredMiddleware` in `settings.py`.
   - Add `@login_not_required` decorator to public endpoints (login, health check, public fleet overview).
3. **`{% querystring %}` Template Tag**:
   - Replace custom query parameter preservation logic in pagination links with the native `{% querystring page=page_obj.next_page_number %}`.

### Upgrade Command
```bash
django-upgrade --target-version 5.1 **/*.py
pip install "Django~=5.1.0"
python manage.py makemigrations
python manage.py migrate
python -Wd manage.py test
```

---

## Phase 4: Upgrading to Django 5.2 LTS (Target)

### Key Changes & Long-Term Stability
1. **Composite Primary Keys**:
   - Refactor `MaintenanceSchedule` to use `models.CompositePrimaryKey('vehicle_id', 'service_code')`.
2. **Interactive Shell Auto-Imports**:
   - `python manage.py shell` automatically imports models for all installed apps.
3. **Long-Term Support**:
   - Full enterprise stability and security fixes guaranteed through **April 2028**.

### Upgrade Command
```bash
django-upgrade --target-version 5.2 **/*.py
pip install "Django~=5.2.0"
python manage.py makemigrations
python manage.py migrate
python -Wd manage.py test
```
