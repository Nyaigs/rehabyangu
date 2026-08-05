# Project Structure

rehabyangu/
├── backend/ # Django application (API server)
│ ├── config/ # Project settings, root URL conf, WSGI
│ ├── patients/ # Patient management
│ ├── appointments/ # Appointments
│ ├── clinical/ # Clinical notes
│ ├── billing/ # Billing & invoices
│ ├── inventory/ # Pharmacy inventory
│ ├── vitals/ # Vitals tracking
│ ├── tenants/ # Tenant & subscription management
│ ├── users/ # User profiles, memberships, audit logs
│ ├── authorization/ # RBAC (permissions, roles)
│ ├── subscriptions/ # Notifications & subscription helpers
│ ├── sponsors/ # Financial sponsors
│ └── manage.py # Django management script
├── frontend/ # React application (currently being rebuilt)
│ ├── src/
│ │ ├── api/ # Axios client
│ │ ├── components/ # Shared UI & layout components
│ │ ├── context/ # Auth & toast contexts
│ │ ├── hooks/ # Custom React hooks
│ │ ├── lib/ # Utilities
│ │ ├── pages/ # Page components (temporary)
│ │ ├── router.tsx # TanStack Router configuration
│ │ └── main.tsx # Entry point
│ └── ...
├── docs/ # Complete engineering documentation
│ ├── architecture/ # System architecture, multi-tenancy, RBAC
│ ├── backend/ # Backend specific docs
│ ├── frontend/ # Frontend specific docs
│ ├── design/ # Design system
│ ├── development/ # Developer guidelines
│ ├── deployment/ # Deployment & CI/CD
│ ├── business/ # Business model, SaaS model
│ ├── security/ # Security policies
│ ├── api/ # API reference
│ ├── product/ # Product vision, feature matrix
│ ├── roadmap/ # Future plans
│ └── README.md # Documentation index
├── docker-compose.yml # Local development services
├── LICENSE # Proprietary license
├── README.md # Repository overview
└── ...
text


This structure separates the backend, frontend, and documentation layers clearly, enabling independent development and scaling.
