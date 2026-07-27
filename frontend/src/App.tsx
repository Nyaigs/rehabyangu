import { AuthProvider, useAuth } from './context/AuthContext';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { createRootRoute, createRoute, createRouter, RouterProvider, Outlet, Link } from '@tanstack/react-router';
import Login from './pages/Login';
import Patients from './pages/Patients';
import Appointments from './pages/Appointments';
import type { ReactNode } from 'react';

function Layout({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth();
  if (!user) return <Login />;
  return (
    <div>
      <div className="bg-blue-600 text-white p-4 flex justify-between items-center flex-wrap gap-2">
        <span className="font-bold text-xl">RehabYangu</span>
        <div className="flex gap-4 items-center flex-wrap">
          <Link to="/" className="hover:underline">Patients</Link>
          <Link to="/appointments" className="hover:underline">Appointments</Link>
          <button onClick={logout} className="bg-red-500 hover:bg-red-600 px-4 py-1 rounded">Logout</button>
        </div>
      </div>
      <div className="p-4">{children}</div>
    </div>
  );
}

const rootRoute = createRootRoute({
  component: () => {
    const { user, isLoading } = useAuth();
    if (isLoading) return <div className="p-4">Loading...</div>;
    if (!user) return <Login />;
    return <Layout><Outlet /></Layout>;
  }
});

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  component: () => <Patients />,
});

const appointmentsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/appointments',
  component: () => <Appointments />,
});

const loginRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/login',
  component: () => <Login />,
});

const routeTree = rootRoute.addChildren([indexRoute, appointmentsRoute, loginRoute]);
const router = createRouter({ routeTree });

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router;
  }
}

function App() {
  const queryClient = new QueryClient();
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <RouterProvider router={router} />
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
