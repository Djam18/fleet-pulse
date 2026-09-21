# 05. User Flows & State Transitions — FleetPulse

## 1. Authentication & Onboarding Flow

```
[Unauthenticated User]
         │
         ▼
  GET /accounts/login/
         │
    ┌────┴───────────────────────────┐
    │                                │
[Existing Operator]           [New Operator]
    │                                │
    │ POST /login/                   │ Click "Register"
    │ (Username or Email)            ▼
    │                         GET /register/
    │                                │
    ▼                         POST /register/
Valid Session Established            │
    │                         Auto-Login & Redirect
    └────────────────┬───────────────┘
                     ▼
          GET / (Dashboard View)
```

## 2. Password Recovery Flow via Mailpit

```
[Forgot Password]
         │
         ▼
GET /password-reset/ ──> Enter Registered Email
         │
         ▼
POST /password-reset/
         │
         ├──> Generates UID & One-Time Cryptographic Token
         └──> Dispatches SMTP Email to Mailpit (127.0.0.1:1025)
         │
         ▼
GET /password-reset/done/ (User prompted to check Mailpit inbox)
         │
         ▼
User opens http://localhost:8025 and clicks reset link:
GET /reset/<uidb64>/<token>/
         │
         ▼
User inputs & confirms new secure password
         │
         ▼
POST /reset/<uidb64>/<token>/ ──> Password updated in DB
         │
         ▼
GET /reset/done/ ──> Click "Sign In Now"
```

## 3. Vehicle Operational Lifecycle & State Machine

```
               [New Asset Registration]
                          │
                          ▼
                     ┌──────────┐
          ┌─────────>│  ACTIVE  │<────────┐
          │          └────┬─────┘         │
          │               │               │
  Service Completed       │ Odometer /    │ Service
  & Tested                │ Schedule Due  │ Completed
          │               ▼               │
          │       ┌──────────────┐        │
          └───────┤ MAINTENANCE  ├────────┘
                  └───────┬──────┘
                          │
                          │ Asset Reaches End of Life
                          ▼
                     ┌──────────┐
                     │ RETIRED  │
                     └──────────┘
```
