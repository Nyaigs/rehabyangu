# RehabYangu – Product Requirements Document (PRD)

**Version:** 0.1  
**Owner:** CTO / Product Owner  
**Status:** Draft  
**Last Updated:** 2026-07-11  


## 1. Executive Summary

RehabYangu is a **multi-tenant, white-label SaaS platform** designed for rehabilitation centres, psychiatric hospitals, addiction treatment facilities, and mental health organisations across Africa. It provides a complete digital operating system for behavioural healthcare – managing patients, clinical documentation, pharmacy, billing, sponsors, inventory, reporting, and compliance.

The platform is built for **scale**, **security**, and **customisation**. Each facility (tenant) experiences a fully branded system with their own logo, name, colours, and document templates – while sharing a unified, secure, multi-tenant backend.

**Target Launch Customer:** Serenity Place Treatment Center (Kenya).  
**Long-term Vision:** Pan-African expansion.


## 2. Product Vision

> *"To become the most trusted behavioural healthcare management platform in Africa, enabling rehabilitation centres to provide safer, more efficient, and more connected patient care."*

### Core Principles

| Principle | Description |
|-----------|-------------|
| **Security First** | Zero-trust architecture, encryption at rest and in transit, immutable audit logs. |
| **Patient Privacy** | Strict access controls; only authorised personnel can view patient data. |
| **Multi-Tenant by Design** | Each facility is isolated; no cross-tenant data leakage. |
| **White-Label Ready** | Each tenant controls their own branding (logo, name, colours, documents). |
| **Configurable** | Tenants can customise roles, permissions, pricing, and workflows. |
| **Scalable** | Designed to support hundreds of facilities and tens of thousands of patients. |
| **API-First** | All functionality exposed via RESTful APIs for future integrations. |

---

## 3. Target Users & Personas

### Primary Customers
- Rehabilitation centres
- Addiction treatment facilities
- Psychiatric hospitals
- Mental health clinics
- Recovery organisations

### User Personas (Within Each Tenant)
- **Super Administrator** – Full system control, tenant configuration, user management.
- **Director** – Oversight of clinical and operational performance.
- **Psychiatrist** – Psychiatric reviews, medication management, clinical documentation.
- **Clinical Officer** – Daily clinical reviews, treatment plans.
- **Nurse** – Vitals, medication administration, nursing notes, MAR.
- **Counselor** – Therapy sessions, progress notes, group therapy.
- **Pharmacist** – Inventory management, dispensing, expiry alerts.
- **Laboratory Technologist** – Test requests, sample collection, results entry.
- **Accountant** – Billing, invoicing, payments, financial reporting.
- **Receptionist** – Patient registration, admissions, appointments.
- **Store Manager** – Consumables inventory, stock tracking.
- **Cook** – Dietary planning, meal counts (anonymised patient data).
- **Sponsor** (external) – View statements, payment history, outstanding balances.

---

## 4. Core Modules & Features

Below is the complete feature set for RehabYangu. Features marked **MVP** are part of the initial release. Features marked **Phase 2/3** will be delivered in subsequent releases.

### 4.1 Authentication & Security (MVP)

| Feature | Description | Multi-Tenant? | Configurable? |
|---------|-------------|---------------|---------------|
| User Registration | Self-registration with admin approval workflow. | Yes (per tenant) | No |
| Login | Email + password with JWT authentication. | Yes | No |
| Password Reset | Email-based password reset. | Yes | No |
| MFA (Optional) | Multi-factor authentication (later phase). | Yes | Tenant can enable/disable |
| Role-Based Access Control (RBAC) | Granular permissions per role. | Yes | **Yes** – admins can create custom roles |
| Session Management | Auto-logout after 10 minutes inactivity (warning at 9 min). | Yes | **Yes** – configurable timeout |
| Audit Trail | Immutable log of all sensitive actions. | Yes | No |

### 4.2 User Management (MVP)

| Feature | Description | Multi-Tenant? | Configurable? |
|---------|-------------|---------------|---------------|
| Staff Accounts | Create, edit, deactivate users. | Yes | No |
| Roles & Permissions | Pre-defined roles + custom role creation. | Yes | **Yes** – admins can define new roles |
| Activity Logs | View user actions. | Yes | No |
| Pending Approvals | Admin dashboard shows new registrations. | Yes | No |

