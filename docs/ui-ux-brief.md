# RehabYangu – UI/UX Design Brief

**Version:** 0.1  
**Owner:** CTO / UX Lead  
**Status:** Draft  
**Last Updated:** 2026-07-11  

---

## 1. Purpose

This document defines the visual identity, user experience principles, and design system for RehabYangu. It ensures a **consistent, professional, and human‑centered** experience across all modules and devices.

- **Audience:** UX/UI designers, developers, product owners.
- **Goal:** Create a calm, trustworthy, and premium healthcare interface that feels human – not generic or AI‑generated.

---

## 2. Design Philosophy

RehabYangu's design is guided by these core principles:

| Principle | Description |
|-----------|-------------|
| **Human‑Centered** | Every design decision prioritises the user's emotional and cognitive needs. |
| **Calm & Trustworthy** | Patients and staff should feel safe, not overwhelmed. |
| **Professional** | Matches the standards of leading hospital systems. |
| **Accessible** | Usable by everyone, including users with disabilities. |
| **Responsive** | Works seamlessly on desktop, tablet, and mobile. |
| **White‑Label Ready** | Tenants can customise branding without breaking the design system. |

---

## 3. Brand Identity

### 3.1 Brand Personality

RehabYangu is:
- **Empathetic** – understanding the sensitivity of mental health.
- **Professional** – clinical-grade, precise, reliable.
- **Calm** – soothing colors and clean layouts reduce anxiety.
- **Modern** – contemporary but not trendy; designed to last.

### 3.2 Design Tone

- **Voice:** Warm, clear, and supportive.
- **Visual Language:** Clean, spacious, with purposeful use of color and whitespace.
- **Emotion:** Trust, clarity, hope, healing.

---

## 4. Color Palette

### 4.1 Primary Colors

| Color | Hex | Usage |
|-------|-----|-------|
| **Primary Blue** | `#2563eb` | Primary buttons, links, highlights |
| **Primary Blue Dark** | `#1d4ed8` | Hover states, active elements |
| **Primary Blue Light** | `#dbeafe` | Background highlights, subtle accents |
| **White** | `#ffffff` | Page backgrounds, cards |
| **Grey 50** | `#f8fafc` | Page backgrounds (light mode) |
| **Grey 100** | `#f1f5f9` | Card backgrounds, subtle separation |
| **Grey 200** | `#e2e8f0` | Borders, dividers |
| **Grey 600** | `#475569` | Secondary text |
| **Grey 900** | `#0f172a` | Primary text (dark) |

### 4.2 Healthcare Accent Colors

| Color | Hex | Usage |
|-------|-----|-------|
| **Success Green** | `#22c55e` | Confirmed, paid, active, success |
| **Warning Yellow** | `#eab308` | Pending, caution, attention |
| **Error Red** | `#ef4444` | Outstanding balances, errors, alerts |
| **Info Blue** | `#3b82f6` | Informational messages |

### 4.3 Dark Mode Palette

| Color | Hex | Usage |
|-------|-----|-------|
| **Dark Background** | `#0f172a` | Page background |
| **Dark Card** | `#1e293b` | Cards and containers |
| **Dark Border** | `#334155` | Dividers |
| **Dark Text Primary** | `#f1f5f9` | Primary text |
| **Dark Text Secondary** | `#94a3b8` | Secondary text |

---

## 5. Typography

### 5.1 Brand Display Font: Manrope

- **Usage:** Headings, logos, marketing materials.
- **Weight:** 600–800.
- **Why:** Premium, humanist, modern.

### 5.2 Interface Font: Inter

- **Usage:** All application UI (menus, labels, body text).
- **Weights:** 400 (regular), 500 (medium), 600 (semibold).
- **Why:** High legibility, designed for screens.

### 5.3 Document Font: Source Sans 3

- **Usage:** Clinical documents (PDFs, reports, discharge summaries).
- **Why:** Professional, highly readable, print-friendly.

### 5.4 Font Scale

