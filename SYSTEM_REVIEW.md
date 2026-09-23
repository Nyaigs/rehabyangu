# System Review Report: RehabYangu

## 1. Application Type & Deployment Target
- **Type**: Enterprise multi-tenant SaaS rehabilitation management platform
- **Frontend**: React 19 + TypeScript + Vite + TanStack Router + Tailwind CSS
- **Backend**: Django 6.0 + Django REST Framework + Simple JWT
- **Database**: PostgreSQL 16 (schema-per-tenant)
- **Cache/Redis**: Redis 7
- **Deployment**: Docker Compose (db, redis, backend, frontend)
- **Target**: Rehabilitation centres, mental health hospitals, addiction treatment facilities

## 2. Authentication & Authorization

### Confirmed Issues

| # | Issue | Affected File | Evidence |
|---|-------|---------------|----------|
| A1 | **Inverted platform admin check** - `TenantJWTAuthentication.authenticate()` line 19: `if not user.is_superuser or tenant_id is not None` means a superuser with a `tenant_id` cannot authenticate as platform admin. This breaks the platform admin flow for superusers who also belong to a tenant. | `backend/users/authentication.py:19` | `if is_platform_admin and (not user.is_superuser or tenant_id is not None): raise AuthenticationFailed` |
| A2 | **Host-based tenant enumeration** - `TenantTokenObtainPairView.get_tenant()` lines 81-83 extracts tenant subdomain from hostname: `host = request.get_host().split(':')[0].split('.')` then `if len(host) >= 3 and host[0] not in ('www', 'localhost', '127'): slug = host[0]`. This allows attackers to enumerate valid tenant subdomains by brute-forcing hostnames. | `backend/users/views_auth.py:81-83` | Hostname parsing reveals subdomain without rate limiting |
| A3 | **Missing session validation on token refresh** - `TenantTokenRefreshView` uses `refresh['session_id']` and `refresh['tenant_id']` from the token payload but doesn't verify the session belongs to the authenticating user. A compromised refresh JTI could be reused. | `backend/users/views_auth.py:89-103` | `AuthSession.objects.get(id=refresh['session_id'], user_id=refresh['user_id'], ...)` - no user verification beyond JWT |
| A4 | **Race condition in AuthSession creation** - `TenantTokenObtainPairSerializer` creates a new `AuthSession` on every login without checking for existing active sessions. Multiple concurrent logins create duplicate sessions. | `backend/users/views_auth.py:41` | `session = AuthSession.objects.create(user=user, tenant=tenant, ...)` |
| A5 | **Stale permission cache** - `get_user_permissions()` caches permissions for 300s (`timeout=300`). If roles/permissions change, users get stale permissions until cache expires. | `backend/authorization/utils.py:27` | `cache.set(cache_key, perms, timeout=300)` |
| A6 | **No CSRF exemption rationale** - `TenantTokenObtainPairView` has `authentication_classes = []` and `permission_classes = [AllowAny]`. CSRF protection is bypassed for the login endpoint, which is expected for API auth but should be documented. | `backend/users/views_auth.py:61-63` | `permission_classes = [AllowAny], authentication_classes = []` |

## 3. Secrets & Configuration Handling

### Confirmed Issues

| # | Issue | Affected File | Evidence |
|---|-------|---------------|----------|
| B1 | **Insecure default database credentials** - `settings.py:163` has `PASSWORD='rehabyangu123'` as default. If `.env` is missing or incomplete, the database password is exposed in version control. | `backend/config/settings.py:163` | `'PASSWORD': os.environ.get('DB_PASSWORD', 'rehabyangu123')` |
| B2 | **Empty MFA encryption key default** - `settings.py:133`: `MFA_ENCRYPTION_KEY = os.getenv('MFA_ENCRYPTION_KEY', '')`. Empty string as default means if MFA is enabled without configuring the key, TOTP secrets could be stored unencrypted. | `backend/config/settings.py:133` | `MFA_ENCRYPTION_KEY = os.getenv('MFA_ENCRYPTION_KEY', '')` |
| B3 | **Missing security headers** - No `SECURE_HSTS_SECONDS`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, or `SECURE_SSL_REDIRECT` configured in Django settings. These are recommended for production HTTPS deployment. | `backend/config/settings.py` | Not present in the file |
| B4 | **CORS origins from environment** - `CORS_ALLOWED_ORIGINS` read from env with defaults `http://localhost:5173,https://app.rehabyangu.com`. If not overridden in production, could allow unexpected origins. | `backend/config/settings.py:86-89` | `os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:5173,https://app.rehabyangu.com')` |

