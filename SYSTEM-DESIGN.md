# RehabYangu — System Design

**Author:** Lead System Design
**Audience:** Engineering, Product, Clinical Advisory
**Status:** Draft v1.0 — foundation for all module work going forward

---

## 1. What we're building

RehabYangu is a multi-tenant hospital management system for rehabilitation
centres, addiction treatment facilities, and mental health institutions
across Kenya and East Africa. Each facility ("tenant") gets an isolated,
branded environment covering clinical care, operations, and billing —
without running its own infrastructure.

Three things make this system different from a generic hospital SaaS:

1. **The data is unusually sensitive.** Addiction and mental health records
   carry more stigma risk than a broken arm. Access control and audit
   logging aren't a compliance checkbox here — they're core product
   requirements, on par with uptime.
2. **Connectivity is not guaranteed.** Facilities may be in areas with
   patchy power or internet. The system has to degrade gracefully, not
   just perform well on a good connection.
3. **Payment and insurance rails are local.** Billing has to speak to
   Kenya's Social Health Authority (SHA, successor to NHIF) and M-Pesa
   natively — these aren't optional integrations, they're how most
   facilities actually get paid.

Everything below is designed around those three constraints first, and
generic SaaS best practice second.

---

## 2. Guiding principles

- **Tenant isolation is a security boundary, not just a filter.** No query
  path may return cross-tenant data, even by accident. This is enforced
  at the database layer, not just in application code (see §4).
- **Every read of a clinical record is logged.** Not just writes. Who
  looked at a patient's file, when, and why is itself clinical governance
  data.
- **The API is the product.** Web app, future mobile app, and any future
  integrations all go through the same versioned API — no backend logic
  lives only in the frontend.
- **Design for the facility's worst day, not its best.** Intermittent
  connectivity, a lapsed insurance API, a staff member locked out — the
  system should fail in ways that keep patient care moving.
- **Boring technology where it doesn't matter, careful design where it
  does.** We don't need a novel database for appointment scheduling. We do
  need careful design for consent, access control, and audit trails.

---

## 3. High-level architecture

*(see the architecture diagram above)*

Four layers, each independently deployable and independently scalable:

**Client applications** — the React/TypeScript web app (this is what
Phase 1 built the login for) and, later, a mobile companion app for
clinicians doing rounds or community outreach.

**API gateway** — single entry point for all clients. Handles
authentication (JWT validation), rate limiting, request routing to the
correct domain service, and tenant resolution (mapping a subdomain or
token claim to a `tenant_id` before anything downstream runs).

**Domain services** — the business logic, organized by bounded context
rather than by database table. Each service owns its own data access and
exposes a versioned REST API. Early on these can run as modules within one
deployable backend (a "modular monolith") rather than separate
microservices — see §11 for why that's the right starting point.

**Data layer** — PostgreSQL as the system of record (tenant-isolated, see
§4), Redis for sessions/caching/rate-limit counters, and S3-compatible
object storage for documents, scanned consent forms, and lab attachments.