| Element | Font Size | Weight | Line Height |
|---------|-----------|--------|-------------|
| H1 (Page Title) | 32px (2rem) | 700 | 1.2 |
| H2 (Section Title) | 24px (1.5rem) | 600 | 1.3 |
| H3 (Sub-section) | 20px (1.25rem) | 600 | 1.4 |
| Body Text | 16px (1rem) | 400 | 1.6 |
| Small Text | 14px (0.875rem) | 400 | 1.5 |
| Label | 12px (0.75rem) | 500 | 1.4 |

---

## 6. Layout & Navigation

### 6.1 Layout Structure

RehabYangu uses a **sidebar + main content** layout (similar to leading hospital systems):

┌─────────────────────────────────────────────────────────────┐
│ ┌──────┐ ┌──────────────────────────────────────────────────┐ │
│ │ Logo │ │ Top Bar (Search, Notifications, User Profile) │ │
│ ├──────┤ ├──────────────────────────────────────────────────┤ │
│ │ Dashb │ │ │ │
│ │ Pats │ │ MAIN CONTENT AREA │ │
│ │ Clini │ │ │ │
│ │ Pharm │ │ │ │
│ │ Bill │ │ │ │
│ │ Reps │ │ │ │
│ │ Admin │ │ │ │
│ └──────┘ └──────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
text


### 6.2 Sidebar Navigation

- **Collapsible:** Can be collapsed to icons only (saving screen space).
- **Active State:** Highlight the current section.
- **Sections:** Grouped by module:
  - Dashboard
  - Patients (with sub‑menu: Register, Search, Admissions, Discharged)
  - Clinical (with sub‑menu: EMR, Vitals, MAR, Counseling)
  - Pharmacy
  - Billing
  - Reports
  - Admin (visible to admins only)
  - Settings

### 6.3 Top Bar

- **Left:** Facility logo and name (tenant‑specific).
- **Center:** Global search (search patients, staff, medications, invoices).
- **Right:** Notifications (bell icon), Light/Dark mode toggle, User profile.

### 6.4 Global Search

- **Position:** Top bar, prominently visible.
- **Search Scope:** Patients (name, ID, phone), staff, medications, invoices.
- **Results:** Dropdown with categorized results.
- **Keyboard Shortcut:** `Ctrl + K` (or `Cmd + K` on Mac).

---

## 7. Dashboard

### 7.1 Layout

The dashboard uses a **card‑based layout** with real‑time statistics:

┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Admissions │ │ Occupancy │ │ Available │ │ Discharged │
│ Today: 5 │ │ 78% │ │ 22 beds │ │ This Mo: 32│
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘

┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Revenue │ │ Outstanding │ │ Stock │ │ Expiring │
│ This Mo │ │ Balances │ │ Alerts: 3 │ │ Drugs: 5 │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘

┌─────────────────────────┐ ┌─────────────────────────────────┐
│ Revenue Chart (Bar) │ │ Admission Trends (Line) │
│ Monthly breakdown │ │ Daily/weekly patient flow │
└─────────────────────────┘ └─────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Patient Statistics by Diagnosis │
│ Pie chart / bar chart showing top diagnoses │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Upcoming Reviews / Discharges (List) │
│ - Patient A: Review due tomorrow │
│ - Patient B: Discharge pending pharmacy confirmation │
└─────────────────────────────────────────────────────────────┘
text


### 7.2 Card Design

- **Background:** White (light mode) or dark card (dark mode).
- **Border radius:** `rounded-lg` (8px) for a modern feel.
- **Shadow:** Subtle shadow for depth.
- **Icon:** Professional medical icon (Lucide/Feather icons).
- **Value:** Large, bold number.
- **Label:** Small, secondary text.
- **Trend indicator:** Optional up/down arrow with percentage.

---

## 8. Component System

### 8.1 Buttons

| Type | Styling | Usage |
|------|---------|-------|
| **Primary** | Blue background, white text | Main actions (Save, Submit) |
| **Secondary** | White background, blue text, border | Alternative actions (Cancel, Back) |
| **Destructive** | Red background, white text | Delete, Force Discharge |
| **Ghost** | Transparent, text only | Less prominent actions |
| **Icon** | Icon only, blue | In tables (Edit, Delete, View) |

