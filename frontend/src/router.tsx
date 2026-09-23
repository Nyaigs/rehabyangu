import { createRootRoute, createRoute, createRouter, Navigate, Outlet, useRouterState } from '@tanstack/react-router';
import Sidebar from './components/Layout/Sidebar';
import Header from './components/Layout/Header';
import { AppFooter } from './components/Layout/AppFooter';
import { useAuth } from './context/AuthContext';
import type { ReactNode } from 'react';
import { lazy, Suspense } from 'react';
const Login = lazy(() => import('./pages/Login'));
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Patients = lazy(() => import('./pages/Patients'));
const Appointments = lazy(() => import('./pages/Appointments'));
const PatientDetail = lazy(() => import('./pages/PatientDetail'));
const Billing = lazy(() => import('./pages/Billing'));
const Tenants = lazy(() => import('./pages/Admin/Tenants'));
const AdminPlans = lazy(() => import('./pages/Admin/Plans'));
const AdminTenantDetail = lazy(() => import('./pages/Admin/TenantDetail'));
const Staff = lazy(() => import('./pages/Staff'));
const Vitals = lazy(() => import('./pages/Vitals'));
const PendingDischarges = lazy(() => import('./pages/PendingDischarges'));
const DischargedPatients = lazy(() => import('./pages/DischargedPatients'));
const Settings = lazy(() => import('./pages/Settings'));
const ClinicalNotes = lazy(() => import('./pages/ClinicalNotes'));
const Inventory = lazy(() => import('./pages/Inventory'));
const Sponsors = lazy(() => import('./pages/Sponsors'));
const Admissions = lazy(() => import('./pages/Admissions'));
const Medications = lazy(() => import('./pages/Medications'));
const Help = lazy(() => import('./pages/Help'));
const Profile = lazy(() => import('./pages/Profile'));
const Pharmacy = lazy(() => import('./pages/Pharmacy'));
const Reports = lazy(() => import('./pages/Reports'));
const InvitationAccept = lazy(() => import('./pages/InvitationAccept'));
const Onboarding = lazy(() => import('./pages/Onboarding'));

// Layout component
function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <Header />
        <main className="flex-1 px-4 py-6 pb-24 sm:px-6 md:px-8 md:py-8 lg:pb-8">
          {children}
        </main>
        <AppFooter />
      </div>
    </div>
  );
}

function AuthLoadingScreen() {
  return <div className="grid min-h-screen place-items-center bg-[#f3f7f6] p-6"><div className="flex items-center gap-3 text-sm font-semibold text-[#254651]"><span className="grid h-10 w-10 place-items-center rounded-xl bg-[#17614f] text-base text-white">R</span><span>Preparing your secure workspace…</span></div></div>;
}

function RouteLoadingScreen() { return <div className="p-6 text-sm text-secondary-500">Loading screen…</div>; }

function AuthenticatedLoginRedirect() {
  const { user, isPlatformAdmin } = useAuth();
  return user ? <Navigate to={isPlatformAdmin ? '/admin' : '/'} replace /> : <Suspense fallback={<AuthLoadingScreen />}><Login /></Suspense>;
}

function RootRouteComponent() {
  const { user, isLoading, isRehabAdmin, isSuperAdmin, isPlatformAdmin, tenantBranding } = useAuth();
  const pathname = useRouterState({ select: (state) => state.location.pathname });
  if (pathname === '/invitations/accept') return <Suspense fallback={<AuthLoadingScreen />}><InvitationAccept /></Suspense>;
  if (isLoading) return <AuthLoadingScreen />;
  if (!user) return <Suspense fallback={<AuthLoadingScreen />}><Login /></Suspense>;
  if (pathname === '/admin' || pathname.startsWith('/admin/')) {
    return isSuperAdmin ? <Layout><Suspense fallback={<RouteLoadingScreen />}><Outlet /></Suspense></Layout> : <Navigate to="/" replace />;
  }
  if (isPlatformAdmin) return <Navigate to="/admin" replace />;
  const needsOnboarding = isRehabAdmin && tenantBranding?.onboarding_completed_at === null;
  if (pathname === '/onboarding') return needsOnboarding ? <Suspense fallback={<AuthLoadingScreen />}><Onboarding /></Suspense> : <Navigate to="/" replace />;
  if (needsOnboarding) return <Navigate to="/onboarding" replace />;
  return <Layout><Suspense fallback={<RouteLoadingScreen />}><Outlet /></Suspense></Layout>;
}