**External integrations** — SHA claims submission, M-Pesa (Daraja API)
for payments, and an SMS/WhatsApp gateway (Africa's Talking or similar)
for appointment reminders and staff notifications. These sit behind an
integrations service so a provider swap (e.g. changing SMS vendors) never
touches domain logic.

---

## 4. Multi-tenancy strategy

**Model: shared database, shared schema, row-level isolation — with a
credible path to dedicated databases for facilities that require it.**

Every tenant-owned table carries a `tenant_id` column. Two enforcement
layers, not one:

1. **Application layer:** every ORM query is automatically scoped by the
   authenticated request's `tenant_id`. No hand-written query bypasses
   this — it's middleware, not developer discipline.
2. **Database layer:** PostgreSQL **Row-Level Security (RLS)** policies on
   every tenant-owned table, keyed to a session variable set at the start
   of each request. Even a bug in application-layer scoping cannot leak
   another tenant's rows, because the database itself refuses to return
   them.

**Why shared schema over database-per-tenant to start:** dramatically
simpler migrations, connection pooling, and cost at the scale we're
launching at (tens, not thousands, of facilities). It also makes
cross-tenant product analytics possible without data replication.

**Escape hatch:** a small number of enterprise facilities (e.g. a
government-run referral hospital with its own compliance mandate) may
require a fully isolated database. The schema and service layer are
designed so a tenant can be migrated to a dedicated database later without
an application rewrite — `tenant_id` scoping logic is identical either
way, only the connection routing changes.

**Branding resolution:** on load, the client resolves its tenant from the
subdomain (`greenfields.rehabyangu.com`) and fetches
`GET /tenants/current`, which returns `{ displayName, logoUrl,
primaryColor, legalEntityName }`. This is the exact shape already defined
in `src/config/tenant.ts` in Phase 1 — the frontend does not need to
change when this becomes a live endpoint, only where the data comes from.

---

## 5. Domain modules

| Module | Owns | Key responsibilities |
|---|---|---|
| **Identity & tenancy** | Users, roles, tenants, sessions | Authentication, RBAC, tenant provisioning, staff invitations, MFA |
| **Patient records (EMR)** | Patients, admissions, clinical notes, treatment plans | Intake, diagnosis, progress notes, care plans, discharge summaries |
| **Scheduling** | Appointments, bed/room allocation | Clinician calendars, group therapy sessions, bed board for inpatient units |
| **Billing & claims** | Invoices, payments, SHA claims | Invoice generation, M-Pesa/card payment capture, SHA claim submission and status tracking |
| **Pharmacy & inventory** | Medication stock, dispensing records | Controlled-substance tracking (critical for addiction treatment facilities), stock levels, reorder alerts |
| **Staff & HR** | Employee records, shifts, credentials | Roster management, licence/certification expiry tracking |
| **Notifications** | Reminders, alerts | Appointment reminders (SMS/WhatsApp), medication alerts, staff notifications |
| **Reporting & analytics** | Dashboards, exports | Occupancy, revenue, outcomes reporting; regulator-facing reports |
| **Audit & compliance** | Access logs, consent records | Immutable audit trail, consent capture and versioning, data retention enforcement |

**Module boundaries matter more than the deployment topology.** Whether
these run as one backend process or ten services, each module must only
talk to another module through its public API — never by reaching into
another module's tables. That discipline is what lets us split services
later without a rewrite.

### 5.1 Patient records (EMR) — the core of the product

- Patient demographics, next of kin, and admission history.
- Clinical notes are **append-only and versioned** — a correction creates
  a new version with the original preserved, never an in-place edit. This
  is standard clinical record-keeping practice and a common regulatory
  requirement.
- Treatment plans link to structured goals and progress tracking, not
  just free text, so outcomes reporting (§5.6) has something to aggregate.
- Every field marked sensitive (substance use history, HIV status,
  psychiatric diagnosis) is access-controlled independently of general
  patient data — a front-desk role can see demographics without seeing
  clinical notes.

### 5.2 Billing & claims — where local integration complexity lives

- Invoices support mixed payment sources per line item: self-pay, SHA
  cover, and third-party (employer/NGO-sponsored) in the same invoice.
- SHA claim submission is modeled as its own state machine
  (`draft → submitted → queried → approved/rejected → paid`) because
  claims routinely bounce back for correction — the UI needs to represent
  that loop, not just success/failure.
- M-Pesa integration uses the Daraja STK Push flow for in-person payment
  and C2B for patient/family-initiated payment, with webhook confirmation
  reconciled asynchronously (Daraja callbacks are not always immediate).

### 5.3 Pharmacy & inventory

Addiction treatment facilities dispense controlled substances
(methadone, buprenorphine, benzodiazepines) under tighter regulatory
scrutiny than general stock. Dispensing records here are treated with the
same append-only, audited pattern as clinical notes — a dispensing entry
is never deleted, only reversed with a linked correction entry.

### 5.4 Scheduling

Two distinct calendars that most hospital systems conflate: **clinician
schedules** (one-on-one and group sessions) and **bed/room occupancy**
(inpatient capacity). Treating them as separate resources avoids the
common bug where discharging a patient doesn't free a bed because the
system only modeled "appointments."

### 5.5 Notifications

SMS is the reliable channel in this market — not push notifications, not
email. WhatsApp Business API as a secondary channel where the facility
opts in. Every notification type (appointment reminder, medication
reminder, billing notice) is configurable per tenant, since a mental
health facility may deliberately want more discreet reminder wording than
a general rehab centre.

### 5.6 Reporting & analytics

Two audiences with very different needs: **facility operators** (bed
occupancy, revenue, staff utilization — built with Recharts on the
dashboards) and **regulators/funders** (aggregate outcomes reporting,
often required for continued licensing or grant funding). The data model
is designed so regulator reports are a query against existing structured
treatment-plan data, not a manual reporting exercise bolted on later.

### 5.7 Audit & compliance

This module is a dependency of every other module, not a peer. Any write
to a clinical, billing, or identity record emits an audit event
(`who, what, when, before/after state, tenant`) to an append-only store.
Read access to clinical records is also logged, not just writes — see §7.

---

## 6. Data architecture

### 6.1 Core entities (overview)

```
Tenant
 └─ User (role, staff profile)
 └─ Patient
     └─ Admission
         └─ ClinicalNote (versioned)
         └─ TreatmentPlan
             └─ TreatmentGoal
     └─ Appointment
     └─ Invoice
         └─ InvoiceLineItem
         └─ Payment
         └─ ShaClaim
     └─ ConsentRecord (versioned)
 └─ AuditEvent (append-only, references any entity above)
```

Every entity below `Tenant` carries `tenant_id` and is subject to the
RLS policy described in §4. `AuditEvent` is intentionally modeled as a
generic append-only log referencing `(tenant_id, entity_type, entity_id)`
rather than per-module audit tables — one consistent place to query "show
me everything that happened to this record."

### 6.2 Data classification

| Class | Examples | Handling |
|---|---|---|
| **Highly sensitive** | Substance use history, psychiatric diagnosis, HIV status | Field-level access control, encrypted at rest with a separate key, always audit-logged on read |
| **Sensitive** | General clinical notes, billing detail | Role-based access, audit-logged on write |
| **Operational** | Appointments, staff rosters | Standard tenant-scoped access |
| **Public/branding** | Tenant display name, logo | No restriction beyond tenant scoping |

### 6.3 Retention and deletion

Kenya's Data Protection Act, 2019 gives data subjects a right to
erasure, but clinical records also carry statutory retention requirements
that typically override a deletion request. The design resolves this with
**soft deletion plus anonymization**: a patient's identifying fields can
be irreversibly anonymized on request while the clinical record structure
(needed for facility accreditation and continuity of care history) is
retained. This distinction needs sign-off from a compliance advisor before
Phase 2 data modeling locks it in — flagged here as an open decision, not
a settled one.

---

## 7. Security model

- **Authentication:** email + password today (Phase 1), with mandatory
  MFA for admin and clinical roles before general availability — password
  alone is not an acceptable bar for psychiatric/addiction records.
- **Authorization:** role-based access control (RBAC) scoped per tenant.
  Roles are facility-configurable (a small facility may merge "clinician"
  and "admin"; a large one won't) but every role maps to a fixed set of
  underlying permissions — permissions are not free-text.
- **Encryption:** TLS 1.2+ in transit everywhere, AES-256 at rest for the
  database and object storage, with highly sensitive fields (§6.2)
  additionally encrypted at the application layer so a database-level
  breach alone doesn't expose them in plaintext.
- **Audit trail:** immutable, append-only, includes read access to
  clinical records — not just writes. Audit data itself is retained
  longer than operational data and is not editable by any application
  role, including tenant admins.
- **Session management:** short-lived access tokens, refresh token
  rotation, and forced re-authentication for highly sensitive actions
  (e.g. exporting a patient's full record).
- **Compliance posture:** designed against the Kenya Data Protection
  Act, 2019 as the baseline, with the data classification model in §6.2
  giving us a documented basis for a Data Protection Impact Assessment
  before general availability.

---

## 8. API design

- REST over HTTPS, JSON payloads, versioned in the URL path (`/api/v1/...`)
  so breaking changes don't require coordinated client/server deploys.
- Every endpoint enforces tenant scoping and RBAC at the gateway before
  the request reaches domain logic — a domain service should never need
  to re-check "does this user belong to this tenant."
- Consistent error shape across all services:
  ```json
  {
    "error": {
      "code": "VALIDATION_ERROR",
      "message": "Enter a valid email address",
      "fieldErrors": { "email": "Enter a valid email address" }
    }
  }
  ```
- Pagination via cursor (not offset) on any list endpoint expected to grow
  unbounded (clinical notes, audit events) — offset pagination degrades
  badly on large tables and is easy to get subtly wrong under concurrent
  writes.
- Idempotency keys required on payment-initiating endpoints (M-Pesa STK
  Push, invoice creation) so a retried request from a flaky connection
  can't double-charge a patient.

---

## 9. Infrastructure & delivery

- **Environments:** local → staging → production, with staging running
  against anonymized or synthetic data only — never a copy of production
  clinical data.
- **Containers + orchestration:** each service ships as a container;
  starting on a managed container platform rather than self-managed
  Kubernetes until the operational complexity is justified by scale.
- **CI/CD:** every merge to main runs type-checking, linting, and tests;
  deploys to staging automatically, production on manual approval.
- **Observability:** structured logging with `tenant_id` and `request_id`
  on every log line, so a support ticket from one facility can be traced
  without grepping through every other tenant's traffic.
- **Backups & disaster recovery:** automated daily database backups with
  point-in-time recovery, tested restores on a schedule — not just
  configured and assumed to work.
- **Offline resilience:** given intermittent connectivity at some
  facilities, the web app should tolerate brief disconnection gracefully
  (queued form submissions, clear "reconnecting" states) rather than
  losing in-progress clinical documentation. This is a frontend
  requirement worth designing for explicitly in the EMR module, not an
  afterthought.

---

## 10. External integrations

| Integration | Purpose | Notes |
|---|---|---|
| **SHA (Social Health Authority)** | Insurance claims submission and status | Claim state machine (§5.2); expect API instability and design for retries and manual reconciliation |
| **M-Pesa (Daraja API)** | Patient/family payments | STK Push for in-person, C2B for remote; webhook-based confirmation |
| **SMS/WhatsApp gateway** | Appointment and medication reminders | Africa's Talking or equivalent; per-tenant opt-in and message wording |
| **Card payments** | Secondary payment rail | Deferred until M-Pesa and SHA flows are stable — smaller share of real-world transactions in this market |

All integrations are accessed through an internal **integrations
service** — domain modules call our own internal API, never a third-party
SDK directly. This means a vendor swap, an API version bump, or an outage
mitigation (e.g. queuing SHA submissions during an outage) happens in one
place.

---

## 11. Why a modular monolith to start

For a system at launch scale (a handful to low hundreds of facilities),
running domain modules as one deployable backend — cleanly separated
internally, per §5 — is the right call over microservices from day one:

- Transactions that span modules (e.g. discharging a patient, closing
  their invoice, and freeing a bed) are simple in one database transaction
  and genuinely hard across service boundaries.
- One deployable means one CI/CD pipeline, one on-call surface, and no
  premature investment in service mesh, distributed tracing, or
  inter-service auth — none of which the team benefits from yet.
- The module boundaries in §5 are designed so that if a specific module
  (most likely billing, given its integration load) later needs to scale
  or deploy independently, it can be extracted without redesigning its
  API — because it was never allowed to reach into another module's
  tables in the first place.

---

## 12. Open decisions requiring sign-off

These are flagged, not resolved, and should not block Phase 2 build-out —
but need an answer before general availability:

1. Anonymization vs. hard deletion policy for right-to-erasure requests
   (§6.3) — needs compliance/legal input.
2. MFA enforcement timeline — mandatory at launch, or phased in per role?
3. Dedicated-database threshold — at what tenant size/sensitivity do we
   proactively offer isolated infrastructure rather than waiting for a
   request?
4. WhatsApp as a reminder channel for mental health/addiction contexts —
   some patients may not want treatment-related messages on a shared
   family device; needs a per-patient consent flag, not just per-tenant.

---

## 13. Suggested delivery sequence

1. **Phase 1 — done:** Login and multi-tenant branding shell.
2. **Phase 2:** Identity & tenancy (roles, staff invitations, tenant
   provisioning) — everything else depends on this existing first.
3. **Phase 3:** Patient records (EMR) core — patients, admissions,
   clinical notes.
4. **Phase 4:** Scheduling — appointments and bed/room allocation.
5. **Phase 5:** Billing & claims — invoicing, M-Pesa, SHA claim flow.
6. **Phase 6:** Pharmacy & inventory, staff/HR, notifications.
7. **Phase 7:** Reporting & analytics, audit dashboard for compliance
   review.

Each phase should ship with its own data model review and, for anything
touching clinical or billing data, a lightweight security review before
merge — not a large end-of-project audit.
