# RehabYangu – Implementation Plan

**Version:** 0.1  
**Owner:** CTO / Engineering Lead  
**Status:** Draft  
**Last Updated:** 2026-07-11  

---

## 1. Purpose

This document defines the **phased roadmap, development sprints, team structure, and milestones** for building RehabYangu. It translates the Product Requirements (PRD), Technical Requirements (TRD), and User Journey documents into a **realistic, actionable plan** that the team can execute.

- **Audience:** Engineering team, product owners, stakeholders.
- **Goal:** Deliver a production‑ready MVP for Serenity Place within 12 weeks.

---

## 2. Development Philosophy

| Principle | Description |
|-----------|-------------|
| **MVP First** | Build the core features first; deliver value early. |
| **Iterative** | Release early, gather feedback, improve. |
| **Quality First** | No shortcuts on security, testing, or documentation. |
| **Tenant‑Ready** | Multi‑tenant from Day 1 – no refactoring later. |
| **Test Driven** | Tests written alongside code. |
| **Documentation** | Code is documented; APIs have OpenAPI specs. |

---

## 3. Team Structure

### 3.1 Core Team (MVP Phase)

| Role | Count | Responsibility |
|------|-------|----------------|
| **Product Owner** | 1 (Brian/Nyaigotti) | Prioritise features, approve decisions |
| **CTO / Architect** | 1 | Technical oversight, architecture |
| **Backend Engineer** | 2 | Django, PostgreSQL, APIs, security |
| **Frontend Engineer** | 2 | React, TypeScript, UI/UX implementation |
| **DevOps Engineer** | 1 | CI/CD, deployment, monitoring |
| **QA Engineer** | 1 | Testing, automation, quality assurance |
| **UX/UI Designer** | 1 | Design system, wireframes, user flows |

**Total:** ~8–9 core team members.

### 3.2 Extended Team (Phase 2+)

| Role | Count | When |
|------|-------|------|
| **Mobile Developer** | 1–2 | Phase 2 |
| **Data Scientist** | 1 | Phase 3 (AI features) |
| **Customer Support** | 1–2 | Post‑launch |
| **Implementation Specialist** | 1–2 | Onboarding new tenants |

---

## 4. Phased Roadmap

### Phase 0: Foundation & Setup (Weeks 1–2)

**Goal:** Establish infrastructure, tooling, and team alignment.

| Week | Activities | Deliverables |
|------|------------|--------------|
| Week 1 | Finalise PRD, TRD, UI/UX Brief. Set up GitHub repo, project board. Initial environment setup (Docker, PostgreSQL, Django). | All docs approved. Dev environment running locally. |
| Week 2 | Set up CI/CD pipeline (GitHub Actions). Establish coding standards. Create database schema (initial models). Create React project structure. | CI/CD pipeline working. Basic Django models. React project scaffolded. |

**Key Decisions:**
- Confirm multi‑tenant strategy (schema‑per‑tenant).
- Confirm technology stack (Django + React + PostgreSQL).
- Set up project management tool (GitHub Projects / Trello / Jira).

---

### Phase 1: Core MVP (Weeks 3–10)

**Goal:** Deliver a working product with core features for Serenity Place.

#### Sprint 1: Authentication & User Management (Weeks 3–4)

| Task | Owner | Description |
|------|-------|-------------|
| User Registration | Backend | Self‑registration with admin approval workflow |
| Login & JWT | Backend | Login, JWT generation, refresh tokens |
| Password Reset | Backend | Email‑based password reset |
| Role Management | Backend | RBAC, pre‑defined roles, custom role creation |
| Admin Dashboard | Frontend | Pending approvals, user management |
| Audit Logging | Backend | Immutable audit trail for sensitive actions |

**Deliverables:**
- Users can register, login, reset password.
- Admins can approve/reject users.
- Roles and permissions enforced.
- Audit logs generated for sensitive actions.

---

#### Sprint 2: Patient Management & Admissions (Weeks 5–6)

| Task | Owner | Description |
|------|-------|-------------|
| Patient Registration | Full‑stack | Registration form with demographics, photo upload, sponsor info |
| Patient Search | Full‑stack | Search by name, ID, phone, admission number |
| Admission Flow | Full‑stack | Admission number generation, ward/bed allocation |
| Ward & Bed Management | Backend | Ward/bed models, availability tracking |
| Patient Listing | Frontend | List with search/filter/pagination |

**Deliverables:**
- Patients can be registered and admitted.
- Beds are allocated and tracked.
- Search and list working.

---

