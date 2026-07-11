# RehabYangu – User Journey & Workflow Document
**Version:** 0.1  
**Owner:** UX Lead  
**Status:** On Reviea  
**Last Updated:** 2026-07-11  

## 1. Purpose
This document describes how different users interact with RehabYangu. It defines:

- User personas and their goals.
- Step‑by‑step journeys for key tasks.
- Workflow diagrams (text‑based) for clinical, administrative, and financial processes.
- Role‑based access and screen transitions.
- Error scenarios and how the system responds.

This document serves as the bridge between the Product Requirements (PRD) and the UI/UX Design.

## 2. User Personas
### 2.1 Super Administrator
- **Role:** Tenant owner or IT manager.
- **Goals:** Configure tenant settings, manage users, oversee system health.
- **Key Tasks:** Approve new user registrations, create roles, set pricing, manage branding.

### 2.2 Director
- **Role:** Facility director / clinical lead.
- **Goals:** Oversee operations, monitor patient outcomes, manage staff.
- **Key Tasks:** View dashboards, approve force discharges, review clinical reports.

### 2.3 Psychiatrist
- **Role:** Medical doctor specialising in mental health.
- **Goals:** Conduct psychiatric reviews, prescribe medications, update treatment plans.
- **Key Tasks:** Schedule appointments, record MSE, adjust medications, document clinical findings.

### 2.4 Clinical Officer
- **Role:** General practitioner or clinical officer.
- **Goals:** Daily patient reviews, manage chronic conditions, coordinate care.
- **Key Tasks:** Record daily progress notes, order lab tests, initiate discharges.

### 2.5 Nurse
- **Role:** Registered nurse or psychiatric nurse.
- **Goals:** Monitor patients, administer medication, document nursing care.
- **Key Tasks:** Record vitals, administer medications via MAR, write SOAP notes, shift handover.

### 2.6 Counselor
- **Role:** Mental health counselor.
- **Goals:** Conduct therapy sessions, track patient progress.
- **Key Tasks:** Schedule individual/group sessions, write progress notes, evaluate treatment goals.

### 2.7 Pharmacist
- **Role:** Pharmacy manager.
- **Goals:** Manage drug inventory, dispense medications, ensure safety.
- **Key Tasks:** Add/update stock, dispense to patients, monitor expiry, generate stock reports.

### 2.8 Laboratory Technologist
- **Role:** Lab technician.
- **Goals:** Process lab requests and tests, enter results.
- **Key Tasks:** Receive test orders, collect samples, enter results, flag abnormal values.

### 2.9 Accountant
- **Role:** Finance officer.
- **Goals:** Manage billing, invoicing, and payments.
- **Key Tasks:** Generate invoices, record payments, track outstanding balances, sponsor statements.

### 2.10 Receptionist
- **Role:** Front‑office staff.
- **Goals:** Register patients, handle admissions, manage appointments.
- **Key Tasks:** Register new patients, admit patients, search patients, update demographics.

### 2.11 Store Manager
- **Role:** Supplies manager.
- **Goals:** Manage consumables inventory.
- **Key Tasks:** Add stock, issue items, generate purchase orders.

### 2.12 Cook
- **Role:** Kitchen staff.
- **Goals:** Plan meals based on patient dietary needs (anonymised).
- **Key Tasks:** View dietary requirements, see patient counts (names hidden).

### 2.13 Sponsor (External)
- **Role:** Individual or organisation paying for patient treatment.
- **Goals:** View statements, make payments, see outstanding balances.
- **Key Tasks:** Login (limited access) or access info through whatsapp, view sponsor‑specific dashboard, download statements.

## 3. User Journeys (Core Workflows)
### 3.1 Patient Registration & Admission
**Actor:** Receptionist

**Pre‑condition:** Patient arrives at the facility.

**Steps:**
1. Receptionist logs in and navigates to **Patient Management → Register Patient**.
2. Fills in demographics:
   - Full name, DOB, gender, national ID.
   - Contact details (phone, email, address).
   - Emergency contact and next of kin.
   - Sponsor information (if any).
   - Insurance details (if applicable).
   - Referral source.
   - Uploads patient photo (optional).
