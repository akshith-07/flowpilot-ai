/**
 * WorkflowDetailPage Component
 * Detailed view of a workflow with version history and executions
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeftIcon,
  PencilIcon,
  PlayIcon,
  TrashIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  DocumentDuplicateIcon,
  EllipsisVerticalIcon,
} from '@heroicons/react/24/outline';
import { Button, Card, Badge, DataTable, Loading, Modal } from '@components/ui';
import { workflowService, executionService } from '@services';
import { ROUTES } from '@constants';
import { formatDate, formatRelativeTime } from '@utils/formatters';
import toast from 'react-hot-toast';

/**
 * Workflow Detail Page
 */
export default function WorkflowDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [workflow, setWorkflow] = useState(null);
  const [versions, setVersions] = useState([]);
  const [executions, setExecutions] = useState([]);
  const [activeTab, setActiveTab] = useState('overview');
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    loadWorkflowDetails();
  }, [id]);

  /**
   * Load workflow details
   */
  const loadWorkflowDetails = async () => {
    try {
      setLoading(true);
      const [workflowData, executionsData] = await Promise.all([
        workflowService.getWorkflowById(id),
        executionService.getExecutions({ workflow_id: id, limit: 10 }),
      ]);

      setWorkflow(workflowData);
      setExecutions(executionsData.results || executionsData);

      // Load versions if available
      try {
        const versionsData = await workflowService.getWorkflowVersions(id);
        setVersions(versionsData);
      } catch (error) {
        console.error('Error loading versions:', error);
      }
    } catch (error) {
      console.error('Error loading workflow:', error);
      toast.error('Failed to load workflow details');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle execute workflow
   */
  const handleExecute = async () => {
    try {
      const execution = await executionService.executeWorkflow(id, {});
      toast.success('Workflow execution started');
      navigate(`${ROUTES.EXECUTION_DETAIL}/${execution.id}`);
    } catch (error) {
      console.error('Error executing workflow:', error);
      toast.error('Failed to start workflow execution');
    }
  };

  /**
   * Handle duplicate workflow
   */
  const handleDuplicate = async () => {
    try {
      const duplicated = await workflowService.duplicateWorkflow(id);
      toast.success('Workflow duplicated successfully');
      navigate(`${ROUTES.WORKFLOW_DETAIL}/${duplicated.id}`);
    } catch (error) {
      console.error('Error duplicating workflow:', error);
      toast.error('Failed to duplicate workflow');
    }
  };

  /**
   * Handle delete workflow
   */
  const handleDelete = async () => {
    try {
      setDeleting(true);
      await workflowService.deleteWorkflow(id);
      toast.success('Workflow deleted successfully');
      navigate(ROUTES.WORKFLOWS);
    } catch (error) {
      console.error('Error deleting workflow:', error);
      toast.error('Failed to delete workflow');
      setDeleting(false);
    }
  };

  /**
   * Get status badge variant
   */
  const getStatusVariant = (status) => {
    const variants = {
      active: 'success',
      draft: 'warning',
      inactive: 'secondary',
    };
    return variants[status] || 'secondary';
  };

  /**
   * Execution columns
   */
  const executionColumns = [
    {
      key: 'id',
      label: 'Execution ID',
      render: (execution) => (
        <button
          onClick={() => navigate(`${ROUTES.EXECUTION_DETAIL}/${execution.id}`)}
          className="text-blue-600 hover:text-blue-800 font-mono text-sm"
        >
          {execution.id.substring(0, 8)}
        </button>
      ),
    },
    {
      key: 'status',
      label: 'Status',
      render: (execution) => {
        const variants = {
          completed: 'success',
          running: 'primary',
          failed: 'error',
          pending: 'warning',
        };
        return (
          <Badge variant={variants[execution.status] || 'secondary'}>
            {execution.status}
          </Badge>
        );
      },
    },
    {
      key: 'started_at',
      label: 'Started',
      render: (execution) => formatRelativeTime(execution.started_at),
    },
    {
      key: 'duration',
      label: 'Duration',
      render: (execution) => {
        if (execution.completed_at && execution.started_at) {
          const duration = new Date(execution.completed_at) - new Date(execution.started_at);
          return `${(duration / 1000).toFixed(2)}s`;
        }
        return execution.status === 'running' ? 'Running...' : '-';
      },
    },
  ];

  /**
   * Version columns
   */
  const versionColumns = [
    {
      key: 'version',
      label: 'Version',
      render: (version) => (
        <span className="font-mono font-medium">v{version.version}</span>
      ),
    },
    {
      key: 'description',
      label: 'Description',
    },
    {
      key: 'created_by',
      label: 'Created By',
      render: (version) => version.created_by?.email || '-',
    },
    {
      key: 'created_at',
      label: 'Created',
      render: (version) => formatDate(version.created_at),
    },
    {
      key: 'actions',
      label: '',
      render: (version) => (
        <Button size="sm" variant="outline">
          Restore
        </Button>
      ),
    },
  ];

  if (loading) {
    return <Loading.LoadingPage />;
  }

  if (!workflow) {
    return (
      <div className="max-w-7xl mx-auto py-12 text-center">
        <p className="text-gray-500">Workflow not found</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate(ROUTES.WORKFLOWS)}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeftIcon className="w-4 h-4 mr-2" />
          Back to Workflows
        </button>

        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold text-gray-900">
                {workflow.name}
              </h1>
              <Badge variant={getStatusVariant(workflow.status)}>
                {workflow.status}
              </Badge>
            </div>
            {workflow.description && (
              <p className="text-gray-600 mt-2">{workflow.description}</p>
            )}
            <div className="flex items-center gap-4 mt-4 text-sm text-gray-500">
              <span>Created {formatRelativeTime(workflow.created_at)}</span>
              <span>•</span>
              <span>Updated {formatRelativeTime(workflow.updated_at)}</span>
              <span>•</span>
              <span>{executions.length} executions</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate(`${ROUTES.WORKFLOW_BUILDER}/${id}`)}
            >
              <PencilIcon className="w-4 h-4 mr-2" />
              Edit
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleDuplicate}
            >
              <DocumentDuplicateIcon className="w-4 h-4 mr-2" />
              Duplicate
            </Button>
            <Button size="sm" onClick={handleExecute}>
              <PlayIcon className="w-4 h-4 mr-2" />
              Run Workflow
            </Button>
            <button
              onClick={() => setDeleteModalOpen(true)}
              className="p-2 text-gray-400 hover:text-red-600 rounded-lg hover:bg-red-50 transition-colors"
            >
              <TrashIcon className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex gap-6">
          {['overview', 'executions', 'versions'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`pb-3 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === tab
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div>
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card>
                <div className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">
                        Total Executions
                      </p>
                      <p className="text-3xl font-bold text-gray-900 mt-2">
                        {executions.length}
                      </p>
                    </div>
                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                      <PlayIcon className="w-6 h-6 text-blue-600" />
                    </div>
                  </div>
                </div>
              </Card>

              <Card>
                <div className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">
                        Success Rate
                      </p>
                      <p className="text-3xl font-bold text-gray-900 mt-2">
                        {executions.length > 0
                          ? Math.round(
                              (executions.filter((e) => e.status === 'completed')
                                .length /
                                executions.length) *
                                100
                            )
                          : 0}
                        %
                      </p>
                    </div>
                    <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                      <CheckCircleIcon className="w-6 h-6 text-green-600" />
                    </div>
                  </div>
                </div>
              </Card>

              <Card>
                <div className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">
                        Last Execution
                      </p>
                      <p className="text-lg font-bold text-gray-900 mt-2">
                        {executions[0]
                          ? formatRelativeTime(executions[0].started_at)
                          : 'Never'}
                      </p>
                    </div>
                    <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                      <ClockIcon className="w-6 h-6 text-purple-600" />
                    </div>
                  </div>
                </div>
              </Card>
            </div>

            {/* Workflow Definition */}
            <Card>
              <div className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Workflow Definition
                </h3>
                {workflow.definition ? (
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-600">Nodes:</span>
                        <span className="ml-2 font-medium">
                          {workflow.definition.nodes?.length || 0}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-600">Connections:</span>
                        <span className="ml-2 font-medium">
                          {workflow.definition.connections?.length || 0}
                        </span>
                      </div>
                    </div>
                    <details>
                      <summary className="text-sm font-medium text-gray-700 cursor-pointer hover:text-gray-900">
                        View JSON Definition
                      </summary>
                      <pre className="mt-2 p-4 bg-gray-50 rounded-lg text-xs overflow-auto max-h-96">
                        {JSON.stringify(workflow.definition, null, 2)}
                      </pre>
                    </details>
                  </div>
                ) : (
                  <p className="text-gray-500 text-sm">
                    No workflow definition available
                  </p>
                )}
              </div>
            </Card>
          </div>
        )}

        {/* Executions Tab */}
        {activeTab === 'executions' && (
          <Card>
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-gray-900">
                  Recent Executions
                </h3>
                <Button size="sm" onClick={handleExecute}>
                  <PlayIcon className="w-4 h-4 mr-2" />
                  New Execution
                </Button>
              </div>

              {executions.length > 0 ? (
                <DataTable
                  data={executions}
                  columns={executionColumns}
                  onRowClick={(execution) =>
                    navigate(`${ROUTES.EXECUTION_DETAIL}/${execution.id}`)
                  }
                />
              ) : (
                <div className="text-center py-12">
                  <p className="text-gray-500">No executions yet</p>
                  <Button
                    size="sm"
                    variant="outline"
                    className="mt-4"
                    onClick={handleExecute}
                  >
                    Run First Execution
                  </Button>
                </div>
              )}
            </div>
          </Card>
        )}

        {/* Versions Tab */}
        {activeTab === 'versions' && (
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-6">
                Version History
              </h3>

              {versions.length > 0 ? (
                <DataTable data={versions} columns={versionColumns} />
              ) : (
                <div className="text-center py-12">
                  <p className="text-gray-500">No version history available</p>
                </div>
              )}
            </div>
          </Card>
        )}
      </div>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={deleteModalOpen}
        onClose={() => setDeleteModalOpen(false)}
        title="Delete Workflow"
        maxWidth="md"
      >
        <div className="space-y-4">
          <p className="text-gray-600">
            Are you sure you want to delete <strong>{workflow.name}</strong>?
            This action cannot be undone.
          </p>

          <div className="flex justify-end gap-3 pt-4 border-t">
            <Button
              variant="outline"
              onClick={() => setDeleteModalOpen(false)}
              disabled={deleting}
            >
              Cancel
            </Button>
            <Button variant="error" onClick={handleDelete} disabled={deleting}>
              {deleting ? (
                <>
                  <Loading.Spinner size="sm" className="mr-2" />
                  Deleting...
                </>
              ) : (
                <>
                  <TrashIcon className="w-4 h-4 mr-2" />
                  Delete Workflow
                </>
              )}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