### 8.2 Form Inputs

- **Style:** Minimal, clean, with bottom border or outline.
- **Label:** Always visible, placed above the input.
- **Placeholder:** Hint text.
- **Validation:** Green border for valid, red border for invalid.
- **Error Message:** Below input, red text.

### 8.3 Tables

- **Style:** Clean, striped (alternating rows).
- **Header:** Grey background, bold text.
- **Rows:** Hover state.
- **Actions:** Icons (Edit, Delete, View) in the last column.
- **Pagination:** At the bottom.
- **Search/Filter:** Above the table.

### 8.4 Cards

- **Usage:** Dashboard stats, patient summaries, module previews.
- **Style:** White background, subtle shadow, rounded corners.
- **Content:** Icon, title, value, optional trend.

### 8.5 Modals

- **Usage:** Confirmations, forms (e.g., Discharge, Force Discharge), alerts.
- **Backdrop:** Semi‑transparent overlay.
- **Content:** Centered, max‑width.

---

## 9. Icons

We will use **Lucide React** icons – clean, professional, modern, medical‑friendly.

**Common Icons:**

| Icon | Usage |
|------|-------|
| `Activity` | Vitals, health monitoring |
| `User` / `Users` | Patients, staff |
| `Bed` | Bed management |
| `Pill` | Pharmacy |
| `DollarSign` | Billing |
| `FileText` | Documents, reports |
| `Bell` | Notifications |
| `Search` | Global search |
| `Settings` | Settings |
| `LogOut` | Logout |
| `Sun` / `Moon` | Light/Dark mode toggle |
| `AlertCircle` | Alerts, warnings |

---

## 10. White‑Labelling UI

Each tenant can customise:

| Element | Default | Customisation |
|---------|---------|---------------|
| **Logo** | RehabYangu logo | Upload PNG (auto‑resize) |
| **Facility Name** | "RehabYangu" | Input field |
| **Primary Colour** | `#2563eb` | Colour picker |
| **Favicon** | RehabYangu favicon | Generated from logo |
| **Login Page** | RehabYangu branded | Logo + facility name |
| **Dashboard Header** | RehabYangu | Logo + facility name |
| **Documents** | RehabYangu letterhead | Logo + facility name + address |
| **Emails** | RehabYangu branded | Logo + facility name |

**Default fallback:** If tenant has not customised, show RehabYangu branding.

---

## 11. Login & Registration Screens

### 11.1 Login Page

- **Layout:** Centered card on a gradient or healthcare‑inspired background.
- **Content:** Logo (tenant-specific), facility name, email field, password field, login button.
- **Links:** "Forgot password?", "Register".
- **Background:** Calm, professional (soft blue/grey gradient or healthcare image).

### 11.2 Registration Page

- **Layout:** Same card style.
- **Content:** Full name, email, password, confirm password, role selection (optional), register button.
- **Post‑registration:** Show success message: "Account created successfully. Please wait for administrator approval before logging in."

---

## 12. Patient Management UI

### 12.1 Patient List

- **Layout:** Table with search/filter at the top.
- **Columns:** Photo (thumbnail), Name, Admission Number, Admission Date, Ward, Status (Admitted/Discharged).
- **Actions:** View, Edit, Admit, Discharge (if applicable).

### 12.2 Patient Profile / EMR

- **Layout:** Tabs (Overview, EMR, Vitals, MAR, Billing, Documents).
- **Header:** Patient photo, name, admission number, bed, status.
- **Quick Actions:** Admitting, Discharge, Record Vitals.

### 12.3 Admission Form

- **Layout:** Multi‑step or long form with clear sections.
- **Sections:** Patient information, Emergency contact, Sponsor, Medical history, Allergies, Consent.
- **Validation:** Clear error messages.

---

## 13. Vitals Recording UI

### 13.1 Record Vitals Form

- **Layout:** Clean grid of inputs.
- **Fields:** BP (systolic/diastolic side‑by‑side), HR, RR, Temp, SpO2, Blood Sugar (optional), Pain Score.
- **Save Button:** Prominent, primary blue.
- **After Save:** Show "Vital signs recorded successfully" toast + display immediately below.

