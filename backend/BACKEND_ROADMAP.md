# Backend Improvement Roadmap

Planned enhancements to the RehabYangu backend.  
Items are listed in rough priority order and can be tackled incrementally.

---

## Audit & Compliance
- [ ] Add automatic audit logging for **Vitals** (create / update / delete)
- [ ] Add automatic audit logging for **Clinical Notes** (create / update / delete)
- [ ] Add automatic audit logging for **Billing** (charges, payments, invoices)
- [ ] Add automatic audit logging for **Inventory** (stock additions / removals)
- [ ] Implement comprehensive audit log retention policy (e.g., archive logs older than 1 year)

## Subscription & Billing
- [ ] Send 4‑day grace‑period warning notifications to tenant admins (in‑app + email)
- [ ] Implement automated payment reminders (e.g., 7 days before next billing date)
- [ ] Add support for yearly billing cycle (logic exists, needs testing)
- [ ] Build a billing history endpoint for tenants (list of invoices / payments)
- [ ] Add **bill clearance** step to discharge flow (accountant/director confirms balance paid before final approval)
- [ ] Auto‑generate invoice upon patient discharge if balance > 0
- [ ] Self‑service tenant sign‑up (trial registration) – future

## Testing & Quality
- [ ] Write unit tests for authentication flow (JWT, tenant scoping, superuser bypass)
- [ ] Write integration tests for RBAC (role‑based access enforcement)
- [ ] Write tests for subscription management commands (`check_subscriptions`)
- [ ] Add API documentation with Swagger / OpenAPI (drf‑spectacular)
- [ ] Set up CI pipeline (GitHub Actions) to run migrations, lint, and tests

## Performance & Scalability
- [ ] Optimise permission caching (`get_user_permissions` currently caches for 5 min)
- [ ] Add database indexes on frequently filtered fields (e.g., `tenant_id` on all scoped models)
- [ ] Evaluate connection pooling for PostgreSQL (e.g., pgbouncer) for production
- [ ] Implement rate limiting for critical endpoints (login, patient list)
- [ ] Add a health‑check endpoint (`GET /api/health/`) for monitoring tools

## Architecture & Maintainability
- [ ] Version the API (e.g., `/api/v1/`) to allow non‑breaking future changes
- [ ] Refactor repeated `get_queryset` / `perform_create` patterns into a reusable mixin
- [ ] Add a custom Django management command to seed demo data for new tenants
- [ ] Move background tasks (email / SMS) to Celery for reliability (currently not needed)
- [ ] Implement proper logging configuration (request logs, error alerts)
- [ ] Create a **Director** role (`DR` prefix) with permissions (view financials, manage staff, approve discharges)
- [ ] Add staff creation endpoint (`POST /api/staff/create/`) and document role assignment flow

## Security
- [ ] Review and tighten CORS settings for production (currently allows all origins)
- [ ] Enforce HTTPS with secure cookie flags in production
- [ ] Add two‑factor authentication (2FA) for rehab admin accounts
- [ ] Conduct a security audit of permission checks across all views
- [ ] Build a **superadmin impersonation endpoint** (obtain tenant‑scoped token without re‑logging in)

## Developer Experience
- [ ] Provide a one‑command setup script for new developers (bootstrap DB, create demo data)
- [ ] Add pre‑commit hooks for linting (Black, isort, flake8)
- [ ] Document internal API conventions (error format, pagination, filtering)

## Automation & Notifications
- [ ] Inventory stock deduction API (nurse records usage, system subtracts quantity)
- [ ] Low‑stock notification when `current_stock` falls below `reorder_level`
- [ ] Automated daily/weekly reports (PDF/Excel) emailed to rehab admins (patient census, revenue, low‑stock)
- [ ] Automated daily PostgreSQL backup with retention policy (cron job)
- [ ] Automated discharge workflow notifications (bill cleared → admin alerted to approve)

---

*This roadmap is a living document. Items can be added, removed, or re‑prioritised as the project evolves.*
