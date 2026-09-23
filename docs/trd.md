# RehabYangu — Technical Requirements Document (TRD)

**Version:** 0.2
**Owner:** WeiraLynk Engineering
**Status:** Current
**Last Updated:** 2026-09-23

## 1. Purpose

This document defines the technical architecture, design decisions, and implementation strategy for RehabYangu.

## 2. Architecture Overview

RehabYangu is a multi-tenant SaaS platform using a shared-database, shared-schema architecture with PostgreSQL Row-Level Security (RLS) for tenant isolation.

### 2.1 High-Level Components

┌─────────────────────────────────────────────────────────────┐
│ Frontend (React + TypeScript) │
│ Dashboard · EMR · Pharmacy · Billing · Reports · Admin │
└──────────────────────────┬──────────────────────────────────┘
│ HTTPS / JWT
▼
┌─────────────────────────────────────────────────────────────┐
│ API Gateway (Nginx — production) │
│ Rate limiting · SSL termination · Static file serving │
└──────────────────────────┬──────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ Backend (Django + DRF) │
│ Authentication · Tenant middleware · Clinical services │
│ Billing · Reports · Audit logging │
└──────────────────────────┬──────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ Data Layer │
│ PostgreSQL 16 — Shared schema, RLS on every tenant table │
│ Redis 7 — Caching, sessions, future Celery broker │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ External Integrations │
│ M-Pesa (Daraja), Email, SMS gateways, S3 (R2) │
└─────────────────────────────────────────────────────────────┘


### 2.2 Multi-Tenancy Strategy

Shared schema with Row-Level Security.

- Every tenant-owned table carries a `tenant_id` column.
- RLS policies on every table restrict rows to the current tenant.
- The application connects as a least-privilege database role (`rehabyangu_app`) that cannot bypass RLS.
- Migrations run as the owner role (`rehabyangu`).

Why shared schema over schema-per-tenant:
- Simpler migrations
- Efficient connection pooling
- Lower operational cost at pilot scale
- Easy cross-tenant analytics for the platform admin
- Enterprise tenants can later be migrated to dedicated databases without a rewrite

### 2.3 Tenant Identification

In production, the `X-Tenant` HTTP header is required on every request. In development (`DEBUG=True`), hostname fallback is allowed for convenience.

### 2.4 Authentication & Sessions

- JWT access and refresh tokens issued by `/api/token/`.
- Every token carries `user_id`, `tenant_id`, `session_id`, `role`, and `is_platform_admin`.
- The `AuthSession` model tracks every active session.
- Logout revokes the session server-side; the token is rejected on the next request even if unexpired.
- Refresh token rotation blacklists the old token.
- Token issuance and refresh are rate-limited.
- MFA (TOTP) is scaffolded; enforcement at login is a future phase.

### 2.5 Security Headers (production)

- SECURE_SSL_REDIRECT = True
- SESSION_COOKIE_SECURE = True
- CSRF_COOKIE_SECURE = True
- SECURE_HSTS_SECONDS = 31536000
- SECURE_HSTS_INCLUDE_SUBDOMAINS = True
- SECURE_CONTENT_TYPE_NOSNIFF = True
- X_FRAME_OPTIONS = 'DENY'
- SECURE_REFERRER_POLICY = 'same-origin'

### 2.6 Secrets Management

Production secrets are managed in Doppler. The backend reads all secrets from environment variables injected by `doppler run`. See `docs/secrets-management.md`.

### 2.7 Deployment

- Local: Docker Compose (db, redis, backend, frontend).
- Production: Oracle Cloud Free Tier (ARM VM) + Cloudflare Tunnel + Cloudflare Pages for the frontend. Alternative: Hetzner VPS with Kamal.
- CI: GitHub Actions runs the full test suite, Django checks, frontend build, and performance budget on every push.