### 4.3 Patient Management (MVP)

| Feature | Description | Multi-Tenant? | Configurable? |
|---------|-------------|---------------|---------------|
| Patient Registration | Full demographics, photo upload, emergency contacts, sponsor info, insurance. | Yes | No |
| Patient Search | Search by name, admission number, phone, ID. | Yes | No |
| Patient Photo | Upload and display patient photo. | Yes | No |
| Admission | Auto-generated admission number (ADM-YYYY-XXXX). Ward and bed allocation. | Yes | No |
| Transfer | Transfer between wards with audit trail. | Yes | No |
| Discharge | Full discharge workflow with balance check (see Section 5). | Yes | **Yes** – force discharge permission configurable |
| Discharged Patients | Dedicated section; read-only records. | Yes | No |

### 4.4 Electronic Medical Record (EMR) (MVP)

| Feature | Description | Multi-Tenant? | Configurable? |
|---------|-------------|---------------|---------------|
| Clinical Notes | Free-text clinical documentation. | Yes | No |
| Mental State Examination (MSE) | Structured template. | Yes | **Yes** – templates can be customised |
| DSM-5 / ICD-10 Diagnoses | Multiple diagnoses supported. | Yes | **Yes** – diagnosis lists can be updated |
| Nursing Notes | Chronological nursing documentation. | Yes | No |
| Progress Notes | Clinical and counseling progress. | Yes | No |
| Treatment Plans | Goals, timelines, interventions. | Yes | **Yes** – customisable templates |
| Care Plans | Structured care planning. | Yes | **Yes** – customisable |
| Risk Assessments | Suicide, violence, and general risk. | Yes | **Yes** – assessment tools can be added |
| Attachments | Upload documents (PDFs, images). | Yes | No |

### 4.5 Vitals Module (MVP – Critical)

| Feature | Description | Multi-Tenant? | Configurable? |
|---------|-------------|---------------|---------------|
| Record Vitals | BP, HR, RR, Temp, SpO2, Blood Sugar, Pain Score. | Yes | No |
| Vitals History | Chronological table with trends. | Yes | No |
| Vitals Trends | Line charts (BP, HR, Temp, SpO2). | Yes | No |
| Abnormal Alerts | Highlight values outside normal ranges. | Yes | **Yes** – thresholds configurable |
| Edit Restriction | Vitals cannot be edited after 24 hours. | Yes | No |

### 4.6 Pharmacy Management (MVP)

| Feature | Description | Multi-Tenant? | Configurable? |
|---------|-------------|---------------|---------------|
| Drug Inventory | Name, generic, strength, form, batch, supplier, price, stock, expiry. | Yes | No |
| Stock Management | Add, update, deduct stock. | Yes | No |
| Dispensing | Dispense to patients with dosage-form validation (whole numbers vs decimals). | Yes | No |
| Low Stock Alerts | Notify when stock below minimum. | Yes | **Yes** – threshold configurable |
| Expiry Alerts | Notify when drugs expire within 30/60/90 days. | Yes | **Yes** – configurable |
| Medication Cost Tracking | Record cost per unit. | Yes | No |
| Medication Charges | Automatically add to patient bill. | Yes | No |

### 4.7 Medication Administration Record (MAR) (MVP)

| Feature | Description | Multi-Tenant? | Configurable? |
|---------|-------------|---------------|---------------|
| MAR Entry | Medication name, dose, route, frequency, time, status (Given/Missed/Refused/Held). | Yes | No |
| MAR Print | Print MAR for a patient per day. | Yes | **Yes** – template configurable |
| Nurse Attribution | Each administration recorded by nurse. | Yes | No |

### 4.8 Medical Consumables (Phase 2)

| Feature | Description | Multi-Tenant? | Configurable? |
|---------|-------------|---------------|---------------|
| Consumables Inventory | Track gloves, syringes, dressings, IV fluids, etc. | Yes | No |
| Consumables Dispensing | Record usage during procedures. | Yes | No |
| Cost Tracking | Automatically charge to patient. | Yes | No |
| Low Stock Alerts | Notify when stock below minimum. | Yes | **Yes** – threshold configurable |

