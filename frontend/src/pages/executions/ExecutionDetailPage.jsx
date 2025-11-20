/**
 * ExecutionDetailPage Component
 * Detailed view of workflow execution with real-time logs and timeline
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeftIcon,
  ArrowPathIcon,
  XCircleIcon,
  DocumentDuplicateIcon,
} from '@heroicons/react/24/outline';
import { Button, Card, Badge, Loading } from '@components/ui';
import ExecutionTimeline from '@components/executions/ExecutionTimeline';
import { executionService, workflowService } from '@services';
import { ROUTES } from '@constants';
import { formatDate, formatRelativeTime, formatDuration } from '@utils/formatters';
import { useWebSocket } from '@hooks';
import toast from 'react-hot-toast';

/**
 * ExecutionDetailPage Component
 */
export default function ExecutionDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [execution, setExecution] = useState(null);
  const [workflow, setWorkflow] = useState(null);
  const [steps, setSteps] = useState([]);
  const [logs, setLogs] = useState([]);
  const [activeTab, setActiveTab] = useState('timeline');
  const [retrying, setRetrying] = useState(false);
  const [canceling, setCanceling] = useState(false);

  /**
   * WebSocket for real-time updates
   */
  const { connected } = useWebSocket({
    url: `/ws/executions/${id}/`,
    onMessage: handleWebSocketMessage,
    enabled: execution?.status === 'running',
  });

  /**
   * Load execution details
   */
  useEffect(() => {
    loadExecutionDetails();
  }, [id]);

  /**
   * Poll for updates if execution is running
   */
  useEffect(() => {
    let interval;
    if (execution?.status === 'running' && !connected) {
      interval = setInterval(loadExecutionDetails, 3000);
    }
    return () => clearInterval(interval);
  }, [execution?.status, connected]);

  /**
   * Handle WebSocket message
   */
  function handleWebSocketMessage(data) {
    if (data.type === 'execution_update') {
      setExecution((prev) => ({ ...prev, ...data.execution }));
    } else if (data.type === 'step_update') {
      setSteps((prev) =>
        prev.map((step) =>
          step.id === data.step.id ? { ...step, ...data.step } : step
        )
      );
    } else if (data.type === 'log') {
      setLogs((prev) => [...prev, data.log]);
    }
  }

  /**
   * Load execution details
   */
  const loadExecutionDetails = async () => {
    try {
      setLoading(true);
      const executionData = await executionService.getExecutionById(id);
      setExecution(executionData);

      // Load workflow
      if (executionData.workflow_id) {
        try {
          const workflowData = await workflowService.getWorkflowById(
            executionData.workflow_id
          );
          setWorkflow(workflowData);
        } catch (error) {
          console.error('Error loading workflow:', error);
        }
      }

      // Load steps
      if (executionData.steps) {
        setSteps(executionData.steps);
      }

      // Load logs
      if (executionData.logs) {
        setLogs(executionData.logs);
      }
    } catch (error) {
      console.error('Error loading execution:', error);
      toast.error('Failed to load execution details');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle retry execution
   */
  const handleRetry = async () => {
    try {
      setRetrying(true);
      const newExecution = await executionService.retryExecution(id);
      toast.success('Execution retried successfully');
      navigate(`${ROUTES.EXECUTION_DETAIL}/${newExecution.id}`);
    } catch (error) {
      console.error('Error retrying execution:', error);
      toast.error('Failed to retry execution');
      setRetrying(false);
    }
  };

  /**
   * Handle cancel execution
   */
  const handleCancel = async () => {
    try {
      setCanceling(true);
      await executionService.cancelExecution(id);
      toast.success('Execution canceled successfully');
      loadExecutionDetails();
    } catch (error) {
      console.error('Error canceling execution:', error);
      toast.error('Failed to cancel execution');
    } finally {
      setCanceling(false);
    }
  };

  /**
   * Get status badge variant
   */
  const getStatusVariant = (status) => {
    const variants = {
      completed: 'success',
      running: 'primary',
      failed: 'error',
      pending: 'warning',
      canceled: 'secondary',
    };
    return variants[status] || 'secondary';
  };

  /**
   * Calculate progress
   */
  const calculateProgress = () => {
    if (steps.length === 0) return 0;
    const completed = steps.filter(
      (s) => s.status === 'completed' || s.status === 'failed'
    ).length;
    return Math.round((completed / steps.length) * 100);
  };

  if (loading) {
    return <Loading.LoadingPage />;
  }

  if (!execution) {
    return (
      <div className="max-w-7xl mx-auto py-12 text-center">
        <p className="text-gray-500">Execution not found</p>
      </div>
    );
  }

  const progress = calculateProgress();
  const duration =
    execution.completed_at && execution.started_at
      ? new Date(execution.completed_at) - new Date(execution.started_at)
      : execution.started_at
      ? Date.now() - new Date(execution.started_at)
      : null;

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate(ROUTES.EXECUTIONS)}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeftIcon className="w-4 h-4 mr-2" />
          Back to Executions
        </button>

        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-2xl font-bold text-gray-900">
                Execution #{execution.id.substring(0, 8)}
              </h1>
              <Badge variant={getStatusVariant(execution.status)}>
                {execution.status}
              </Badge>
              {connected && (
                <Badge variant="success">
                  <span className="flex items-center gap-1">
                    <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                    Live
                  </span>
                </Badge>
              )}
            </div>

            {workflow && (
              <button
                onClick={() =>
                  navigate(`${ROUTES.WORKFLOW_DETAIL}/${workflow.id}`)
                }
                className="text-blue-600 hover:text-blue-800 font-medium"
              >
                {workflow.name}
              </button>
            )}

            <div className="flex items-center gap-4 mt-3 text-sm text-gray-500">
              <span>Started {formatRelativeTime(execution.started_at)}</span>
              {duration && (
                <>
                  <span>•</span>
                  <span>Duration: {formatDuration(duration)}</span>
                </>
              )}
              {execution.triggered_by && (
                <>
                  <span>•</span>
                  <span>By {execution.triggered_by}</span>
                </>
              )}
            </div>
          </div>

          <div className="flex items-center gap-3">
            {execution.status === 'running' && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleCancel}
                disabled={canceling}
              >
                {canceling ? (
                  <>
                    <Loading.Spinner size="sm" className="mr-2" />
                    Canceling...
                  </>
                ) : (
                  <>
                    <XCircleIcon className="w-4 h-4 mr-2" />
                    Cancel
                  </>
                )}
              </Button>
            )}

            {(execution.status === 'failed' || execution.status === 'canceled') && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleRetry}
                disabled={retrying}
              >
                {retrying ? (
                  <>
                    <Loading.Spinner size="sm" className="mr-2" />
                    Retrying...
                  </>
                ) : (
                  <>
                    <ArrowPathIcon className="w-4 h-4 mr-2" />
                    Retry
                  </>
                )}
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      {execution.status === 'running' && (
        <div className="mb-6">
          <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
            <span>Progress</span>
            <span>{progress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card>
          <div className="p-4">
            <p className="text-sm text-gray-600">Total Steps</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">
              {steps.length}
            </p>
          </div>
        </Card>

        <Card>
          <div className="p-4">
            <p className="text-sm text-gray-600">Completed</p>
            <p className="text-2xl font-bold text-green-600 mt-1">
              {steps.filter((s) => s.status === 'completed').length}
            </p>
          </div>
        </Card>

        <Card>
          <div className="p-4">
            <p className="text-sm text-gray-600">Failed</p>
            <p className="text-2xl font-bold text-red-600 mt-1">
              {steps.filter((s) => s.status === 'failed').length}
            </p>
          </div>
        </Card>

        <Card>
          <div className="p-4">
            <p className="text-sm text-gray-600">Duration</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">
              {duration ? formatDuration(duration) : '-'}
            </p>
          </div>
        </Card>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex gap-6">
          {['timeline', 'logs', 'data'].map((tab) => (
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
        {/* Timeline Tab */}
        {activeTab === 'timeline' && (
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-6">
                Execution Timeline
              </h3>
              <ExecutionTimeline steps={steps} />
            </div>
          </Card>
        )}

        {/* Logs Tab */}
        {activeTab === 'logs' && (
          <Card>
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-gray-900">
                  Execution Logs
                </h3>
                <div className="text-sm text-gray-500">
                  {logs.length} log entries
                </div>
              </div>

              {logs.length > 0 ? (
                <div className="bg-gray-900 rounded-lg p-4 font-mono text-sm max-h-[600px] overflow-auto">
                  {logs.map((log, index) => (
                    <div key={index} className="mb-1">
                      <span className="text-gray-500">
                        {formatDate(log.timestamp)}
                      </span>
                      <span className="mx-2 text-gray-600">|</span>
                      <span
                        className={
                          log.level === 'ERROR'
                            ? 'text-red-400'
                            : log.level === 'WARNING'
                            ? 'text-yellow-400'
                            : log.level === 'INFO'
                            ? 'text-blue-400'
                            : 'text-gray-400'
                        }
                      >
                        {log.level}
                      </span>
                      <span className="mx-2 text-gray-600">|</span>
                      <span className="text-gray-300">{log.message}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <p className="text-gray-500">No logs available</p>
                </div>
              )}
            </div>
          </Card>
        )}

        {/* Data Tab */}
        {activeTab === 'data' && (
          <div className="space-y-6">
            {/* Input Data */}
            <Card>
              <div className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Input Data
                </h3>
                {execution.input ? (
                  <pre className="p-4 bg-gray-50 rounded-lg text-sm overflow-auto max-h-96">
                    {JSON.stringify(execution.input, null, 2)}
                  </pre>
                ) : (
                  <p className="text-gray-500">No input data</p>
                )}
              </div>
            </Card>

            {/* Output Data */}
            <Card>
              <div className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Output Data
                </h3>
                {execution.output ? (
                  <pre className="p-4 bg-gray-50 rounded-lg text-sm overflow-auto max-h-96">
                    {JSON.stringify(execution.output, null, 2)}
                  </pre>
                ) : (
                  <p className="text-gray-500">
                    {execution.status === 'running'
                      ? 'Waiting for execution to complete...'
                      : 'No output data'}
                  </p>
                )}
              </div>
            </Card>

            {/* Error Data */}
            {execution.error && (
              <Card>
                <div className="p-6">
                  <h3 className="text-lg font-semibold text-red-900 mb-4">
                    Error Details
                  </h3>
                  <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-sm text-red-700">{execution.error}</p>
                  </div>
                </div>
              </Card>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
