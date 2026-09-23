# RehabYangu

**Enterprise Multi-Tenant Rehabilitation Management Platform**

Built by [WeiraLynk](https://github.com/weiralynk)

RehabYangu is a commercial SaaS platform for rehabilitation centres, mental health hospitals, addiction treatment facilities, psychiatric hospitals, and wellness centres. It replaces fragmented paper records and spreadsheets with one secure, cloud-based system.

---

## Project Information

| Field | Value |
|---|---|
| **Product** | RehabYangu |
| **Owner** | WeiraLynk |
| **Engineering Leads** | Project Lead & [Benjie Koimett](https://github.com/bkoimett) |
| **Repository** | https://github.com/Nyaigs/rehabyangu |
| **Status** | Pre-pilot — security hardening in progress |

---

## Key Features

- Patient management & electronic medical records
- Admissions, discharges, and clinical notes (append-only, versioned)
- Psychiatry, counselling, nursing, and pharmacy workflows
- Billing, invoicing, and payment tracking
- Inventory & pharmacy stock management
- Staff management with role-based access control (RBAC)
- Multi-tenant architecture with tenant-specific branding
- Subscription & billing lifecycle (trial → overdue → grace → suspended)
- Immutable audit logging
- Super-admin dashboard for platform-wide oversight

---

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, TypeScript, Vite, Tailwind CSS, TanStack Router, TanStack Query, React Hook Form, Zod, Recharts |
| Backend | Django 6.0, Django REST Framework, Simple JWT |
| Database | PostgreSQL 16 (shared schema + Row-Level Security) |
| Cache | Redis 7 |
| Auth | JWT with server-side session revocation |
| Secrets | Doppler (production) |
| Containerisation | Docker Compose |

---

## Quick Start

Prerequisites: Docker, Docker Compose, Node.js 20+.

```bash
git clone https://github.com/Nyaigs/rehabyangu.git
cd rehabyangu
cp backend/.env.example backend/.env
# Edit backend/.env with your local values
docker-compose up -d
docker exec -e DB_USER=rehabyangu -e DB_PASSWORD=rehabyangu123 \
  rehabyangu_backend python manage.py migrate
docker exec rehabyangu_backend python manage.py seed_default_roles

Frontend: http://localhost:5173
Backend API: http://localhost:8000/api/
Documentation

Full documentation is in the docs/ folder:

    Documentation Index

    Multi-Tenancy Architecture

    Security Hardening

    Secrets Management

    Technical Requirements (TRD)

    Product Requirements (PRD)

    Implementation Plan

    UI/UX Brief

    Business Plan

License

Proprietary — © WeiraLynk. All rights reserved.