## 4. Common Web Security Risks

### Confirmed Issues

| # | Issue | Affected File | Evidence |
|---|-------|---------------|----------|
| C1 | **TenantRLSMiddleware wraps every request in `transaction.atomic()`** - Line 12-18 of `middleware.py` ensures single transaction but `set_rls_context()` uses raw `connection.cursor()` which bypasses connection pooling. This could cause RLS context to leak between requests or cause connection pool exhaustion under load. | `backend/users/middleware.py` | `with transaction.atomic(): set_rls_context()` |
| C2 | **No rate limiting on token refresh** - `TenantTokenRefreshView` has `permission_classes = [AllowAny]`, `authentication_classes = []`, and no `throttle_scope` set. Can be brute-forced without restriction. | `backend/users/views_auth.py:89-91` | No `throttle_scope` attribute |
| C3 | **Debug mode not hard-coded for production** - `DEBUG` reads from env with `'False'` default. If `DEBUG=True` is set in production, it exposes sensitive information. | `backend/config/settings.py:32` | `DEBUG = os.getenv('DEBUG', 'False').lower() in ('1', 'true', 'yes')` |
| C4 | **X-Frame-Options not explicitly set** - No `X_FRAME_OPTIONS` middleware setting visible. The `ClickJacking` middleware is present but without explicit header configuration. | `backend/config/settings.py:82` | `django.middleware.clickjacking.XFrameOptionsMiddleware` in MIDDLEWARE |

## 5. SEO & Crawlability

- **SPA nature**: The frontend is a React SPA with TanStack Router. No server-side rendering (SSR) or static HTML generation for key routes.
- **Meta tags**: `index.html` exists but only has basic structure; no dynamic meta tag injection seen in the source.
- **Search engine accessibility**: Limited for SPA without SSR or pre-rendering. The `notFoundComponent` at root route serves a simple 404 page.
- **Sitemap/robots.txt**: Not found in the project structure.

## 6. AI Discoverability & Machine-Readable Documentation

- **Documentation format**: PRD, TRD, implementation plan, and other docs are in Markdown format.
- **No OpenAPI/Swagger schema**: Backend DRF endpoints don't appear to have automatic OpenAPI generation configured (no `drf-yasg` or `spectacular` seen in dependencies).
- **Machine-readable docs**: The documentation exists but isn't machine-discoverable via standard API specification tools.

## 7. Accessibility & Core User Paths

- **WCAG 2.1 AA**: Cited in PRD as a requirement but not verified in the codebase.
- **Frontend components**: Use Radix UI primitives (`@radix-ui/react-*`) which are accessible by default, but:
  - No `alt` text handling seen in image components
  - Color contrast depends on Tailwind CSS custom properties set from tenant branding
  - Focus management not explicitly addressed in custom hooks
- **Core user paths**: 
  - Login → AuthContext login → token storage → refreshAuth → dashboard
  - Onboarding flow for rehab admins with `onboarding_completed_at` check
  - Patient admission → clinical notes → vitals → pharmacy → billing → discharge

## 8. Documentation vs Actual Behavior

| # | Documentation Claim | Actual Behavior | Discrepancy |
|---|-----|----------------|-------------|
| D1 | PRD 5.1: "When a user clicks 'Discharge' on a patient, the system MUST check the patient's outstanding balance" | `RequestDischargeView` creates a discharge request but does **not** check the patient's balance. Balance check appears only in `DischargedPatientsView` which lists balances but doesn't block discharge. | **Missing balance check** at discharge initiation |
| D2 | PRD 5.3: "Tablet/Capsule: Whole numbers ONLY" with error "Tablets must be dispensed in whole numbers" | No dosage-form validation found in the pharmacy/inventory code. The `Dispense` endpoint and related serializers don't enforce whole number vs decimal rules based on dosage form. | **Validation missing** |
| D3 | TRD 7.2: "JWT with refresh tokens. Session idle timeout: 10 minutes (warning at 9 minutes)" | No idle timeout/warning logic found in frontend (AuthContext) or backend. Token expiry is only the JWT `ACCESS_TOKEN_LIFETIME` (30 min) and `REFRESH_TOKEN_LIFETIME` (7 days). | **Idle timeout not implemented** |
| D4 | PRD 4.3: "Discharged Patients Section: Show all discharged patients with discharge date. Outstanding balances displayed clearly in red if > 0" | `DischargedPatientsView` displays balances but colors depend on frontend Tailwind classes. No enforcement that discharged patients don't appear in active lists is seen in the PatientViewSet `get_queryset` which filters by tenant only. | **No tenant-scoped filtering to exclude discharged** |
| D5 | TRD 4.2: "Tenant identification via Subdomain: tenant_name.rehabyangu.com" | Backend `get_tenant()` method (views_auth.py:78-86) falls back to hostname parsing when `X-Tenant` header is absent. This means the subdomain method is optional, not primary. | **Implementation differs from design** |