### 4.9 Psychiatric Module (MVP)

| Feature | Description | Multi-Tenant? | Configurable? |
|---------|-------------|---------------|---------------|
| Psychiatric Reviews | Diagnosis update, MSE, medication changes, recommendations. | Yes | No |
| Appointments | Schedule and manage psychiatric appointments. | Yes | No |
| Review Limits | 2 reviews included per month; additional reviews automatically charged. | Yes | **Yes** – package limits configurable |
| Upcoming Reviews Dashboard | Widget showing reviews due in next 7 days. | Yes | No |

### 4.10 Counseling Module (MVP)

| Feature | Description | Multi-Tenant? | Configurable? |
|---------|-------------|---------------|---------------|
| Individual Therapy | Session notes, attendance. | Yes | No |
| Group Therapy | Track group sessions, attendance, notes. | Yes | No |
| Family Therapy | Family session documentation. | Yes | No |
| Psychoeducation | Educational session tracking. | Yes | No |
| Relapse Prevention | Session notes and planning. | Yes | No |
| Weekly Session Count | Track number of sessions per counselor/patient. | Yes | No |
| Progress Evaluation | Evaluate patient progress toward goals. | Yes | No |

### 4.11 Nursing Module (MVP)

| Feature | Description | Multi-Tenant? | Configurable? |
|---------|-------------|---------------|---------------|
| Nursing Notes (SOAP) | Subjective, Objective, Assessment, Plan. | Yes | No |
| Care Plans | Nursing care planning. | Yes | **Yes** – templates configurable |
| Shift Handover | Structured handover notes. | Yes | **Yes** – template configurable |
| Incident Reports | Record and track incidents. | Yes | No |

### 4.12 Laboratory Module (Phase 2)

| Feature | Description | Multi-Tenant? | Configurable? |
|---------|-------------|---------------|---------------|
| Test Requests | Doctor requests tests for patient. | Yes | No |
| Sample Collection | Record collection details. | Yes | No |
| Results Entry | Lab technologist enters results. | Yes | No |
| Abnormal Results | Highlight abnormal values. | Yes | **Yes** – reference ranges configurable |
| Downloadable Reports | PDF test reports. | Yes | **Yes** – template configurable |

### 4.13 Billing & Finance (MVP – Critical)

| Feature | Description | Multi-Tenant? | Configurable? |
|---------|-------------|---------------|---------------|
| Automatic Charging | All billable services automatically charged to patient account. | Yes | **Yes** – charges and prices configurable |
| Payment Methods | Cash, Bank Transfer, Card, M-Pesa. | Yes | **Yes** – enable/disable methods |
| Invoice Generation | Grouped by category (not per dose). Professional layout. | Yes | **Yes** – template, branding, letterhead |
| Receipt Generation | Professional receipt with transaction reference. | Yes | **Yes** – template, branding |
| Sponsor Statements | Statement of charges and payments. | Yes | **Yes** – template, branding |
| Outstanding Balances | Display clearly; block discharge if balance > 0. | Yes | No |
| Force Discharge | Admin/Director override with reason and password. | Yes | **Yes** – permission configurable |

### 4.14 Sponsorship Management (MVP)

| Feature | Description | Multi-Tenant? | Configurable? |
|---------|-------------|---------------|---------------|
| Sponsor Profiles | Name, contact, payment responsibility. | Yes | No |
| Patient-Sponsor Relationship | Link patients to sponsors. | Yes | No |
| Sponsor Invoices | Generate invoices for sponsors. | Yes | **Yes** – template, branding |
| Sponsor Statements | View all charges and payments. | Yes | **Yes** – template, branding |
| Payment Tracking | Track sponsor payments. | Yes | No |
| Outstanding Balances | Show per sponsor and per patient. | Yes | No |

### 4.15 Inventory & Stores (Phase 2)

| Feature | Description | Multi-Tenant? | Configurable? |
|---------|-------------|---------------|---------------|
| Stock Management | Medical, cleaning, office, and food supplies. | Yes | No |
| Purchase Orders | Generate and track purchase orders. | Yes | No |
| Supplier Records | Manage suppliers. | Yes | No |
| Stock Reports | Downloadable stock reports. | Yes | **Yes** – template, branding |

