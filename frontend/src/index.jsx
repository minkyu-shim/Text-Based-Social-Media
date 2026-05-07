import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import './index.css';

import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ToastProvider } from './contexts/ToastContext';
import { ToastContainer } from './components/Toast/ToastContainer';
import { AppShell } from './components/AppShell/AppShell';

import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { HomeFeedPage } from './pages/HomeFeedPage';
import { SearchPage } from './pages/SearchPage';
import { RecommendedPage } from './pages/RecommendedPage';
import { NotificationsPage } from './pages/NotificationsPage';
import { MyProfilePage } from './pages/MyProfilePage';
import { UserProfilePage } from './pages/UserProfilePage';

/** Redirects authenticated users away from login/register */
function PublicRoute({ children }) {
  const { accessToken, loading } = useAuth();
  if (loading) return null;
  if (accessToken) return <Navigate to="/" replace />;
  return children;
}

/** Redirects unauthenticated users to login */
function PrivateRoute({ children }) {
  const { accessToken, loading } = useAuth();
  if (loading) return null;
  if (!accessToken) return <Navigate to="/login" replace />;
  return children;
}

function AppRoutes() {
  return (
    <Routes>
      {/* Public routes */}
      <Route
        path="/login"
        element={
          <PublicRoute>
            <LoginPage />
          </PublicRoute>
        }
      />
      <Route
        path="/register"
        element={
          <PublicRoute>
            <RegisterPage />
          </PublicRoute>
        }
      />

      {/* Private routes inside AppShell */}
      <Route
        element={
          <PrivateRoute>
            <AppShell />
          </PrivateRoute>
        }
      >
        <Route index element={<HomeFeedPage />} />
        <Route path="/search" element={<SearchPage />} />
        <Route path="/recommendations" element={<RecommendedPage />} />
        <Route path="/notifications" element={<NotificationsPage />} />
        <Route path="/profile/me" element={<MyProfilePage />} />
        <Route path="/profile/:userId" element={<UserProfilePage />} />
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <ToastProvider>
          <AppRoutes />
          <ToastContainer />
        </ToastProvider>
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>
);
