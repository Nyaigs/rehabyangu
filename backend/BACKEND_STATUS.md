# RehabYangu Backend – Status & Architecture

## Overview
Multi‑tenant SaaS backend for rehabilitation facilities. Built with Django & DRF.  
All data is tenant‑isolated at the application layer via `Tenant` and `TenantMembership`.

## Multi‑Tenancy
- Shared DB, application‑level isolation through `Tenant` + `TenantMembership`.
- Per‑tenant user IDs (e.g., `SER‑001`) auto‑generated on membership creation.
- All views use `request.tenant` (set by custom JWT auth) for scoping.
- Global superadmin (`rehabyangu`) can access any active tenant without a membership.

## Authentication & Authorization
- JWT issued at `POST /api/token/` with `X‑Tenant` header.
- Tokens carry `tenant_id`, `role`, `is_rehab_admin` claims.
- Superusers receive `super_admin` role and bypass membership checks.
- `TenantJWTAuthentication` attaches `request.tenant` and `request.tenant_membership`.
- RBAC via `Permission` + `Role` models, enforced by `HasPermission`.
- `IsInTenant` permission applied to all views.

## Subscription & Billing
- Tenant fields: `status`, `plan`, `billing_cycle`, `monthly_fee`, `trial_ends_at`, `grace_period_end`.
- Management command `check_subscriptions` updates statuses (trial→overdue→suspended).
- Cron job (host) runs it daily at 2 AM.
- Login blocked (402) if tenant suspended/overdue; mid‑session access also denied.

## Audit Logging
- `AuditLog` model: actor, tenant, action, object type/id, description, IP, timestamp.
- Tenant‑scoped API: `GET /api/audit-logs/`.
- Automatic signals for `Patient` and `Appointment` create/update/delete.
- Admin integration for superadmins.

## App Hardening Status
| App           | View Hardening | Tenant Scoping | RBAC Permissions | Auto Auditing |
|---------------|---------------|----------------|------------------|--------------|
| patients      | ✅            | ✅             | ✅               | ✅           |
| tenants       | ✅            | ✅             | ✅               | N/A          |
| inventory     | ✅            | ✅             | ✅               | ❌           |
| vitals        | ✅            | ✅             | ✅               | ❌           |
| clinical      | ✅            | ✅             | ✅               | ❌           |
| appointments  | ✅            | ✅             | ✅               | ✅           |
| billing       | ✅            | ✅             | ✅               | ❌           |
| subscriptions | ✅            | ✅             | ✅               | N/A          |
| users         | ✅            | ✅             | ✅               | N/A          |
| authorization | ✅            | ✅             | ✅               | N/A          |

All views now use `request.tenant` and `TenantMembership`. No code references the deprecated `UserProfile.tenant`.

## Strengths
- Clean multi‑tenant architecture without schema‑per‑tenant complexity.
- Strong RBAC with roles & direct permissions.
- Subscription lifecycle enforced at login and on every request.
- Audit trail ready for healthcare compliance.
- Superadmin bypass for platform‑wide management.
- Per‑tenant user IDs for professional logging/display.

## Future Work (Low Priority)
- Add audit signals for other models (Vitals, ClinicalNotes, Billing, Inventory).
- 4‑day grace‑period warning notifications in `check_subscriptions`.
- Unit & integration tests.
- Finer‑grained role permissions via admin UI.
- Celery for background tasks (email/SMS) – not currently needed.

*Last updated: August 2, 2026*