### 13.2 Vitals History

- **Layout:** Table with date/time, all vitals, recorded by.
- **Filters:** Date range, Last 24h/3d/1w/1m.
- **Trend Charts:** Line charts for BP, HR, Temp, SpO2.
- **Abnormal Values:** Highlighted in red.

---

## 14. Discharge UI

### 14.1 Discharge Flow

- **Step 1:** Doctor initiates discharge (clinical summary, follow‑up plan).
- **Step 2:** Pharmacy confirms no pending medications.
- **Step 3:** Billing confirms all charges captured.
- **Step 4:** Finance confirms balance cleared.

**Block:** If balance > 0, show warning and block discharge.

### 14.2 Force Discharge

- **Visibility:** Admin/Director only.
- **Modal:** Reason field, password confirmation.
- **Audit Log:** Record who, when, why.

---

## 15. Reports & Documents

### 15.1 Report Generation

- **Button:** "Generate Report" → opens modal with filters.
- **Filters:** Date range, ward, status, patient.
- **Format:** PDF, Word, Excel.
- **Preview:** Optional preview before download.

### 15.2 Document Generation

- **Templates:** Pre‑styled with tenant branding.
- **Preview:** Show before download/print.
- **Format:** PDF, Word.

---

## 16. Notifications

### 16.1 In‑App Notifications

- **Position:** Dropdown from bell icon in top bar.
- **Items:** New user registration, low stock, upcoming reviews, discharged patients.
- **Badge:** Number of unread notifications.

### 16.2 Toast Notifications

- **Style:** Slide‑in from top or bottom.
- **Colors:** Blue (info), Green (success), Red (error), Yellow (warning).
- **Auto‑dismiss:** 5 seconds.

---

## 17. Accessibility (WCAG 2.1 AA)

- **Keyboard Navigation:** All elements accessible via keyboard (Tab, Enter, Space).
- **Focus Indicators:** Clear outline for focus states.
- **Colour Contrast:** All text meets WCAG contrast ratios.
- **Screen Reader:** Proper ARIA labels and semantic HTML.
- **Text Resize:** All content remains usable at 200% zoom.
- **Alternative Text:** All images have alt text.

---

## 18. Light & Dark Mode

- **Toggle:** In top bar (sun/moon icon).
- **Theme:** Uses Tailwind's dark: variant.
- **Colors:** Respects color palette (see Section 4).
- **Persistence:** User preference saved in local storage or backend.

---

## 19. Responsive Design

### 19.1 Breakpoints

| Breakpoint | Width | Layout |
|------------|-------|--------|
| **Mobile** | < 640px | Stacked, hamburger menu |
| **Tablet** | 640–1024px | Collapsible sidebar, cards 2‑column |
| **Desktop** | > 1024px | Full sidebar, cards 4‑column |

### 19.2 Mobile Considerations

- **Sidebar:** Hidden behind hamburger menu.
- **Tables:** Horizontal scroll or card view.
- **Buttons:** Touch‑friendly (minimum 44px tap target).
- **Forms:** Single‑column layout.
- **Dashboard:** Cards stack vertically.

---

## 20. Design Assets

### 20.1 Logo Variations

- **Full:** Logo + "RehabYangu" text.
- **Icon only:** For favicon and small spaces.
- **Monochrome:** For white/black backgrounds.

### 20.2 Favicon

- **Size:** 32x32, 64x64, 180x180.
- **Colour:** Primary blue or white.

---

## 21. Design Guidelines for Developers

- Use **Tailwind CSS** for all styling.
- Use **shadcn/ui** components for consistency.
- Use **Lucide React** for icons.
- Use **Inter** as the default font.
- Use the color palette defined in Section 4.
- Support **dark mode** via Tailwind's `dark:` class.
- Use **responsive** classes (`sm:`, `md:`, `lg:`).
- **Accessibility:** Always include `aria-label` for icon buttons.

---

## 22. Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | 2026-07-11 | CTO | Initial draft. |

---

**Status:** DRAFT – Ready for review by Product Owners and design team.

