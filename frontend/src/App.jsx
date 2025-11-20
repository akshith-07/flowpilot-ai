/**
 * App Component
 * Main application component with routing
 */

import { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';

import { ROUTES } from '@constants';
import { selectIsAuthenticated, fetchCurrentUser } from '@store/slices/authSlice';
import { getAccessToken } from '@utils';

// Layouts
import AuthLayout from '@layouts/AuthLayout';
import DashboardLayout from '@layouts/DashboardLayout';

// Auth Pages
import LoginPage from '@pages/auth/LoginPage';
import RegisterPage from '@pages/auth/RegisterPage';
import ForgotPasswordPage from '@pages/auth/ForgotPasswordPage';
import ResetPasswordPage from '@pages/auth/ResetPasswordPage';

// Dashboard Pages
import DashboardPage from '@pages/DashboardPage';

// Workflow Pages
import WorkflowsPage from '@pages/workflows/WorkflowsPage';
import WorkflowDetailPage from '@pages/workflows/WorkflowDetailPage';
import WorkflowBuilderPage from '@pages/workflows/WorkflowBuilderPage';

// Execution Pages
import ExecutionsPage from '@pages/executions/ExecutionsPage';
import ExecutionDetailPage from '@pages/executions/ExecutionDetailPage';

// Connector Pages
import ConnectorsPage from '@pages/connectors/ConnectorsPage';
import ConnectorDetailPage from '@pages/connectors/ConnectorDetailPage';

// Document Pages
import DocumentsPage from '@pages/documents/DocumentsPage';
import DocumentDetailPage from '@pages/documents/DocumentDetailPage';

// Analytics Pages
import AnalyticsPage from '@pages/analytics/AnalyticsPage';

// Organization Pages
import OrganizationSettingsPage from '@pages/organization/OrganizationSettingsPage';
import OrganizationMembersPage from '@pages/organization/OrganizationMembersPage';

// User Settings Pages
import UserProfilePage from '@pages/settings/UserProfilePage';
import UserSecurityPage from '@pages/settings/UserSecurityPage';

// Not Found
import NotFoundPage from '@pages/NotFoundPage';

/**
 * Protected Route Component
 */
const ProtectedRoute = ({ children }) => {
  const isAuthenticated = useSelector(selectIsAuthenticated);

  if (!isAuthenticated) {
    return <Navigate to={ROUTES.LOGIN} replace />;
  }

  return children;
};

/**
 * Public Route Component (redirects to dashboard if authenticated)
 */
const PublicRoute = ({ children }) => {
  const isAuthenticated = useSelector(selectIsAuthenticated);

  if (isAuthenticated) {
    return <Navigate to={ROUTES.DASHBOARD} replace />;
  }

  return children;
};

/**
 * Main App Component
 */
function App() {
  const dispatch = useDispatch();
  const isAuthenticated = useSelector(selectIsAuthenticated);

  /**
   * Fetch current user on app load if token exists
   */
  useEffect(() => {
    const token = getAccessToken();
    if (token && !isAuthenticated) {
      dispatch(fetchCurrentUser());
    }
  }, [dispatch, isAuthenticated]);

  return (
    <Routes>
      {/* Public Routes */}
      <Route
        path={ROUTES.LOGIN}
        element={
          <PublicRoute>
            <AuthLayout>
              <LoginPage />
            </AuthLayout>
          </PublicRoute>
        }
      />
      <Route
        path={ROUTES.REGISTER}
        element={
          <PublicRoute>
            <AuthLayout>
              <RegisterPage />
            </AuthLayout>
          </PublicRoute>
        }
      />
      <Route
        path={ROUTES.FORGOT_PASSWORD}
        element={
          <PublicRoute>
            <AuthLayout>
              <ForgotPasswordPage />
            </AuthLayout>
          </PublicRoute>
        }
      />
      <Route
        path={ROUTES.RESET_PASSWORD}
        element={
          <PublicRoute>
            <AuthLayout>
              <ResetPasswordPage />
            </AuthLayout>
          </PublicRoute>
        }
      />

      {/* Protected Routes */}
      <Route
        path={ROUTES.DASHBOARD}
        element={
          <ProtectedRoute>
            <DashboardLayout>
              <DashboardPage />
            </DashboardLayout>
          </ProtectedRoute>
        }
      />

      {/* Workflows */}
      <Route
        path={ROUTES.WORKFLOWS}
        element={
          <ProtectedRoute>
            <DashboardLayout>
              <WorkflowsPage />
            </DashboardLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path={ROUTES.WORKFLOW_DETAIL}
        element={
          <ProtectedRoute>
            <DashboardLayout>
              <WorkflowDetailPage />
            </DashboardLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path={ROUTES.WORKFLOW_BUILDER}
        element={
          <ProtectedRoute>
            <DashboardLayout fullWidth>
              <WorkflowBuilderPage />
            </DashboardLayout>
          </ProtectedRoute>
        }
      />

      {/* Executions */}
      <Route
        path={ROUTES.EXECUTIONS}
        element={
          <ProtectedRoute>
            <DashboardLayout>
              <ExecutionsPage />
            </DashboardLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path={ROUTES.EXECUTION_DETAIL}
        element={
          <ProtectedRoute>
            <DashboardLayout>
              <ExecutionDetailPage />
            </DashboardLayout>
          </ProtectedRoute>
        }
      />

      {/* Connectors */}
      <Route
        path={ROUTES.CONNECTORS}
        element={
          <ProtectedRoute>
            <DashboardLayout>
              <ConnectorsPage />
            </DashboardLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path={ROUTES.CONNECTOR_DETAIL}
        element={
          <ProtectedRoute>
            <DashboardLayout>
              <ConnectorDetailPage />
            </DashboardLayout>
          </ProtectedRoute>
        }
      />

      {/* Documents */}
      <Route
        path={ROUTES.DOCUMENTS}
        element={
          <ProtectedRoute>
            <DashboardLayout>
              <DocumentsPage />
            </DashboardLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path={ROUTES.DOCUMENT_DETAIL}
        element={
          <ProtectedRoute>
            <DashboardLayout>
              <DocumentDetailPage />
            </DashboardLayout>
          </ProtectedRoute>
        }
      />

      {/* Analytics */}
      <Route
        path={ROUTES.ANALYTICS}
        element={
          <ProtectedRoute>
            <DashboardLayout>
              <AnalyticsPage />
            </DashboardLayout>
          </ProtectedRoute>
        }
      />

      {/* Organization */}
      <Route
        path={ROUTES.ORGANIZATION_SETTINGS}
        element={
          <ProtectedRoute>
            <DashboardLayout>
              <OrganizationSettingsPage />
            </DashboardLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path={ROUTES.ORGANIZATION_MEMBERS}
        element={
          <ProtectedRoute>
            <DashboardLayout>
              <OrganizationMembersPage />
            </DashboardLayout>
          </ProtectedRoute>
        }
      />

      {/* User Settings */}
      <Route
        path={ROUTES.USER_PROFILE}
        element={
          <ProtectedRoute>
            <DashboardLayout>
              <UserProfilePage />
            </DashboardLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path={ROUTES.USER_SECURITY}
        element={
          <ProtectedRoute>
            <DashboardLayout>
              <UserSecurityPage />
            </DashboardLayout>
          </ProtectedRoute>
        }
      />

      {/* Root redirect */}
      <Route
        path={ROUTES.HOME}
        element={
          isAuthenticated ? (
            <Navigate to={ROUTES.DASHBOARD} replace />
          ) : (
            <Navigate to={ROUTES.LOGIN} replace />
          )
        }
      />

      {/* 404 Not Found */}
      <Route path={ROUTES.NOT_FOUND} element={<NotFoundPage />} />
    </Routes>
  );
}

export default App;