3. Clicks **Save** → patient is created with a unique patient ID.
4. System shows success message and offers: **Admit this patient** or **Go to patient list**.

**Admission Steps (immediate or later):**
1. Receptionist clicks **Admit** on the patient record.
2. System auto‑generates admission number: `ADM-YYYY-XXXX`.
3. Receptionist selects:
   - Ward (dropdown of available wards).
   - Bed (dropdown filtered by selected ward, only available beds shown).
   - Primary diagnosis (free text or from DSM/ICD list).
   - Psychiatric diagnosis (from DSM/ICD).
   - Substance use history, medical/surgical history, family history.
   - Allergies (with severity).
   - Current medications.
   - Upload consent forms (PDF/Image).
4. Clicks **Admit**.
5. System:
   - Marks bed as occupied.
   - Creates an admission record.
   - Adds admission charges to billing.
   - Notifies relevant staff (e.g., nurse, psychiatrist).
6. Patient appears in **Active Inpatients** list.

**Alternative Flow (sponsor/insurance):**
- If a sponsor is selected, the system links the patient to the sponsor for billing.
- Insurance details are stored for future claims.

**Error Scenarios:**
- Required fields missing → show validation errors.
- Bed already occupied → bed not listed.
- Duplicate patient (same ID/phone) → warning: "Patient already exists. Do you want to update their record?"


### 3.2 Recording Vitals
**Actor:** Nurse

**Pre‑condition:** Patient is admitted.

**Steps:**
1. Nurse navigates to **Patient Search** and finds the patient.
2. Opens patient record → clicks **Vitals** tab → **Record New Vitals**.
3. Form pre‑fills current date/time (editable up to 24 hours back).
4. Nurse enters:
   - Blood Pressure (systolic/diastolic).
   - Heart Rate (bpm).
   - Respiratory Rate (breaths/min).
   - Temperature (°C).
   - Oxygen Saturation (SpO2 %).
   - Blood Sugar (mmol/L – optional).
   - Pain Score (0‑10).
5. Clicks **Save**.
6. System:
   - Shows success: "Vital signs recorded successfully."
   - Displays the newly recorded vitals immediately in the history table.
   - Updates the patient dashboard card with the latest vitals.
   - Highlights any abnormal values in red (e.g., BP > 140/90).
7. Nurse can view **Vitals History** with trends (line charts) for all parameters.

**Error Scenarios:**
- Missing required fields → validation errors.
- Out‑of‑range values (e.g., HR > 300) → warning: "Please verify the value."
- Editing after 24 hours → blocked with message: "Vitals cannot be edited after 24 hours."


### 3.3 Medication Administration (MAR)
**Actor:** Nurse

**Pre‑condition:** Pharmacist has dispensed medications and medication orders exist.

**Steps:**
1. Nurse selects patient → opens **MAR** tab.
2. Sees a list of scheduled medications for the day (with times).
3. For each medication, nurse:
   - Confirms dosage and route.
   - Selects status: **Given**, **Missed**, **Refused**, or **Held**.
   - If Missed/Refused/Held, enters a reason.
   - Records time (auto‑filled with current time, editable).
4. Clicks **Save MAR**.
5. System:
   - Logs each administration with nurse’s name and timestamp.
   - Updates patient’s medication history.
   - Deducts stock (if dispensing was not done earlier).
   - Adds charges to patient’s bill (per medication dose).
   - Sends alert if a medication was missed (to doctor and nurse supervisor).

**Print MAR:**
- Nurse can click **Print MAR** to generate a PDF for a specific date.
- The MAR includes patient name, all medications, times, administration status, and nurse signatures.

**Error Scenarios:**
- Medication out of stock → warning: "Insufficient stock. Contact pharmacy."
- Time/date in the future → validation: "Cannot record future administrations."


### 3.4 Discharge Workflow
**Actor:** Doctor / Clinical Officer (initiates), with steps for Pharmacy, Billing, Finance.

**Pre‑condition:** Patient is ready for discharge.

**Flow:**