#### Sprint 3: EMR & Clinical Documentation (Weeks 6–7)

| Task | Owner | Description |
|------|-------|-------------|
| Clinical Notes | Full‑stack | Free‑text notes for clinicians |
| Mental State Examination | Full‑stack | Structured MSE template |
| Diagnoses | Backend | DSM‑5/ICD‑10 support |
| Treatment Plans | Full‑stack | Goals, timelines, interventions |
| Vitals Recording | Full‑stack | BP, HR, RR, Temp, SpO2, Blood Sugar, Pain Score |
| Vitals History | Frontend | Table with date filters and trends |

**Deliverables:**
- Clinicians can write notes and MSE.
- Vitals can be recorded, viewed, and trended.
- Abnormal vitals highlighted in red.

---

#### Sprint 4: Pharmacy & MAR (Weeks 7–8)

| Task | Owner | Description |
|------|-------|-------------|
| Drug Inventory | Full‑stack | Add, update, list drugs with batch/expiry |
| Stock Management | Backend | Deduct stock on dispensing, low stock alerts |
| Dispensing | Full‑stack | Dispense with dosage‑form validation (whole vs decimal) |
| MAR | Full‑stack | Medication Administration Record with status |
| Stock Alerts | Backend | Low stock and expiry notifications |

**Deliverables:**
- Drugs can be added, dispensed, and tracked.
- MAR can be recorded and printed.
- Stock and expiry alerts work.

---

#### Sprint 5: Billing & Finance (Weeks 8–9)

| Task | Owner | Description |
|------|-------|-------------|
| Automatic Charging | Backend | Services automatically charge patients |
| Invoice Generation | Full‑stack | Grouped by category; professional PDF |
| Payment Recording | Full‑stack | Cash, bank, card, M‑Pesa |
| Receipt Generation | Full‑stack | Professional PDF receipt |
| Sponsorship Management | Full‑stack | Sponsor profiles, invoices, statements |
| Outstanding Balances | Backend | Track and display outstanding amounts |

**Deliverables:**
- Invoices generated correctly (grouped by drug, not per dose).
- Payments recorded and receipts generated.
- Sponsor statements available.

---

#### Sprint 6: Discharge & Reports (Weeks 9–10)

| Task | Owner | Description |
|------|-------|-------------|
| Discharge Workflow | Full‑stack | Clinical summary, pharmacy/billing/finance confirmation |
| Balance Check | Backend | Block discharge if balance > 0 |
| Force Discharge | Full‑stack | Admin override with reason and password |
| Discharged Patients | Frontend | Dedicated section, read‑only records |
| Core Reports | Full‑stack | Admissions, discharges, patient census, bed occupancy |
| Dashboard | Frontend | Real‑time stats, alerts, charts |

**Deliverables:**
- Discharge workflow working (with balance check).
- Force discharge working for admins.
- Discharged patients list accessible.
- Core reports generated.
- Dashboard showing key metrics.

---

### Phase 2: Extended Features (Weeks 11–16)

**Goal:** Add missing modules and enhance the platform.

| Module | Priority | Description |
|--------|----------|-------------|
| **Laboratory** | High | Test requests, sample collection, results entry |
| **Medical Consumables** | High | Inventory and dispensing of consumables |
| **Advanced Reporting** | Medium | Additional report types (financial, pharmacy, etc.) |
| **Mobile Optimisation** | High | Ensure all screens work perfectly on mobile |
| **Notifications (Email/SMS)** | High | In‑app, email, and SMS notifications |
| **M‑Pesa Integration** | Medium | Payment gateway integration |

---

### Phase 3: Scaling & Advanced Features (Weeks 17–24)

| Module | Priority | Description |
|--------|----------|-------------|
| **AI‑Powered Insights** | Low | Predictive analytics, relapse risk, outcome prediction |
| **Telehealth Integration** | Low | Video consultations |
| **Mobile Application** | Medium | Native mobile app (Android/iOS) |
| **HL7/FHIR Integration** | Low | Interoperability with other healthcare systems |
| **Multi‑Tenant Scaling** | High | Performance optimisation, horizontal scaling |
| **Advanced Analytics** | Medium | Custom dashboards, data visualisation |

---

## 5. Milestones & Timeline

| Milestone | Target Date | Deliverable |
|-----------|-------------|-------------|
| **M0: Documentation Complete** | Week 2 | All six documents approved |
| **M1: MVP Alpha** | Week 6 | Core features working (auth, patients, vitals) |
| **M2: MVP Beta** | Week 8 | Pharmacy, MAR, billing working |
| **M3: MVP Release** | Week 10 | Discharge, reports, dashboard working; ready for Serenity Place |
| **M4: Phase 2** | Week 16 | Laboratory, consumables, notifications |
| **M5: Production Scale** | Week 24 | Scaling, performance optimisation, advanced features |

