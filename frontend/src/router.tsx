import { createRootRoute, createRoute, createRouter, Outlet } from '@tanstack/react-router';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Patients from './pages/Patients';
import Appointments from './pages/Appointments';
import PatientDetail from './pages/PatientDetail';
import Billing from './pages/Billing';
import Tenants from './pages/Admin/Tenants';
import Staff from './pages/Staff';
import Vitals from './pages/Vitals';
import PendingDischarges from './pages/PendingDischarges';
import DischargedPatients from './pages/DischargedPatients';
import Settings from './pages/Settings';
import ClinicalNotes from './pages/ClinicalNotes';
import Inventory from './pages/Inventory';
import Sponsors from './pages/Sponsors';
import ComingSoon from './components/ComingSoon';
import Sidebar from './components/Layout/Sidebar';
import Header from './components/Layout/Header';
import { useAuth } from './context/AuthContext';
import type { ReactNode } from 'react';

// Layout component
function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="flex h-screen overflow-hidden bg-secondary-50">
      <Sidebar />
      <div className="flex-1 flex flex-col ml-56">
        <Header />
        <main className="flex-1 overflow-y-auto p-4 md:p-6 lg:p-8 bg-secondary-50 animate-fadeIn">
          {children}
        </main>
      </div>
    </div>
  );
}

// Root route
const rootRoute = createRootRoute({
  component: () => {
    const { user, isLoading } = useAuth();
    if (isLoading) return <div className="flex items-center justify-center h-screen text-sm text-secondary-500">Loading...</div>;
    if (!user) return <Login />;
    return <Layout><Outlet /></Layout>;
  },
  notFoundComponent: () => <div className="p-4 text-center">Page Not Found (404)</div>,
});

// Routes (no /new-login, no LoginPage import)
const dashboardRoute = createRoute({ getParentRoute: () => rootRoute, path: '/', component: () => <Dashboard /> });
const patientsRoute = createRoute({ getParentRoute: () => rootRoute, path: '/patients', component: () => <Patients /> });
const appointmentsRoute = createRoute({ getParentRoute: () => rootRoute, path: '/appointments', component: () => <Appointments /> });
const billingRoute = createRoute({ getParentRoute: () => rootRoute, path: '/billing', component: () => <Billing /> });
const patientDetailRoute = createRoute({ getParentRoute: () => rootRoute, path: '/patients/$id', component: () => <PatientDetail /> });
const adminTenantsRoute = createRoute({ getParentRoute: () => rootRoute, path: '/admin/tenants', component: () => <Tenants /> });
const staffRoute = createRoute({ getParentRoute: () => rootRoute, path: '/staff', component: () => <Staff /> });
const vitalsRoute = createRoute({ getParentRoute: () => rootRoute, path: '/vitals', component: () => <Vitals /> });
const pendingDischargesRoute = createRoute({ getParentRoute: () => rootRoute, path: '/pending-discharges', component: () => <PendingDischarges /> });
const dischargedPatientsRoute = createRoute({ getParentRoute: () => rootRoute, path:'/discharged-patients', component: () => <DischargedPatients /> });
const loginRoute = createRoute({ getParentRoute: () => rootRoute, path: '/login', component: () => <Login /> });
const admissionsRoute = createRoute({ getParentRoute: () => rootRoute, path: '/admissions', component: () => <ComingSoon /> });
const clinicalNotesRoute = createRoute({ getParentRoute: () => rootRoute, path: '/clinical-notes', component: () => <ClinicalNotes /> });
const medicationRoute = createRoute({ getParentRoute: () => rootRoute, path: '/medication', component: () => <ComingSoon /> });
const pharmacyRoute = createRoute({ getParentRoute: () => rootRoute, path: '/pharmacy', component: () => <ComingSoon /> });
const inventoryRoute = createRoute({ getParentRoute: () => rootRoute, path: '/inventory', component: () => <Inventory /> });
const sponsorsRoute = createRoute({ getParentRoute: () => rootRoute, path: '/sponsors', component: () => <Sponsors /> });
const reportsRoute = createRoute({ getParentRoute: () => rootRoute, path: '/reports', component: () => <ComingSoon /> });
const settingsRoute = createRoute({ getParentRoute: () => rootRoute, path: '/settings', component: () => <Settings /> });
const helpRoute = createRoute({ getParentRoute: () => rootRoute, path: '/help', component: () => <ComingSoon /> });
const profileRoute = createRoute({ getParentRoute: () => rootRoute, path: '/profile', component: () => <ComingSoon /> });

const routeTree = rootRoute.addChildren([
  dashboardRoute,
  patientsRoute,
  appointmentsRoute,
  clinicalNotesRoute,
  vitalsRoute,
  billingRoute,
  admissionsRoute,
  medicationRoute,
  pharmacyRoute,
  inventoryRoute,
  sponsorsRoute,
  reportsRoute,
  staffRoute,
  settingsRoute,
  helpRoute,
  patientDetailRoute,
  adminTenantsRoute,
  pendingDischargesRoute,
  dischargedPatientsRoute,
  profileRoute,
  loginRoute,
]);

export const router = createRouter({ routeTree });

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router;
  }
}