#### Step 1: Doctor Initiates Discharge
1. Doctor opens patient record → clicks **Discharge**.
2. System checks outstanding balance.
3. If balance > 0 → shows warning: *"This patient has an outstanding balance of KES [amount]. Discharge cannot proceed until the balance is cleared."* → Discharge button blocked.
4. If balance = 0 → Discharge form opens.
5. Doctor fills:
   - Clinical summary.
   - Discharge diagnosis.
   - Medications at discharge.
   - Follow‑up plan.
   - Referral details (if any).
6. Clicks **Initiate Discharge**.
7. System creates a discharge request and notifies:
   - Pharmacy (to confirm no pending meds).
   - Billing (to confirm all charges captured).
   - Finance (to confirm balance).

#### Step 2: Pharmacy Confirmation
- Pharmacist sees pending discharge requests in dashboard.
- Reviews patient’s medication dispensing history.
- If all medications dispensed → confirms.
- If pending → notes reason (e.g., "Patient has not received last dose of antibiotic").

#### Step 3: Billing Confirmation
- Accountant reviews charges: admission, accommodation, medication, consumables, lab, reviews.
- If all captured → confirms.
- If missing → adds charges and confirms.

#### Step 4: Finance Confirmation
- Finance officer reviews payment history.
- If balance = 0 → confirms.
- If balance > 0 → flags as outstanding (discharge cannot proceed unless force discharge).

#### Step 5: Final Approval (Doctor)
- Doctor receives notification that all steps are confirmed.
- Clicks **Complete Discharge**.
- System:
   - Marks patient as discharged.
   - Moves patient from active inpatients to Discharged Patients.
   - Frees bed.
   - Generates Discharge Summary (PDF/Word).
   - Records discharge date/time.
   - Logs in audit trail.

**Force Discharge (Admins/Directors only):**
- If balance > 0 and user has permission, a **Force Discharge** button appears.
- Requires:
   - Reason (mandatory text).
   - Admin password confirmation.
- System logs the override in audit trail.
- Patient is discharged with outstanding balance flagged (red) in the discharged list.

**Error Scenarios:**
- Balance > 0 and user not admin → button greyed out with tooltip: "Contact admin to clear balance."
- Missing clinical summary → validation.

### 3.5 Generating an Invoice
**Actor:** Accountant

**Pre‑condition:** Patient has accrued charges.

**Steps:**
1. Accountant selects patient → **Billing** tab → **Generate Invoice**.
2. System auto‑collects all charges:
   - Groups by category (Medication, Consumables, Accommodation, Lab, Reviews, etc.).
   - Within medication, groups by drug name (not individual doses).
3. Accountant can:
   - Add discounts (with reason).
   - Add manual adjustments (e.g., service not automatically captured).
   - Select date range (default: admission to current date).
4. Clicks **Generate Invoice**.
5. System creates a professional invoice (PDF) with:
   - Facility branding (logo, name, address, contacts).
   - Patient details (name, admission number, dates).
   - Itemised grouped charges with subtotals.
   - Total, amount paid, outstanding balance (in red if > 0).
6. Invoice is saved to patient’s billing history.
7. Accountant can **Print** or **Download PDF**.
8. Option to send invoice to sponsor/patient via email.

**Error Scenarios:**
- No charges → message: "No charges to invoice."
- Missing facility branding → system uses default (RehabYangu).

### 3.6 Recording Payment
**Actor:** Accountant

**Steps:**
1. Accountant navigates to patient billing → **Record Payment**.
2. Selects payment method: Cash, Bank Transfer, Card, M-Pesa.
3. Enters amount, payment reference (e.g., M‑Pesa transaction ID).
4. Optionally allocates payment to specific invoice(s).
5. Clicks **Record Payment**.
6. System:
   - Generates a receipt (PDF) with receipt number, date, payment method, reference.
   - Updates patient’s balance.
   - Updates sponsor balance (if sponsor linked).
   - Logs in audit trail.
7. Accountant can print or email the receipt.

### 3.7 Pharmacy Dispensing
**Actor:** Pharmacist

**Pre‑condition:** Doctor has prescribed medication (via EMR or prescription).