## 9. Tests, Lint, Typecheck & Build

- **Backend**: Python files compile successfully. No `pytest` or test frameworks configured in `requirements.txt` beyond Django.
- **Frontend**: `node_modules` not installed; `npm run lint` fails due to missing `eslint` binary and `@eslint/js` peer dependency. `npm run build` would fail similarly.
- **TypeScript**: `tsconfig.json` has `strict: true`, `noUnusedLocals: true`, `noUnusedParameters: true` - but cannot verify without node modules.
- **Docker**: `docker-compose.yml` defines 4 services (db, redis, backend, frontend) with proper health checks. Backend Dockerfile installs deps from `requirements.txt`.

## 10. Prioritized Factual Report

### Critical Risks (must-fix before release)

1. **Insecure default database credentials** (`settings.py:163`)
   - Default password `rehabyangu123` is embedded in source code
   - **Remediation**: Remove default value; enforce `DB_PASSWORD` env var; add to `.env.example` with placeholder

2. **Host-based tenant enumeration vulnerability** (`views_auth.py:81-83`)
   - Attackers can enumerate valid tenant subdomains by varying the Host header
   - **Remediation**: Require `X-Tenant` header for all authentication; remove hostname-based fallback or add rate limiting

3. **Missing balance check at discharge initiation** (PRD 5.1 non-compliance)
   - `RequestDischargeView` creates discharge requests without checking outstanding balance
   - **Remediation**: Add balance check before creating discharge request; block if balance > 0

4. **Empty MFA encryption key default** (`settings.py:133`)
   - Empty string default could expose TOTP secrets if MFA enabled without configuration
   - **Remediation**: Make `MFA_ENCRYPTION_KEY` required (no default); add startup validation

### High Risks (fix before production)

5. **Inverted platform admin check** (`authentication.py:19`)
   - Superusers with tenant context cannot authenticate as platform admins
   - **Remediation**: Review and correct the logic; ensure platform admins without tenant context work correctly

6. **Missing security headers** (HSTS, secure cookies, etc.)
   - Production HTTPS deployment without recommended Django security settings
   - **Remediation**: Add `SECURE_HSTS_SECONDS`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_SSL_REDIRECT`

7. **CORS misconfiguration risk**
   - Default origins could be used in production if env vars not set
   - **Remediation**: Pin production origins; remove production-like defaults from code

8. **TenantRLSMiddleware transaction management**
   - `transaction.atomic()` with raw `connection.cursor()` for RLS could cause context leaks or pool exhaustion
   - **Remediation**: Use `set_rls_context` outside of `transaction.atomic()` or use `SET CONFIG` properly within Django's connection management

9. **Missing idle timeout/warning** (PRD 7.2)
   - No 10-minute session timeout with 9-minute warning as specified in TRD
   - **Remediation**: Implement session timeout/warning in frontend and/or backend

10. **Token refresh without rate limiting**
    - `TenantTokenRefreshView` unauthenticated and unthrottled
    - **Remediation**: Add `throttle_scope = 'login'` or similar; add rate limiting

### Medium Risks (address in next sprint)

11. **Stale permission cache** (300s timeout)
    - Users may have outdated permissions after role changes
    - **Remediation**: Add cache invalidation on role/permission changes; reduce cache timeout

12. **No OpenAPI/Swagger documentation**
    - API endpoints lack machine-readable specification
    - **Remediation**: Add `drf-spectacular` or `drf-yasg` for API documentation

13. **No sitemap/robots.txt for SEO**
    - SPA without search engine accessibility
    - **Remediation**: Add static sitemap and robots.txt; consider SSR or static generation

14. **No audit log retention policy enforcement**
    - Audit logs stored but no TTL or archival mechanism seen
    - **Remediation**: Implement log rotation/archival per TRD 12.1-12.3

15. **No OpenAPI/Swagger documentation** - API endpoints lack machine-readable specification for clients and AI tools
16. **Missing sitemap/robots.txt** - SPA without search engine accessibility support
17. **No session idle timeout/warning** - TRD 7.2 specifies 10-min timeout with 9-min warning, not implemented
18. **Stale permission cache** - 300s cache timeout may cause outdated permission displays

---
*Review Date: 2026-09-23*
*Application: RehabYangu - Multi-tenant rehabilitation management platform*