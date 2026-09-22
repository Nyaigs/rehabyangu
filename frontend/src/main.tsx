import React from 'react';
import ReactDOM from 'react-dom/client';
import { RouterProvider } from '@tanstack/react-router';
import { router } from './router';
import { AuthProvider } from './context/AuthContext';
import { ToastProvider } from './context/ToastContext';
import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from './api/queryClient';
import { ErrorBoundary } from './components/ErrorBoundary';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ErrorBoundary><QueryClientProvider client={queryClient}>
      <AuthProvider><ToastProvider><RouterProvider router={router} /></ToastProvider></AuthProvider>
    </QueryClientProvider></ErrorBoundary>
  </React.StrictMode>
);