**Steps:**
1. Pharmacist sees pending prescriptions in dashboard.
2. Selects patient → **Dispense Medication**.
3. For each prescribed medication:
   - Verifies drug, strength, dosage form.
   - Enters quantity to dispense.
   - **System enforces dosage‑form rules:**
     - Tablet/Capsule → whole numbers only.
     - Syrup/Injection/IV/Cream → allows 1 decimal place.
     - If invalid → error: "Tablets must be dispensed in whole numbers."
   - Selects batch number (if multiple batches).
   - Checks expiry date (warns if expiring soon).
4. Clicks **Dispense**.
5. System:
   - Deducts stock.
   - Adds medication charges to patient’s bill.
   - Updates MAR with dispensing details.
   - Generates a dispensing label (optional).
   - Sends notification to nurse (if in‑patient).

**Error Scenarios:**
- Insufficient stock → warning: "Only X units available. Adjust quantity."
- Drug expired → blocked: "This batch is expired. Select another batch."


### 3.8 Psychiatric Review
**Actor:** Psychiatrist

**Steps:**
1. Psychiatrist opens patient record → **Psychiatric Review**.
2. Fills:
   - Review date.
   - Mental State Examination (structured template).
   - Diagnosis update (DSM/ICD).
   - Medication changes (start, stop, adjust).
   - Recommendations.
3. Clicks **Save**.
4. System:
   - Adds review to patient’s EMR.
   - If this is the 3rd review in the month (beyond the 2 included), adds a charge for "Additional Psychiatric Review".
   - Notifies clinical team.
   - Updates treatment plan if applicable.


### 3.9 Counseling Session
**Actor:** Counselor

**Steps:**
1. Counselor selects patient → **Counseling** tab.
2. Selects session type: Individual, Group, Family, Psychoeducation, Relapse Prevention.
3. Enters:
   - Date/time.
   - Duration.
   - Attendance (Patient attended, Did not attend).
   - Session notes (free text or structured).
   - Progress toward treatment goals.
4. Clicks **Save**.
5. System:
   - Adds session to patient’s counseling history.
   - Updates weekly session count.
   - If billing applies, adds charge (configurable per tenant).


## 4. Workflow Diagrams (Text‑Based)
### 4.1 Discharge Workflow

┌──────────────┐
│ Doctor │
│ Initiates │
│ Discharge │
└──────┬───────┘
│
▼
┌──────────────┐ ┌──────────────┐
│ Check │ │ Balance > 0 │
│ Outstanding │────▶│ Block │
│ Balance │ │ Discharge │
└──────┬───────┘ └──────────────┘
│ Balance = 0
▼
┌──────────────┐
│ Notify │
│ Pharmacy │
└──────┬───────┘
│
▼
┌──────────────┐ ┌──────────────┐
│ Pharmacy │ │ Notify │
│ Confirms? │────▶│ Doctor of │
└──────┬───────┘ │ pending │
│ Yes └──────────────┘
▼
┌──────────────┐
│ Notify │
│ Billing │
└──────┬───────┘
│
▼
┌──────────────┐ ┌──────────────┐
│ Billing │ │ Notify │
│ Confirms? │────▶│ Doctor of │
└──────┬───────┘ │ missing │
│ Yes │ charges │
▼
┌──────────────┐
│ Notify │
│ Finance │
└──────┬───────┘
│
▼
┌──────────────┐ ┌──────────────┐
│ Finance │ │ Notify │
│ Confirms? │────▶│ Doctor │
└──────┬───────┘ │ (balance >0) │
│ Yes └──────────────┘
▼
┌──────────────┐
│ Doctor │
│ Completes │
│ Discharge │
└──────────────┘
text


### 4.2 Vitals Recording Flow

┌──────────────┐
│ Nurse │
│ Selects │
│ Patient │
└──────┬───────┘
│
▼
┌──────────────┐
│ Enters │
│ Vitals │
└──────┬───────┘
│
▼
┌──────────────┐ ┌──────────────┐
│ Validate │ │ Show │
│ Values │────▶│ Validation │
└──────┬───────┘ │ Error │
│ Valid └──────────────┘
▼
┌──────────────┐
│ Save │
└──────┬───────┘
│
▼
┌──────────────┐
│ Display │
│ Success + │
│ Update │
│ History/ │
│ Trends │
└──────────────┘