### 4.16 Human Resources (Phase 3)

| Feature | Description | Multi-Tenant? | Configurable? |
|---------|-------------|---------------|---------------|
| Staff Records | Employee profiles with photos. | Yes | No |
| Attendance | Staff attendance tracking. | Yes | No |
| Leave Management | Leave requests and approvals. | Yes | No |
| Payroll Preparation | Generate payroll reports. | Yes | **Yes** – configurable | 
| Performance Reviews | Staff performance evaluation. | Yes | **Yes** – template configurable |

### 4.17 Reports (MVP – Core)

| Report Type | Format | Description | Multi-Tenant? | Configurable? |
|-------------|--------|-------------|---------------|---------------|
| Admissions Report | PDF, Word, Excel | Admissions by date range. | Yes | **Yes** – filters, branding |
| Discharges Report | PDF, Word, Excel | Discharges by date range. | Yes | **Yes** – filters, branding |
| Patient Census | PDF, Excel | Current inpatients. | Yes | **Yes** – branding |
| Bed Occupancy | PDF, Excel | Occupancy by ward. | Yes | **Yes** – branding |
| Medication Usage | PDF, Excel | Medication usage by drug. | Yes | **Yes** – filters, branding |
| Pharmacy Sales | PDF, Excel | Revenue from pharmacy. | Yes | **Yes** – filters, branding |
| Financial Reports | PDF, Excel | Revenue, expenses, outstanding. | Yes | **Yes** – filters, branding |
| Outstanding Balances | PDF, Excel | All outstanding patient balances. | Yes | **Yes** – filters, branding |
| Sponsor Statements | PDF, Word | Per sponsor statement. | Yes | **Yes** – template, branding |
| Expiring Drugs Report | PDF, Excel | Drugs expiring within 30/60/90 days. | Yes | **Yes** – filters, branding |
| Audit Logs | PDF, Excel | All user actions. | Yes | **Yes** – filters |

### 4.18 Document Generation (MVP – Core)

| Document Type | Format | Description | Multi-Tenant? | Configurable? |
|---------------|--------|-------------|---------------|---------------|
| Admission Forms | PDF, Word | Pre-filled with patient data. | Yes | **Yes** – template, branding |
| Consent Forms | PDF, Word | Upload or generate. | Yes | **Yes** – template, branding |
| Treatment Plans | PDF, Word | Clinical treatment plan. | Yes | **Yes** – template, branding |
| Progress Reports | PDF, Word | Clinical progress summary. | Yes | **Yes** – template, branding |
| Medical Summaries | PDF, Word | Patient medical summary. | Yes | **Yes** – template, branding |
| Discharge Summaries | PDF, Word | Complete discharge summary. | Yes | **Yes** – template, branding |
| Referral Letters | PDF, Word | Referral to other facilities. | Yes | **Yes** – template, branding |
| Medical Certificates | PDF, Word | Sick notes/certificates. | Yes | **Yes** – template, branding |
| Invoices | PDF, Word | Professional invoice with grouping. | Yes | **Yes** – template, branding |
| Receipts | PDF, Word | Payment receipt. | Yes | **Yes** – template, branding |
| Sponsor Statements | PDF, Word | Sponsor statement. | Yes | **Yes** – template, branding |

### 4.19 Notifications (MVP – Core)

| Notification Type | Channels | Description | Multi-Tenant? | Configurable? |
|-------------------|----------|-------------|---------------|---------------|
| New User Registration | In-app, Email | Notify admins of pending approval. | Yes | No |
| Account Approval | Email | Notify user of approval. | Yes | **Yes** – email template |
| Low Stock Alert | In-app, Email | Notify pharmacist/store manager. | Yes | **Yes** – threshold configurable |
| Expiring Drugs | In-app, Email | Notify pharmacist. | Yes | **Yes** – threshold configurable |
| Missed Medication | In-app, Email | Notify nurse and doctor. | Yes | No |
| Upcoming Reviews | In-app | Notify psychiatrist. | Yes | **Yes** – configurable | 
| Upcoming Discharges | In-app | Notify doctor and billing. | Yes | No |
| Outstanding Bills | In-app | Notify accountant. | Yes | No |
| New Admission | In-app | Notify relevant staff. | Yes | **Yes** – configurable |

