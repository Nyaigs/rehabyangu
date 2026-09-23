# Security Handover — Benjie

**Date:** 2026-09-23
**From:** Project Lead
**To:** Benjie Koimett

## Context

You reviewed RehabYangu on 2026-09-23 and flagged 14 issues (documented in
`docs/security-hardening.md`). The fixes already applied are listed below.
The remaining ones are open for you to complete.

## Already fixed (commit 7a887b2 and the pending security commit)

1. **Default DB password removed.** `settings.py` now requires `DB_PASSWORD`.
2. **Host-based tenant enumeration disabled in production.** `get_tenant()`
   only falls back to hostname parsing when `DEBUG=True`.
3. **Platform admin check corrected.** Superusers with a tenant_id can still
   authenticate as platform admins.
4. **Production security headers added.** HSTS, secure cookies, SSL redirect,
   X-Frame-Options — all gated behind `if not DEBUG`.
5. **CORS hardened.** No production URL as a hardcoded default. Production
   requires `CORS_ALLOWED_ORIGINS` env var.
6. **Discharge balance check.** `RequestDischargeView` blocks discharge when
   the patient has an outstanding balance unless `force=True` with a reason.
7. **Token refresh throttled.** `TenantTokenRefreshView` uses the `login`
   throttle scope.

## Still open — over to you

1. **MFA encryption key validation.** Currently required in settings but
   not validated for length. Should be ≥32 bytes when MFA is used.
2. **Idle timeout (10 min / 9 min warning).** Per TRD 7.2. Frontend work
   in `AuthContext.tsx`.
3. **Permission cache invalidation.** Currently expires after 300s. Should
   invalidate on role/membership change via signals.
4. **RLS middleware concern.** Your review flagged `transaction.atomic()`
   + `connection.cursor()`. Verify the pattern is safe or replace it.
5. **Audit log retention.** Add an `audit_rotate` command that archives
   logs older than 730 days (7-year retention for Kenya compliance).
6. **OpenAPI schema.** Add `drf-spectacular` for `/api/schema/` and
   `/api/docs/`.

## Environment setup

- Doppler project: `rehabyangu`
- Your invite: check `koimettb@gmail.com` inbox
- Run: `doppler login && doppler setup`
- Backend: `docker-compose up -d` then `docker exec -e DB_USER=rehabyangu -e DB_PASSWORD=rehabyangu123 rehabyangu_backend python manage.py test`

## Coordination

- Work on a branch: `git checkout -b security/remaining-fixes`
- Push and open a PR when done
- I'll review and merge
- Ping me on WhatsApp if blocked
