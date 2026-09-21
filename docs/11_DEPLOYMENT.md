# 11. Deployment & Infrastructure Guide — FleetPulse

## 1. System Requirements & Environment
- **Runtime**: Python 3.12+ (tested on Python 3.12.3)
- **Framework**: Django 4.2 LTS (`Django==4.2.30`)
- **Container Services**:
  - `ats-mailpit`: SMTP server on `127.0.0.1:1025`, Web UI on `http://127.0.0.1:8025`.
  - `postgres_global` / `postgis`: Optional relational database backend on `127.0.0.1:5432`.
  - `valkey_global`: Redis-compatible cache & session backend on `127.0.0.1:6380`.

## 2. Environment Configuration
Configuration is loaded via environment variables (`dj_database_url`, `SECRET_KEY`, `DEBUG`):
```ini
DEBUG=True
SECRET_KEY=django-insecure-fleetpulse-dev-key
DATABASE_URL=sqlite:///backend/db.sqlite3
EMAIL_HOST=127.0.0.1
EMAIL_PORT=1025
EMAIL_USE_TLS=False
DEFAULT_FROM_EMAIL=FleetPulse Security <no-reply@fleetpulse.local>
```

## 3. Setup & Initialization Commands
```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Run database migrations
cd backend
python manage.py migrate

# 3. Compile GNU gettext message catalogs
python manage.py compilemessages -i ".venv*"

# 4. Seed 3,000+ realistic fleet records
python manage.py seed_fleet

# 5. Start development server
python manage.py runserver 0.0.0.0:8000
```

## 4. Production WSGI / ASGI Deployment
For high-concurrency production deployments handling both standard HTTP requests and long-lived Server-Sent Events (SSE):
- **Web Server**: Gunicorn with Uvicorn worker class or ASGI (Daphne/Uvicorn).
- **Reverse Proxy**: NGINX with buffering disabled for streaming (`proxy_buffering off; proxy_cache off;`).
- **Static Assets**: Collected via `python manage.py collectstatic` and served directly by NGINX or WhiteNoise.