### 4.20 Analytics & Dashboards (MVP – Core)

| Dashboard | Description | Multi-Tenant? | Configurable? |
|-----------|-------------|---------------|---------------|
| Dashboard Overview | Real-time stats: admissions, occupancy, revenue, alerts. | Yes | No |
| Admissions Trends | Line chart of admissions over time. | Yes | No |
| Bed Occupancy | Current occupancy percentage and trends. | Yes | No |
| Revenue Charts | Monthly revenue bar chart. | Yes | **Yes** – date filters |
| Outstanding Balances | Total outstanding. | Yes | No |
| Medication Costs | Cost tracking. | Yes | No |
| Recovery Outcomes | Treatment outcome analytics. | Yes | **Yes** – configurable |
| Length of Stay | Average stay analysis. | Yes | **Yes** – configurable |

### 4.21 System Settings (MVP – Critical)

| Setting | Description | Multi-Tenant? | Configurable? |
|---------|-------------|---------------|---------------|
| Facility Information | Name, address, logo, contacts. | Yes | **Yes** – per tenant |
| Branding | Logo upload, primary colour, document letterheads. | Yes | **Yes** – per tenant |
| Package Pricing | Rehabilitation package rates. | Yes | **Yes** – per tenant |
| Medication Pricing | Markup percentage or fixed price. | Yes | **Yes** – per tenant |
| Consumable Pricing | Price per unit. | Yes | **Yes** – per tenant |
| Role & Permissions | Create/edit roles. | Yes | **Yes** – per tenant |
| Invoice Templates | Customisable template. | Yes | **Yes** – per tenant |
| Receipt Templates | Customisable template. | Yes | **Yes** – per tenant |
| Notification Settings | Enable/disable notifications. | Yes | **Yes** – per tenant |
| Backup Schedule | Automatic backup frequency. | Yes | **Yes** – per tenant |

---

## 5. Critical Business Rules (Non‑Negotiable)

### 5.1 Discharge Rules

1. **Standard Discharge:** When a user clicks "Discharge" on a patient, the system **MUST** check the patient's outstanding balance.
2. If **balance > 0**, the system **MUST** show a warning popup:  
   *"This patient has an outstanding balance of KES [amount]. Discharge cannot proceed until the balance is cleared."*  
   The Discharge button is greyed out/blocked.
3. **Force Discharge:** Only visible to users with **Admin or Director** roles.
   - Requires a mandatory **reason** field.
   - Requires **admin password confirmation**.
   - Creates an **audit log entry** recording who authorised it, when, and why.
4. **Discharged Patients Section:**
   - Show all discharged patients with discharge date.
   - Outstanding balances displayed clearly in **red** if > 0.
   - Filters: Discharge Date Range, Balance Status (Cleared/Pending), Ward.
   - Click to view patient record in **read-only** mode.
5. Discharged patients **MUST NOT** appear in:
   - Main patient list / active inpatients
   - Bed occupancy counts
   - Active admissions
   - Medication administration lists

### 5.2 Discharge Workflow Steps

1. **Step 1:** Doctor initiates discharge with clinical summary.
2. **Step 2:** Pharmacy confirms no pending medications to dispense.
3. **Step 3:** Billing confirms all charges are captured.
4. **Step 4:** Finance confirms balance clearance or flags outstanding amount.
5. **Step 5:** Final discharge approved; patient moved to discharged list.

### 5.3 Medication Quantity Rules

Based on **dosage form**:

| Dosage Form | Quantity Allowed | Example |
|-------------|------------------|---------|
| Tablet / Capsule | **Whole numbers ONLY** | 1, 2, 15 (NOT 1.05 or 2.5) |
| Syrup / Suspension | **1 decimal place** | 5.0 ml, 7.5 ml |
| Injection | **1 decimal place** | 2.5 ml |
| IV Fluid | **1 decimal place** | 500.0 ml |
| Cream / Ointment | **1 decimal place** | 2.5 g |
| Inhaler | **Whole numbers** | 2 puffs |
| Drops | **Whole numbers** | 5 drops |

