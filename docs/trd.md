# RehabYangu – Technical Requirements Document (TRD)
**Version:** 0.1  
**Owner:** Product Architect  
**Status:** On Review  
**Last Updated:** 2026-07-11  


## 1. Purpose
This document defines the technical architecture, design decisions, and implementation strategy for RehabYangu. It is the bridge between the Product Requirements (PRD) and the actual codebase.

- **Audience:** Developers, DevOps, QA, and technical stakeholders.
- **Goal:** Ensure that the system is secure, scalable, maintainable, and production‑ready.


## 2. Architecture Overview
RehabYangu follows a **modular, service‑oriented architecture** with clear separation of concerns.

### 2.1 High‑Level Components
┌─────────────────────────────────────────────────────────────────┐
│ Frontend (React + TS) │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │ Dashboard │ │ EMR │ │ Pharmacy │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │ Billing │ │ Reports │ │ Admin │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
│ HTTPS / JWT
▼
┌─────────────────────────────────────────────────────────────────┐
│ API Gateway (Nginx) │
│ - Rate limiting, SSL termination, static file serving │
└───────────────────────────┬─────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│ Backend (Django + DRF) │
│ ┌───────────────────────────────────────────────────────────┐ │
│ │ Authentication & Security (JWT, MFA, RBAC/ABAC) │ │
│ ├───────────────────────────────────────────────────────────┤ │
│ │ Tenant Middleware (schema routing) │ │
│ ├───────────────────────────────────────────────────────────┤ │
│ │ Clinical Services (EMR, vitals, MAR, pharmacy) │ │
│ ├───────────────────────────────────────────────────────────┤ │
│ │ Billing & Finance Services (invoicing, payments) │ │
│ ├───────────────────────────────────────────────────────────┤ │
│ │ Reporting & Document Generation (PDF, Word, Excel) │ │
│ └───────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│ Data Layer │
│ ┌───────────────────────────────────────────────────────────┐ │
│ │ PostgreSQL (schema‑per‑tenant + public schema) │ │
│ │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │ │
│ │ │ Tenant A │ │ Tenant B │ │ Public │ │ │
│ │ │ schema │ │ schema │ │ schema │ │ │
│ │ └─────────────┘ └─────────────┘ └─────────────┘ │ │
│ ├───────────────────────────────────────────────────────────┤ │
│ │ Redis (caching, sessions, Celery broker) │ │
│ └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│ Async Jobs (Celery) │
│ - Email/SMS notifications, PDF generation, billing tasks │
└─────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│ External Integrations │
│ - M‑Pesa API, Email providers, SMS gateways, S3 storage │
└─────────────────────────────────────────────────────────────────┘

### 2.2 Key Design Principles
- **Separation of Concerns:** Each module has a single responsibility.
- **API‑First:** All functionality exposed via RESTful APIs.
- **Stateless:** JWT tokens ensure no server‑side session state (except Redis for caching).
- **Asynchronous:** Long‑running tasks (PDF generation, emails) are offloaded to Celery.


## 3. Technology Stack
### 3.1 Backend
| Component | Choice | Rationale |
|-----------|--------|-----------|
| **Language** | Python 3.11+ | Mature ecosystem, healthcare libraries, rapid development. |
| **Framework** | Django 4.2+ | Built‑in admin, ORM, migrations, security features. |
| **API Layer** | Django REST Framework (DRF) | Robust serialization, authentication, view sets. |
| **Task Queue** | Celery 5.3+ | Async job processing (PDF, email, billing). |
| **Broker** | Redis 7+ | Lightweight, fast, also used for caching and sessions. |
| **Database** | PostgreSQL 15+ | ACID compliance, JSON support, schema‑per‑tenant. |
| **Object Storage** | S3‑compatible (MinIO dev, AWS S3 prod) | Scalable, secure file storage for logos, documents, attachments. |

### 3.2 Frontend
| Component | Choice | Rationale |
|-----------|--------|-----------|
| **Language** | TypeScript 5+ | Type safety, maintainability. |
| **Framework** | React 18+ | Component‑based, rich ecosystem. |
| **Build Tool** | Vite 5+ | Fast development, modern bundling. |
| **Styling** | Tailwind CSS 3+ | Utility‑first, consistent design system. |
| **UI Components** | shadcn/ui | Accessible, customizable, production‑ready. |
| **State Management** | TanStack Query 5+ | Server‑state management, caching, polling. |
| **Routing** | TanStack Router | Type‑safe routing, nested layouts. |
| **Forms** | React Hook Form + Zod | Performant, validation with schema. |

