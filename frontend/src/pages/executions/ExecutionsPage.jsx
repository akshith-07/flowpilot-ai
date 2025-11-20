import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { ArrowPathIcon, XMarkIcon } from '@heroicons/react/24/outline';
import {
  fetchExecutions,
  retryExecution,
  cancelExecution,
} from '@/store/slices/executionsSlice';
import DataTable from '@/components/ui/DataTable';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';
import { ConfirmModal } from '@/components/ui/Modal';
import { FormSelect } from '@/components/ui/Form';
import { formatRelativeTime, formatDuration } from '@/utils/formatters';
import toast from 'react-hot-toast';

export default function ExecutionsPage() {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { executions, loading } = useSelector((state) => state.executions);

  const [cancelModalOpen, setCancelModalOpen] = useState(false);
  const [selectedExecution, setSelectedExecution] = useState(null);
  const [statusFilter, setStatusFilter] = useState('');

  useEffect(() => {
    dispatch(fetchExecutions({ status: statusFilter }));
  }, [dispatch, statusFilter]);

  const handleRetry = async (execution) => {
    try {
      await dispatch(retryExecution(execution.id)).unwrap();
      toast.success('Execution retried successfully');
    } catch (error) {
      toast.error(error || 'Failed to retry execution');
    }
  };

  const handleCancel = async () => {
    try {
      await dispatch(cancelExecution(selectedExecution.id)).unwrap();
      toast.success('Execution cancelled');
      setCancelModalOpen(false);
      setSelectedExecution(null);
    } catch (error) {
      toast.error(error || 'Failed to cancel execution');
    }
  };

  const getStatusBadge = (status) => {
    const config = {
      running: { variant: 'primary', label: 'Running' },
      completed: { variant: 'success', label: 'Completed' },
      failed: { variant: 'error', label: 'Failed' },
      cancelled: { variant: 'secondary', label: 'Cancelled' },
      pending: { variant: 'warning', label: 'Pending' },
    };
    const statusConfig = config[status] || config.pending;
    return <Badge variant={statusConfig.variant}>{statusConfig.label}</Badge>;
  };

  const columns = [
    {
      key: 'workflow_name',
      label: 'Workflow',
      render: (value, row) => (
        <div className="flex flex-col">
          <span className="font-medium text-gray-900">{value}</span>
          <span className="text-xs text-gray-500">ID: {row.id?.slice(0, 8)}</span>
        </div>
      ),
    },
    {
      key: 'status',
      label: 'Status',
      render: (value) => getStatusBadge(value),
    },
    {
      key: 'started_at',
      label: 'Started',
      render: (value) => (
        <span className="text-sm text-gray-500">{formatRelativeTime(value)}</span>
      ),
    },
    {
      key: 'duration',
      label: 'Duration',
      render: (value, row) => {
        if (row.status === 'running') return <Badge variant="primary">Running</Badge>;
        return <span className="text-sm text-gray-900">{formatDuration(value)}</span>;
      },
    },
    {
      key: 'steps_completed',
      label: 'Progress',
      render: (value, row) => (
        <span className="text-sm text-gray-900">{value || 0} / {row.total_steps || 0}</span>
      ),
    },
    {
      key: 'actions',
      label: 'Actions',
      sortable: false,
      render: (_, row) => (
        <div className="flex items-center space-x-2">
          {(row.status === 'failed' || row.status === 'cancelled') && (
            <Button
              variant="ghost"
              size="sm"
              leftIcon={ArrowPathIcon}
              onClick={(e) => {
                e.stopPropagation();
                handleRetry(row);
              }}
              title="Retry"
            />
          )}
          {row.status === 'running' && (
            <Button
              variant="ghost"
              size="sm"
              leftIcon={XMarkIcon}
              onClick={(e) => {
                e.stopPropagation();
                setSelectedExecution(row);
                setCancelModalOpen(true);
              }}
              className="text-error-600 hover:text-error-700"
              title="Cancel"
            />
          )}
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Executions</h1>
          <p className="mt-1 text-sm text-gray-500">Monitor and manage workflow executions</p>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        <FormSelect
          placeholder="All Statuses"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          options={[
            { label: 'Running', value: 'running' },
            { label: 'Completed', value: 'completed' },
            { label: 'Failed', value: 'failed' },
            { label: 'Cancelled', value: 'cancelled' },
            { label: 'Pending', value: 'pending' },
          ]}
          className="w-48"
        />
      </div>

      <DataTable
        data={executions}
        columns={columns}
        loading={loading}
        searchable
        pagination
        onRowClick={(row) => navigate(`/executions/${row.id}`)}
        emptyMessage="No executions found"
      />

      <ConfirmModal
        isOpen={cancelModalOpen}
        onClose={() => setCancelModalOpen(false)}
        onConfirm={handleCancel}
        title="Cancel Execution"
        message="Are you sure you want to cancel this execution?"
        confirmText="Cancel Execution"
        variant="danger"
      />
    </div>
  );
}