**Validation:**
- If dosage form is Tablet/Capsule and user enters a decimal, show error:  
  *"Tablets must be dispensed in whole numbers. Please enter a whole number."*
- Input field automatically restricts decimals based on dosage form.

### 5.4 Invoice Grouping Rules

Invoices **MUST** group charges properly – **NOT** list every single dose separately.

**Correct Grouping:**

Medication Charges:

    Paracetamol 500mg Tablet | KES 10 | 15 tablets | KES 150

    Amoxicillin 250mg Capsule | KES 8 | 20 capsules | KES 160
    Subtotal: KES 310

Consumables:

    Syringe 5ml | KES 5 | 3 units | KES 15
    Subtotal: KES 15

Accommodation:

    Ward Charges (7 days) | KES 5,000/day | KES 35,000
    Subtotal: KES 35,000

Total: KES 35,325
text


**Incorrect (do NOT do this):**

Paracetamol 500mg - Day 1 | KES 10
Paracetamol 500mg - Day 2 | KES 10
Paracetamol 500mg - Day 3 | KES 10
... (15 lines for one drug)
text


### 5.5 Vitals Recording Rules

- **Nurse selects patient** → enters vitals.
- After **SAVE**: show success message *"Vital signs recorded successfully"*.
- **IMMEDIATELY display** recorded vitals on the same screen.
- Vitals appear in patient's vitals history.
- **Vitals Trends** with line charts.
- **Abnormal values highlighted in RED**:
  - BP > 140/90 or < 90/60
  - HR > 100 or < 60
  - Temp > 37.5°C
  - SpO2 < 95%
- Vitals visible to: Nurses, Clinical Officers, Psychiatrists, Directors, Super Admins.
- Vitals **NOT editable** after 24 hours (audit compliance).

---

## 6. Non‑Functional Requirements

| Category | Requirement |
|----------|-------------|
| **Performance** | Page load < 3 seconds; API response < 500ms for 95% of requests. |
| **Scalability** | Support 100+ tenants and 10,000+ concurrent users. |
| **Availability** | 99.9% uptime (SLA). |
| **Security** | Zero-trust architecture; encryption at rest and in transit; immutable audit logs. |
| **Backup** | Daily automated backups; point-in-time recovery. |
| **Disaster Recovery** | RPO: 15 minutes; RTO: 2 hours. |
| **Compliance** | Kenya Data Protection Act; ISO 27001 (future). |
| **Accessibility** | WCAG 2.1 Level AA compliant. |
| **Responsiveness** | Fully functional on desktop, tablet, and mobile. |
| **Internationalisation** | Support for English and Swahili (future). |

---

## 7. MVP Scope (Minimum Viable Product)

For the **initial launch at Serenity Place**, the MVP will include:

### ✅ MVP Core (Must Have)

- Authentication (registration, login, password reset, admin approval workflow)
- User Management (roles, permissions, activity logs)
- Patient Registration & Admission
- Electronic Medical Record (basic: clinical notes, MSE, diagnoses, treatment plans)
- Vitals Module (recording, history, trends, abnormal alerts)
- Nursing Module (SOAP notes, care plans)
- Pharmacy Management (inventory, dispensing, stock alerts, expiry alerts)
- MAR (Medication Administration Record)
- Billing & Finance (automatic charging, invoicing with grouping, receipts, payments)
- Sponsorship Management (sponsor profiles, statements)
- Discharge Workflow (with balance check and force discharge for admins)
- Discharged Patients (read-only records)
- Dashboard (key statistics, alerts, charts)
- Reports (admissions, discharges, patient census, bed occupancy, financial)
- Document Generation (invoices, receipts, admission forms, discharge summaries)
- Notifications (email + in-app for key alerts)
- White‑labelling (facility name, logo, colours, document templates)
- Multi‑tenant Isolation (schema‑per‑tenant)
- System Settings (facility info, branding, pricing, templates)

### ⏳ Phase 2 (Extended)

- Laboratory Module
- Medical Consumables (full inventory + dispensing)
- Advanced Reporting (more report types)
- Analytics (additional dashboards)
- Inventory & Stores (full supply chain)
- Telehealth integration (future)

