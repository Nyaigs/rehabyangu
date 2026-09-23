# Security Hardening Log

**Status:** Current
**Last Updated:** 2026-09-23

This document records security fixes applied to RehabYangu, the reasoning, and how each is verified.

## Critical Fixes

| # | Issue | Fix |
|---|---|---|
| 1 | Hardcoded default DB password | Removed default. DB_PASSWORD required. |
| 2 | MFA key could be empty | MFA_ENCRYPTION_KEY required; startup validates >= 32 bytes. |
| 3 | Platform admin with tenant_id could not authenticate | Fixed logic: superusers always pass platform-admin check. |
| 4 | Host-based tenant enumeration | Production requires X-Tenant header. |
| 5 | No balance check at discharge | Discharge blocked when outstanding balance > 0 unless forced with reason. |
| 6 | Token refresh unthrottled | Added ScopedRateThrottle with login scope. |

## High-Priority Fixes

| # | Issue | Fix |
|---|---|---|
| 7 | Missing security headers | Added SECURE_SSL_REDIRECT, SESSION_COOKIE_SECURE, CSRF_COOKIE_SECURE, HSTS, X_FRAME_OPTIONS. |
| 8 | CORS defaulted to production URLs | Production requires CORS_ALLOWED_ORIGINS. |
| 9 | RLS middleware transaction pattern | Confirmed atomic + set_rls_context(local=True) pattern. |
| 10 | No idle timeout | Frontend enforces 10-minute idle timeout with 9-minute warning. |

## Medium-Priority Fixes

| # | Issue | Fix |
|---|---|---|
| 11 | Permission cache not invalidated | Signal handlers clear cache on role/membership change. |
| 12 | No audit log retention | audit_rotate management command archives logs older than 730 days. |
| 13 | No OpenAPI schema | Added drf-spectacular. |

## Non-Applicable Items

SEO/sitemap/robots.txt do not apply — the application is behind authentication and clinical data must not be indexed.

## Verify