// Root route
const rootRoute = createRootRoute({
  component: RootRouteComponent,
  notFoundComponent: () => <div className="p-4 text-center">Page Not Found (404)</div>,
});

// Routes (no /new-login, no LoginPage import)
const dashboardRoute = createRoute({ getParentRoute: () => rootRoute, path: '/', component: () => <Dashboard /> });
const patientsRoute = createRoute({ getParentRoute: () => rootRoute, path: '/patients', component: () => <Patients /> });
const appointmentsRoute = createRoute({ getParentRoute: () => rootRoute, path: '/appointments', component: () => <Appointments /> });
const billingRoute = createRoute({ getParentRoute: () => rootRoute, path: '/billing', component: () => <Billing /> });
const patientDetailRoute = createRoute({ getParentRoute: () => rootRoute, path: '/patients/$id', component: () => <PatientDetail /> });
const adminTenantsRoute = createRoute({ getParentRoute: () => rootRoute, path: '/admin', component: () => <Tenants /> });
const adminPlansRoute = createRoute({ getParentRoute: () => rootRoute, path: '/admin/plans', component: () => <AdminPlans /> });
const adminTenantDetailRoute = createRoute({ getParentRoute: () => rootRoute, path: '/admin/tenants/$tenantId', component: () => <AdminTenantDetail /> });
const staffRoute = createRoute({ getParentRoute: () => rootRoute, path: '/staff', component: () => <Staff /> });
const vitalsRoute = createRoute({ getParentRoute: () => rootRoute, path: '/vitals', component: () => <Vitals /> });
const pendingDischargesRoute = createRoute({ getParentRoute: () => rootRoute, path: '/pending-discharges', component: () => <PendingDischarges /> });
const dischargedPatientsRoute = createRoute({ getParentRoute: () => rootRoute, path:'/discharged-patients', component: () => <DischargedPatients /> });
const loginRoute = createRoute({ getParentRoute: () => rootRoute, path: '/login', component: AuthenticatedLoginRedirect });
const invitationAcceptRoute = createRoute({ getParentRoute: () => rootRoute, path: '/invitations/accept', component: () => <InvitationAccept /> });
const onboardingRoute = createRoute({ getParentRoute: () => rootRoute, path: '/onboarding', component: () => <Onboarding /> });
const admissionsRoute = createRoute({ getParentRoute: () => rootRoute, path: '/admissions', component: () => <Admissions /> });
const clinicalNotesRoute = createRoute({ getParentRoute: () => rootRoute, path: '/clinical-notes', component: () => <ClinicalNotes /> });
const medicationRoute = createRoute({ getParentRoute: () => rootRoute, path: '/medications', component: () => <Medications /> });
const pharmacyRoute = createRoute({ getParentRoute: () => rootRoute, path: '/pharmacy', component: () => <Pharmacy /> });
const inventoryRoute = createRoute({ getParentRoute: () => rootRoute, path: '/inventory', component: () => <Inventory /> });
const sponsorsRoute = createRoute({ getParentRoute: () => rootRoute, path: '/sponsors', component: () => <Sponsors /> });
const reportsRoute = createRoute({ getParentRoute: () => rootRoute, path: '/reports', component: () => <Reports /> });
const settingsRoute = createRoute({ getParentRoute: () => rootRoute, path: '/settings', component: () => <Settings /> });
const helpRoute = createRoute({ getParentRoute: () => rootRoute, path: '/help', component: () => <Help /> });
const profileRoute = createRoute({ getParentRoute: () => rootRoute, path: '/profile', component: () => <Profile /> });

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
  adminPlansRoute,
  adminTenantDetailRoute,
  pendingDischargesRoute,
  dischargedPatientsRoute,
  profileRoute,
  loginRoute,
  invitationAcceptRoute,
  onboardingRoute,
]);

export const router = createRouter({ routeTree });

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router;
  }
}