---

## 6. Sprint Cadence

- **Sprint Length:** 2 weeks
- **Planning:** Monday of Week 1
- **Review:** Friday of Week 2
- **Retrospective:** Friday of Week 2
- **Stand‑up:** Daily (15 minutes)

### Sprint Structure

| Day | Activity |
|-----|----------|
| Monday | Sprint planning (2 hours) |
| Tuesday–Thursday | Development + daily stand‑up |
| Friday (Week 1) | Check‑in + progress review |
| Monday–Thursday (Week 2) | Development + daily stand‑up |
| Friday (Week 2) | Sprint review + retrospective |

---

## 7. Development Workflow

### Git Workflow

main (production)
└── develop (integration)
├── feature/xxx (new features)
├── bugfix/xxx (bug fixes)
└── release/xxx (release preparation)
text


**Branch Naming:**
- `feature/patient-registration`
- `bugfix/vitals-error`
- `release/v1.0.0`

**PR Process:**
1. Create branch from `develop`.
2. Write code + tests.
3. Create Pull Request to `develop`.
4. CI runs tests, linters, security scans.
5. At least one reviewer approves.
6. Merge to `develop`.
7. Deploy to staging.
8. Release to `main` (production) on approval.

---

## 8. Testing Strategy

| Test Level | Scope | Frequency | Tools |
|------------|-------|-----------|-------|
| **Unit Tests** | Models, serializers, business logic | Every PR | Django Test, pytest |
| **Integration Tests** | API endpoints, database interactions | Every PR | pytest‑django, DRF test client |
| **E2E Tests** | Critical user journeys | Daily | Playwright / Cypress |
| **Security Tests** | OWASP top 10 | Weekly | Bandit, OWASP ZAP |
| **Performance Tests** | API response times, DB queries | Monthly | Locust, Django Debug Toolbar |
| **User Acceptance (UAT)** | Real user workflows | End of each sprint | Product owners + test users |

**Goal:** 80%+ test coverage for business‑critical modules.

---

## 9. Deployment Strategy

### Environments

| Environment | Purpose | Access |
|-------------|---------|--------|
| **Development** | Local development | Developers only |
| **Staging** | Integration and UAT | Team + testers |
| **Production** | Live system | Customers |

### Deployment Frequency

| Environment | Frequency | Trigger |
|-------------|-----------|---------|
| **Staging** | Daily | Automatic on PR merge |
| **Production** | Weekly | Manual approval |

### Rollback Plan

- Rollback via GitHub revert + re‑deploy previous Docker image.
- Database rollback requires backup restoration (RPO: 15 minutes).

---

## 10. Risk Register

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| **Key developer leaves** | Medium | High | Cross‑training; good documentation |
| **Scope creep** | High | Medium | Strict MVP scope; product owner approval for changes |
| **Integration failure (M‑Pesa)** | Medium | High | Fallback to manual payments; test integration early |
| **Performance issues** | Medium | High | Load test early; scale horizontally |
| **Security breach** | Low | Catastrophic | Zero trust; security audits; encryption |
| **Customer adoption** | Medium | High | Early customer involvement (Serenity Place) |

---

## 11. Success Criteria for MVP

| Metric | Target |
|--------|--------|
| **System uptime** | 99.9% |
| **API response time** | < 500ms (95% of requests) |
| **Patient registration time** | < 3 minutes |
| **Vitals recording success** | 100% |
| **Invoice generation** | Correct grouping; zero errors |
| **User satisfaction** | > 80% (post‑MVP survey) |
| **Bugs** | 0 critical bugs; < 10 high‑priority bugs |
| **Test coverage** | > 80% for critical modules |

---

## 12. Tools & Software

| Category | Tool |
|----------|------|
| **Version Control** | GitHub |
| **Project Management** | GitHub Projects / Linear / Trello |
| **Documentation** | GitHub Wiki / Notion |
| **CI/CD** | GitHub Actions |
| **Monitoring** | Prometheus + Grafana + Loki + Sentry |
| **Testing** | pytest, Playwright, Bandit |
| **Development Environment** | Docker + Docker Compose |
| **Design** | Figma |

---

## 13. Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | 2026-07-11 | CTO | Initial draft. |

---

**Status:** DRAFT – Ready for review by Product Owners and technical team.

