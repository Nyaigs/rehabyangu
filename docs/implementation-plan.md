# RehabYangu — Implementation Plan

**Version:** 0.2
**Owner:** WeiraLynk Engineering
**Status:** Current
**Last Updated:** 2026-09-23

## 1. Team

| Role | Person |
|---|---|
| Engineering Lead | Project Lead |
| Engineering | [Benjie Koimett](https://github.com/bkoimett) |
| Development Partner | WeiraLynk |

AI coding assistants are used as tooling to accelerate implementation. They are not counted as team members.

## 2. Multi-Tenancy Strategy

Shared schema with Row-Level Security.

Each tenant is a row-level scope within one PostgreSQL database. Every tenant-owned table carries a `tenant_id` column. RLS policies enforce isolation at the database layer.

## 3. Onboarding Model

Invite-based. Facility admins invite staff by email. Invitees receive a single-use link, set their own password, and land directly in the correct tenant with a pre-assigned role. No self-registration.

## 4. Sprint Progress

| Sprint | Focus | Status |
|---|---|---|
| Sprint 1 | Auth, multi-tenancy foundation, RBAC scaffold | Done |
| Sprint 2 | Tenant membership, RLS, super admin, subscriptions | Done |
| Sprint 3 | EMR backend, clinical notes, admissions, medications | Done |
| Sprint 4 | Security hardening, RBAC consolidation, reports | Done |
| Sprint 5 | M-Pesa integration, SMS reminders, deployment | Next |

## 5. Near-Term Roadmap

### Sprint 5 — Payments & Deployment
- M-Pesa Daraja integration (STK Push for patient payments)
- Per-tenant M-Pesa credentials in Settings
- Invoice PDF with tenant logo and payment details
- Deployment to Oracle Cloud Free Tier + Cloudflare Tunnel

### Sprint 6 — Clinical Depth
- Treatment plan UI (goals, progress tracking)
- Discharge summary PDF
- Sensitive field masking in UI
- Bed/ward management

### Sprint 7 — Operations & Compliance
- SMS/WhatsApp appointment reminders
- Audit log viewing for facility admins
- ODPC registration and DPIA

## 6. Definition of Done (Pilot)

- Staff log in with workspace + email/username + password
- Each user sees only their facility's data (verified by test)
- RBAC enforced on the backend (not just hidden in the UI)
- Patient registration, admission, clinical notes, vitals work end-to-end
- Invoices generate with facility branding
- Audit logs are written and immutable

## 7. Deployment Target

- Frontend: Cloudflare Pages
- Backend: Oracle Cloud Free Tier (ARM VM) with Docker
- Database: PostgreSQL on the same VM (migrates to managed DB at scale)
- TLS & CDN: Cloudflare
- Secrets: Doppler
- CI/CD: GitHub Actions