## 5. Role‑Based Access – Summary Table
| Role | Can View | Can Create/Edit | Restricted |
|------|----------|-----------------|------------|
| Super Admin | All | All system settings, tenant config | No Restriction |
| Director | All clinical & financial dashboards | Force discharge, approve users | Cannot edit billing rates (configurable) |
| Psychiatrist | Patient EMR, MAR, pharmacy | Psychiatric reviews, prescriptions | Cannot discharge, cannot view finance |
| Clinical Officer | Patient EMR, vitals, lab | Progress notes, initiate discharge (if balance=0) | Cannot prescribe controlled meds (configurable) |
| Nurse | Vitals, MAR, nursing notes | Record vitals, MAR, nursing notes, shift handover | Cannot edit billing, delete records |
| Counselor | Patient counseling records | Session notes, progress evaluation | Cannot prescribe medication, access finance |
| Pharmacist | Drug inventory, prescriptions | Add stock, dispense, update stock | Cannot modify patient diagnoses |
| Lab Tech | Lab requests, results | Enter results | Cannot modify clinical notes |
| Accountant | Billing, invoices, payments | Generate invoices, record payments, manage sponsors | Cannot access clinical records |
| Receptionist | Patient demographics, admissions | Register patients, admit, update demographics | Cannot access finance, clinical records |
| Store Manager | Consumables inventory | Add/issue stock, purchase orders | Cannot access clinical data |
| Cook | Dietary requirements, patient counts (anonymised) | View only | Cannot view patient names/clinical data |
| Sponsor | Sponsor dashboard | View statements, pay | Cannot view other patients/sponsors |


## 6. Screen Transitions & Navigation
### Main Navigation (Sidebar)
All authenticated users see a sidebar with modules based on their role.

- **Dashboard** – always visible.
- **Patients** – visible to all except Cook, Sponsor.
  - Sub‑menu: Register Patient, Patient List, Admissions, Discharged Patients.
- **Clinical** – visible to clinical roles (Doctor, Nurse, Psychiatrist, Counselor).
  - Sub‑menu: EMR, Vitals, MAR, Counseling.
- **Pharmacy** – visible to Pharmacist, Nurse, Doctor (read‑only for Doctor/Nurse).
- **Billing** – visible to Accountant, Director, Super Admin.
- **Reports** – visible based on role.
- **Settings** – visible to Super Admin, Director.
- **Admin** – visible to Super Admin (user management, system config).

### Global Search
Located at the top of every page. Users can search by:
- Patient name, admission number, phone, national ID.
- Staff name.
- Medication name.
- Invoice number.

Search results are filtered by user permissions.


## 7. Error Scenarios & System Responses
| Scenario | System Response |
|----------|-----------------|
| User tries to access a page without permission | Redirect to dashboard with message: "You do not have permission to view this page." |
| User tries to discharge a patient with outstanding balance | Show warning; block discharge; advise to clear balance or use force discharge (admins only). |
| User enters invalid vitals (e.g., HR > 300) | Show validation error: "Please verify the value." |
| Medication dispensing with decimal for tablets | Show error: "Tablets must be dispensed in whole numbers." |
| Drug stock below minimum | Show low‑stock alert in dashboard; notify pharmacist. |
| Drug expiry within 30 days | Show expiry alert in dashboard; notify pharmacist. |
| User account pending approval | On login, show message: "Your account is pending approval." |
| User attempts to edit vitals after 24 hours | Block edit with message: "Vitals cannot be edited after 24 hours." |
| M‑Pesa payment reference missing | Validation: "M‑Pesa transaction ID is required." |
| Bed already occupied | Dropdown excludes occupied beds; if selected, show error. |


## 8. Success Metrics for User Journeys
| Journey | Key Success Indicator |
|---------|------------------------|
| Patient Registration | Time to register < 3 minutes. |
| Vitals Recording | Success rate > 99% (no errors). |
| Discharge | All steps completed within 1 hour (initiation to final). |
| Invoice Generation | Zero errors in grouping charges; PDF renders correctly. |
| Medication Dispensing | Zero decimal errors; stock updated correctly. |
| MAR | All administrations recorded within 1 hour of schedule. |


## 9. Change Log
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | 2026-07-11 | UX Lead | Reviewed for clarity. |

**Status:** On review – Ready for review by other team members.   
