/**
 * Dashboard Page
 * Main dashboard with overview metrics and activity
 */

import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  CogIcon,
  PlayIcon,
  DocumentTextIcon,
  ChartBarIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
} from '@heroicons/react/24/outline';
import { Card, CardHeader, CardTitle, CardDescription, CardBody, Badge, LoadingInline } from '@components/ui';
import { ROUTES } from '@constants';
import { formatNumber, formatDate } from '@utils';

export default function DashboardPage() {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalWorkflows: 45,
    activeWorkflows: 28,
    totalExecutions: 1243,
    successfulExecutions: 1156,
    failedExecutions: 87,
    documentsProcessed: 567,
  });

  const [recentExecutions, setRecentExecutions] = useState([
    {
      id: '1',
      workflow_name: 'Email Processing Workflow',
      status: 'completed',
      created_at: new Date().toISOString(),
      duration: '2.5s',
    },
    {
      id: '2',
      workflow_name: 'Document Extraction',
      status: 'failed',
      created_at: new Date(Date.now() - 3600000).toISOString(),
      duration: '5.2s',
    },
    {
      id: '3',
      workflow_name: 'Data Sync Workflow',
      status: 'completed',
      created_at: new Date(Date.now() - 7200000).toISOString(),
      duration: '1.8s',
    },
  ]);

  useEffect(() => {
    // Simulate data fetching
    const timer = setTimeout(() => {
      setLoading(false);
    }, 500);

    return () => clearTimeout(timer);
  }, []);

  const getStatusBadge = (status) => {
    const variants = {
      completed: 'success',
      failed: 'error',
      running: 'warning',
      pending: 'secondary',
    };

    return <Badge variant={variants[status]} dot>{status}</Badge>;
  };

  if (loading) {
    return <LoadingInline message="Loading dashboard..." />;
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Welcome back! Here's what's happening.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card hover>
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="p-3 bg-primary-100 rounded-lg">
                <CogIcon className="h-6 w-6 text-primary-600" />
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Workflows</p>
              <p className="text-2xl font-bold text-gray-900">{formatNumber(stats.totalWorkflows)}</p>
            </div>
          </div>
        </Card>

        <Card hover>
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="p-3 bg-success-100 rounded-lg">
                <PlayIcon className="h-6 w-6 text-success-600" />
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Active Workflows</p>
              <p className="text-2xl font-bold text-gray-900">{formatNumber(stats.activeWorkflows)}</p>
            </div>
          </div>
        </Card>

        <Card hover>
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="p-3 bg-warning-100 rounded-lg">
                <ChartBarIcon className="h-6 w-6 text-warning-600" />
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Executions</p>
              <p className="text-2xl font-bold text-gray-900">{formatNumber(stats.totalExecutions)}</p>
            </div>
          </div>
        </Card>

        <Card hover>
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="p-3 bg-purple-100 rounded-lg">
                <DocumentTextIcon className="h-6 w-6 text-purple-600" />
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Documents</p>
              <p className="text-2xl font-bold text-gray-900">{formatNumber(stats.documentsProcessed)}</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Recent Executions</CardTitle>
            <CardDescription>Latest workflow executions</CardDescription>
          </CardHeader>
          <CardBody>
            <div className="space-y-4">
              {recentExecutions.map((execution) => (
                <div
                  key={execution.id}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{execution.workflow_name}</p>
                    <p className="text-sm text-gray-600">
                      {formatDate(execution.created_at, 'MMM d, yyyy HH:mm')} • {execution.duration}
                    </p>
                  </div>
                  <div>
                    {getStatusBadge(execution.status)}
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-4">
              <Link
                to={ROUTES.EXECUTIONS}
                className="text-sm font-medium text-primary-600 hover:text-primary-700"
              >
                View all executions →
              </Link>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Get started quickly</CardDescription>
          </CardHeader>
          <CardBody>
            <div className="space-y-3">
              <Link
                to={ROUTES.WORKFLOW_CREATE}
                className="block p-4 bg-primary-50 rounded-lg hover:bg-primary-100 transition-colors group"
              >
                <div className="flex items-center">
                  <CogIcon className="h-5 w-5 text-primary-600 mr-3" />
                  <div>
                    <p className="font-medium text-gray-900 group-hover:text-primary-600">
                      Create Workflow
                    </p>
                    <p className="text-sm text-gray-600">Build a new automation</p>
                  </div>
                </div>
              </Link>

              <Link
                to={ROUTES.DOCUMENT_UPLOAD}
                className="block p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors group"
              >
                <div className="flex items-center">
                  <DocumentTextIcon className="h-5 w-5 text-gray-600 mr-3" />
                  <div>
                    <p className="font-medium text-gray-900 group-hover:text-primary-600">
                      Upload Document
                    </p>
                    <p className="text-sm text-gray-600">Process a new document</p>
                  </div>
                </div>
              </Link>

              <Link
                to={ROUTES.CONNECTORS}
                className="block p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors group"
              >
                <div className="flex items-center">
                  <DocumentTextIcon className="h-5 w-5 text-gray-600 mr-3" />
                  <div>
                    <p className="font-medium text-gray-900 group-hover:text-primary-600">
                      Connect Service
                    </p>
                    <p className="text-sm text-gray-600">Add a new integration</p>
                  </div>
                </div>
              </Link>
            </div>
          </CardBody>
        </Card>
      </div>
    </div>
  );
}
