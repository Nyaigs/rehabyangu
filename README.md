# RehabYangu

**Enterprise Multi‑Tenant Rehabilitation Management Platform**  
Built by [Weiraro Technologies](https://weiraro.com)

RehabYangu is a commercial SaaS platform designed for rehabilitation centres, mental health hospitals, addiction treatment facilities, psychiatric hospitals, and wellness centres. It replaces fragmented paper records and spreadsheets with a single, secure, cloud‑based system.

## Key Features
- Patient management & electronic medical records
- Admissions, discharges, and clinical notes
- Psychiatry, counselling, nursing, and pharmacy workflows
- Billing, invoicing, and payment tracking
- Inventory & pharmacy stock management
- Staff management with role‑based access control (RBAC)
- Multi‑tenant architecture with tenant‑specific branding
- Subscription & billing lifecycle enforcement
- Comprehensive audit logging
- Super‑admin dashboard for platform‑wide oversight

## Technology Stack
| Layer       | Technology                                      |
|-------------|-------------------------------------------------|
| Frontend    | React (TypeScript), Vite, Tailwind CSS, TanStack Router, TanStack Query, React Hook Form, Zod, Recharts |
| Backend     | Django 6.0, Django REST Framework, Simple JWT   |
| Database    | PostgreSQL 16                                   |
| Cache       | Redis 7                                         |
| Auth        | JWT (access & refresh tokens)                   |
| Containerisation | Docker Compose                              |

## Getting Started
```bash
git clone https://github.com/Nyaigs/rehabyangu.git
cd rehabyangu
docker-compose up -d
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