### ⏳ Phase 3 (Advanced)

- AI‑powered insights
- Predictive analytics
- Mobile application
- Advanced integrations (HL7/FHIR, government systems)

---

## 8. Licensing & Subscription

### 8.1 Subscription Tiers (Recommended)

| Tier | Price (KES / Month) | Features |
|------|---------------------|----------|
| **Starter** | 10,000 – 20,000 | Core registration, admission, billing, basic reports |
| **Professional** | 30,000 – 50,000 | + EMR, nursing, pharmacy, MAR, counseling |
| **Enterprise** | 80,000 – 130,000 | + All modules, API access, dedicated support |
| **Custom** | Custom | White‑labeled, on‑premise option, custom integrations |

*(Prices to be validated with market research)*

### 8.2 Subscription States

| State | Description |
|-------|-------------|
| **ACTIVE** | Full access |
| **TRIAL** | 30‑day trial with full features |
| **EXPIRED** | Access revoked; data preserved for 30 days |
| **SUSPENDED** | Temporary suspension (non‑payment) |
| **READ_ONLY** | Can view data but not create/modify |

### 8.3 Non‑Payment Handling

1. Send payment reminders (Day 1, 7, 14 after expiry).
2. Grace period: 15 days.
3. After grace period: move to **READ_ONLY** mode.
4. After 30 days: move to **SUSPENDED**.
5. Data retained for 90 days after suspension; then archived.
6. Healthcare data remains protected; facility can export data at any time.

---

## 9. White‑Label Requirements

Each tenant must be able to:

| Customisation | Method |
|---------------|--------|
| **Facility Name** | Input field in Settings |
| **Logo** | Upload PNG (system auto‑resizes to multiple sizes) |
| **Primary Colour** | Colour picker (default: blue) |
| **Letterhead** | Facility name, address, contacts on all documents |
| **Invoice Template** | Customisable template |
| **Receipt Template** | Customisable template |
| **Email Branding** | Logo + facility name in all email notifications |
| **Browser Tab** | Favicon + page title set to facility name |

**Default:** If tenant has not customised, the system shows "RehabYangu" and our logo.

---

## 10. Success Criteria

| Metric | Target |
|--------|--------|
| Number of tenants (Year 1) | 5–10 |
| Number of tenants (Year 3) | 100+ |
| Patient records (per tenant) | 500+ |
| System uptime | 99.9% |
| User satisfaction | > 90% (post‑launch survey) |
| Time to onboard new tenant | < 1 hour (automated) |
| Revenue | Monthly recurring revenue > KES 1M by Year 2 |

---

## 11. Assumptions & Constraints

| Assumption | Impact |
|------------|--------|
| Internet connectivity is available at facilities. | We must support offline mode (future). |
| Users have basic computer literacy. | Training will be required. |
| M‑Pesa integration is available. | Payment flow depends on M‑Pesa API. |
| English is the primary language. | Swahili support will be added later. |
| Data protection laws apply. | We must comply with Kenya Data Protection Act. |

---

## 12. Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Data breach | Medium | Catastrophic | Zero trust; regular security audits |
| User adoption | Medium | High | Strong UX; comprehensive training |
| Regulatory changes | Low | High | Flexible architecture; legal advisor |
| M‑Pesa integration failure | Medium | High | Backup payment methods (bank, cash) |
| Performance issues | Medium | High | Load testing; scalable architecture |
| Technical debt | High | Medium | Code reviews; refactoring sprints |

---

## 13. Review Checklist

- [ ] Executive Summary reviewed
- [ ] Product Vision aligned with founders' goals
- [ ] Target users and personas validated
- [ ] All core modules listed and prioritised
- [ ] Critical business rules (discharge, billing, vitals) verified
- [ ] MVP scope clearly defined
- [ ] White‑labelling requirements understood
- [ ] Licensing and subscription model approved
- [ ] Success criteria agreed
- [ ] Risks and mitigations reviewed

---

## 14. Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | 2026-07-11 | CTO | Initial draft from Serenity Place prompt + RehabYangu vision |

---

**Status:** DRAFT – Awaiting review and approval by Product Owners (Brian & Nyaigotti).
