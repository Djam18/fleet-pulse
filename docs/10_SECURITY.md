# 10. Security Architecture & Threat Model — FleetPulse

## 1. Authentication & Session Hardening
- **Dual Authentication**: `EmailOrUsernameModelBackend` authenticates users using either their username or email via a case-insensitive query (`username__iexact`, `email__iexact`).
- **Session Protection**:
  - `SESSION_COOKIE_HTTPONLY = True`: Disallows JavaScript access to session tokens, preventing XSS-based session hijacking.
  - `SESSION_COOKIE_AGE = 43200`: Enforces a 12-hour maximum session lifespan.
  - `CSRF_COOKIE_HTTPONLY = False`: Allows front-end forms to attach standard CSRF tokens via `{% csrf_token %}`.
- **Route Guards**: Operational views are decorated with `@login_required(login_url='fleet:login')`.

## 2. Password Policies & Reset Security
- **Password Validators**:
  - `UserAttributeSimilarityValidator`
  - `MinimumLengthValidator` (enforces 8+ characters)
  - `CommonPasswordValidator` (blocks top 20,000 common passwords)
  - `NumericPasswordValidator` (blocks purely numeric passwords)
- **Tokenized Password Reset**:
  - Employs HMAC cryptographic tokens with one-time use semantics (`PasswordResetTokenGenerator`).
  - Delivered via local SMTP (`127.0.0.1:1025`) directly to Mailpit in development, isolating outbound communications from public internet leaks.

## 3. Database Injection & Query Defenses
- **Defensive ORM**: 100% of queries use Django's parameterized ORM query compiler, preventing SQL injection.
- **Database Constraints**: Integrity invariants (`check_trip_end_gte_start`, `uniq_veh_service_code`) are executed inside the database engine.

## 4. Cross-Site Scripting (XSS) & Content Security
- **Safe JSON Serialization**: Context data passed to client-side charts is encoded exclusively via Django's `json_script` template tag.
- **Auto-Escaping**: Django's template engine operates with automatic HTML escaping enabled.