### 3.3 Infrastructure
| Component | Choice | Rationale |
|-----------|--------|-----------|
| **Containerization** | Docker + Docker Compose | Consistent dev/prod environments. |
| **Web Server** | Nginx | Reverse proxy, SSL termination, static files. |
| **CI/CD** | GitHub Actions | Integrated with GitHub, automated testing & deployment. |
| **Monitoring** | Prometheus + Grafana + Loki | Metrics, logging, alerting. |
| **Error Tracking** | Sentry | Real‑time error reporting. |


## 4. Multi‑Tenant Architecture
### 4.1 Strategy: Schema‑per‑tenant
**Decision:** We will use a separate PostgreSQL schema for each tenant (facility).

**Advantages:**
- Strong data isolation (critical for healthcare).
- Easy backup/restore per tenant.
- Simplified compliance audits.

**Disadvantages:**
- Migration complexity (we'll automate this).
- Higher connection overhead (we'll use connection pooling).

### 4.2 Implementation Details
#### Tenant Identification

Each request must carry a tenant identifier. We will support two methods:

1. **Subdomain:** `tenant_name.rehabyangu.com` (recommended for production).
2. **Header:** `X-Tenant-ID` (fallback for development/testing).

The **tenant middleware** extracts the identifier and sets the PostgreSQL search path:

```python
# Middleware pseudocode
def tenant_middleware(get_response):
    def middleware(request):
        tenant = extract_tenant(request)
        if tenant:
            connection.set_schema(tenant.schema_name)
            request.tenant = tenant
        else:
            # handle public schema requests (login, registration)
            pass
        return get_response(request)
    return middleware

Database Connection Pooling

We'll use pgbouncer in transaction‑pooling mode to minimise connection overhead.
Migrations

Django migrations will be applied to all tenant schemas using a custom migration runner:
python

class MultiSchemaMigrator:
    def apply_migrations(self):
        for tenant in Tenant.objects.all():
            with connection.cursor() as cur:
                cur.execute(f"SET search_path TO {tenant.schema_name}, public")
                # Run migrations here

Backup & Restore

    pg_dump -n tenant_schema for per‑tenant backups.

    Point‑in‑time recovery via PostgreSQL WAL archiving.

4.3 Public Schema

The public schema stores tenant‑agnostic data:

    tenants table (tenant ID, schema name, config).

    users table (global user accounts, linked to tenants).

    System‑wide configurations.

5. Data Models (Core Entities)

Below are the key Django models. This is a high‑level overview – full field definitions will be in the detailed data dictionary (available separately).
5.1 Tenant
python

class Tenant(models.Model):
    name = models.CharField(max_length=255)
    schema_name = models.CharField(max_length=63, unique=True)
    facility_name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='logos/')
    primary_color = models.CharField(max_length=7, default='#2563eb')
    subscription_plan = models.CharField(max_length=50)
    subscription_status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

5.2 User (Extended Django User)
python

class User(AbstractUser):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    roles = models.ManyToManyField(Role)
    is_active = models.BooleanField(default=False)  # requires admin approval
    pending_approval = models.BooleanField(default=True)

5.3 Patient
python

class Patient(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    patient_id = models.CharField(max_length=20, unique=True)  # auto-generated
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10)
    national_id = models.CharField(max_length=20)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    address = models.TextField()
    emergency_contact_name = models.CharField(max_length=255)
    emergency_contact_phone = models.CharField(max_length=15)
    next_of_kin_name = models.CharField(max_length=255)
    next_of_kin_relationship = models.CharField(max_length=50)
    next_of_kin_phone = models.CharField(max_length=15)
    sponsor = models.ForeignKey('Sponsor', null=True, blank=True)
    insurance_details = models.JSONField(default=dict)
    referral_source = models.CharField(max_length=50)
    photo = models.ImageField(upload_to='patient_photos/', blank=True)
    is_admitted = models.BooleanField(default=False)
    is_discharged = models.BooleanField(default=False)

5.4 Admission
python

class Admission(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT)
    admission_number = models.CharField(max_length=20, unique=True)  # ADM-YYYY-XXXX
    admission_date = models.DateTimeField(auto_now_add=True)
    ward = models.ForeignKey(Ward, on_delete=models.PROTECT)
    bed = models.ForeignKey(Bed, on_delete=models.PROTECT)
    primary_diagnosis = models.TextField()
    psychiatric_diagnosis = models.TextField()
    substance_use_history = models.JSONField(default=dict)
    medical_history = models.TextField(blank=True)
    surgical_history = models.TextField(blank=True)
    family_history = models.TextField(blank=True)
    allergies = models.JSONField(default=list)
    current_medications = models.JSONField(default=list)
    consent_forms = models.FileField(upload_to='consents/')
    discharge_date = models.DateTimeField(null=True, blank=True)
    discharge_reason = models.TextField(blank=True)
    outstanding_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

5.5 Clinical Note (Base for all notes)
python

class ClinicalNote(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    note_type = models.CharField(max_length=50)  # MSE, progress, nursing, etc.
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_archived = models.BooleanField(default=False)
    
    class Meta:
        abstract = True

5.6 Vitals
python

class VitalSign(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    recorded_by = models.ForeignKey(User, on_delete=models.PROTECT)
    date_time = models.DateTimeField()
    blood_pressure_systolic = models.IntegerField()
    blood_pressure_diastolic = models.IntegerField()
    heart_rate = models.IntegerField()
    respiratory_rate = models.IntegerField()
    temperature = models.DecimalField(max_digits=4, decimal_places=1)
    oxygen_saturation = models.IntegerField()
    blood_sugar = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    pain_score = models.IntegerField()  # 0-10
    created_at = models.DateTimeField(auto_now_add=True)
    # Restrict edit after 24 hours via business logic

5.7 Pharmacy – Drug
python

class Drug(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    brand_name = models.CharField(max_length=255)
    generic_name = models.CharField(max_length=255)
    strength = models.CharField(max_length=50)  # e.g., "500mg"
    dosage_form = models.CharField(max_length=50)  # Tablet, Capsule, Syrup, etc.
    batch_number = models.CharField(max_length=50)
    supplier = models.CharField(max_length=255)
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2)
    stock_quantity = models.IntegerField()
    min_stock_level = models.IntegerField()
    max_stock_level = models.IntegerField()
    expiry_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

5.8 Billing – Invoice
python

class Invoice(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT)
    sponsor = models.ForeignKey(Sponsor, null=True, blank=True)
    invoice_number = models.CharField(max_length=20, unique=True)  # INV-YYYY-XXXX
    generated_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    outstanding = models.DecimalField(max_digits=12, decimal_places=2)
    pdf_file = models.FileField(upload_to='invoices/', blank=True)
    is_paid = models.BooleanField(default=False)

5.9 Audit Log
python

class AuditLog(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    action = models.CharField(max_length=255)
    resource_type = models.CharField(max_length=50)
    resource_id = models.CharField(max_length=36)  # UUID of the affected record
    details = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_immutable = True  # enforced in application logic

6. API Design
6.1 RESTful Principles

    Versioned: /api/v1/ prefix.

    Authentication: JWT (Bearer token) for all endpoints except /auth/*.

    Authorization: Checked via RBAC/ABAC in permissions classes.

    Pagination: limit and offset for list endpoints.

    Filtering: ?field=value.

    Sorting: ?ordering=field (prefix - for descending).

6.2 Key Endpoints
Method	Endpoint	Description
POST	/api/v1/auth/login/	Login, returns JWT pair.
POST	/api/v1/auth/register/	Create user account (pending approval).
POST	/api/v1/auth/refresh/	Refresh JWT token.
GET	/api/v1/patients/	List patients (filtered by tenant).
POST	/api/v1/patients/	Create patient.
GET	/api/v1/patients/{id}/	Get patient details.
PUT	/api/v1/patients/{id}/	Update patient.
POST	/api/v1/patients/{id}/admit/	Admit patient.
POST	/api/v1/patients/{id}/discharge/	Initiate discharge.
GET	/api/v1/patients/{id}/vitals/	Get vitals history.
POST	/api/v1/patients/{id}/vitals/	Record new vitals.
GET	/api/v1/pharmacy/drugs/	List drugs.
POST	/api/v1/pharmacy/dispense/	Dispense medication.
GET	/api/v1/billing/invoices/	List invoices.
POST	/api/v1/billing/invoices/	Generate invoice.
POST	/api/v1/billing/payments/	Record payment.
GET	/api/v1/reports/	Generate reports (with query params).
GET	/api/v1/audit-logs/	List audit logs (admin only).
6.3 Authentication & Authorization

    JWT tokens have a short lifetime (15 minutes) with refresh token (7 days).

    Each endpoint checks the user's roles/permissions via DRF permission classes.

    Admin endpoints (e.g., role creation, system config) require is_superuser or custom permission.

7. Security Architecture
7.1 Zero Trust Principles

    Never trust, always verify: Every request is authenticated and authorised.

    Least privilege: Users have only the permissions they need.

    Immutable audit trails: All sensitive actions logged.

    Encryption at rest and in transit: TLS 1.3, database encryption.

7.2 Authentication & Session

    JWT with refresh tokens.

    Optional MFA (planned for Phase 2).

    Session idle timeout: 10 minutes (warning at 9 minutes).

    Password hashing: Django's default PBKDF2.

7.3 Authorization (RBAC + ABAC)

Roles are defined per tenant. Each role has a set of permissions (e.g., can_view_patient, can_edit_vitals). We'll implement both:

    RBAC: Roles assigned to users.

    ABAC: Additional attributes (e.g., user's department, patient's ward) can be used for fine‑grained access.

7.4 Data Encryption

    At rest: PostgreSQL TDE (or filesystem‑level encryption) and encrypted S3 buckets.

    In transit: TLS 1.3 enforced.

7.5 Audit Logging

    Every create/update/delete of sensitive data (patients, admissions, billing, etc.) is logged.

    Logs are stored in a separate table (or database) with INSERT‑only permissions.

7.6 Security Headers

    Strict-Transport-Security

    X-Content-Type-Options: nosniff

    X-Frame-Options: DENY

    Content-Security-Policy (restrictive).

8. Integration Points
Service	Purpose	Protocol	Data Format
M‑Pesa	Payment processing	REST API	JSON
Email Provider	Transactional emails (SendGrid, SMTP)	SMTP / REST	HTML / Plain
SMS Gateway	SMS notifications (Africa's Talking)	REST API	JSON
Object Storage	File storage (logos, docs)	S3 API	Binary / JSON
WhatsApp Business API	Notifications (future)	REST API	JSON
9. Deployment Strategy
9.1 Environment Separation

    Development: Local Docker Compose.

    Staging: Separate server (or namespace) for UAT.

    Production: Load‑balanced, multiple workers.

9.2 Containerization

    Backend, Nginx, PostgreSQL, Redis, Celery workers, and PgBouncer are all containerised.

    docker-compose.yml for local and staging.

9.3 CI/CD Pipeline (GitHub Actions)

    Pull Request: Run linters, unit tests, security scans.

    Merge to main: Build Docker images, push to registry.

    Deploy to staging automatically.

    Deploy to production via manual trigger (or after approval).

9.4 Horizontal Scaling

    Stateless Django application can scale horizontally behind a load balancer.

    Database scaling: read replicas for reporting queries.

10. Performance & Scalability
Component	Strategy
Database	Connection pooling (PgBouncer), indexing, read replicas.
Caching	Redis for session storage, query caching (Django cache).
API	Pagination, selective field fetching.
Frontend	Lazy loading, code splitting, CDN for static assets.
Background Jobs	Celery with multiple workers, retries.
11. Monitoring & Observability
Tool	Purpose
Prometheus	Collect metrics (request count, latency, errors, DB connections).
Grafana	Dashboards for team and client.
Loki	Centralised logging (searchable).
Sentry	Real‑time error tracking and alerts.
Health Check	/health/ endpoint for uptime monitoring.
12. Testing Strategy
Level	Scope	Tools
Unit Tests	Models, serializers, business logic	Django Test, pytest
Integration Tests	API endpoints, database interactions	pytest‑django, DRF test client
End‑to‑End (E2E)	Critical user journeys (registration, admission, discharge)	Playwright / Cypress
Security Tests	OWASP top 10 (injection, XSS, etc.)	Bandit, OWASP ZAP, SAST tools

Target: 80%+ test coverage for business‑critical modules.
13. Disaster Recovery & Backup
Item	Detail
Backup Frequency	Daily full backup (pg_dump) + continuous WAL archiving.
Retention	30 days of daily backups, 6 months of monthly.
Recovery Point Objective (RPO)	15 minutes (point‑in‑time recovery).
Recovery Time Objective (RTO)	2 hours (restore from backup + apply WAL).
Backup Storage	Off‑site (S3 bucket) with encryption.
Test Restoration	Monthly restoration test to validate backups.
14. Development Workflow

    Issue / Feature request created in GitHub.

    Branch from main (or develop) with naming: feature/xxx or bugfix/xxx.

    Develop locally with Docker Compose.

    Push branch and create Pull Request.

    CI runs tests, linters, security scans.

    Review by another developer.

    Merge to main.

    Deploy to staging automatically, production manually.

15. Technology Alternatives Considered
Area	Chosen	Alternatives	Why Chosen
Backend	Django + Python	Node.js, .NET, Ruby on Rails	Strong ecosystem, healthcare libraries, security, rapid development.
Database	PostgreSQL	MySQL, MongoDB	ACID compliance, JSON support, schema‑per‑tenant support.
Frontend	React + TS	Vue, Angular	Rich component ecosystem, type safety, large talent pool.
Task Queue	Celery + Redis	AWS SQS, RabbitMQ	Python native, easy integration with Django.
Storage	S3‑compatible	Local filesystem	Scalable, secure, cost‑effective.
16. Risk & Mitigation (Technical)
Risk	Mitigation
Database migration complexity	Automate tenant migrations; test in staging.
Connection pooling issues	Use PgBouncer; monitor connections.
Third‑party integration failure	Implement retries, fallback (e.g., cash payments if M‑Pesa down).
Performance degradation	Load test regularly; scale horizontally.
Data breach	Regular security audits; zero‑trust design.
17. Change Log
Version	Date	Author	Changes
0.1	2026-07-11	Product Architect Initial draft.
