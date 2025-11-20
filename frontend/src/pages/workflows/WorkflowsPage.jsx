import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { PlusIcon, PlayIcon, PencilIcon, TrashIcon, DocumentDuplicateIcon } from '@heroicons/react/24/outline';
import {
  fetchWorkflows,
  deleteWorkflow,
  duplicateWorkflow,
  executeWorkflow,
} from '@/store/slices/workflowsSlice';
import DataTable from '@/components/ui/DataTable';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';
import Modal, { ConfirmModal } from '@/components/ui/Modal';
import { FormInput, FormSelect, FormTextarea } from '@/components/ui/Form';
import { ROUTES } from '@/constants/routes';
import { formatRelativeTime } from '@/utils/formatters';
import toast from 'react-hot-toast';

export default function WorkflowsPage() {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { workflows, loading } = useSelector((state) => state.workflows);

  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [executeModalOpen, setExecuteModalOpen] = useState(false);
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [selectedWorkflow, setSelectedWorkflow] = useState(null);
  const [executeInput, setExecuteInput] = useState('{}');

  const [newWorkflow, setNewWorkflow] = useState({
    name: '',
    description: '',
    category: '',
  });

  useEffect(() => {
    dispatch(fetchWorkflows());
  }, [dispatch]);

  const handleCreateWorkflow = async () => {
    if (!newWorkflow.name) {
      toast.error('Please enter a workflow name');
      return;
    }

    navigate('/workflows/builder', { state: { workflow: newWorkflow } });
    setCreateModalOpen(false);
  };

  const handleDeleteWorkflow = async () => {
    try {
      await dispatch(deleteWorkflow(selectedWorkflow.id)).unwrap();
      toast.success('Workflow deleted successfully');
      setDeleteModalOpen(false);
      setSelectedWorkflow(null);
    } catch (error) {
      toast.error(error || 'Failed to delete workflow');
    }
  };

  const handleDuplicateWorkflow = async (workflow) => {
    try {
      await dispatch(duplicateWorkflow(workflow.id)).unwrap();
      toast.success('Workflow duplicated successfully');
    } catch (error) {
      toast.error(error || 'Failed to duplicate workflow');
    }
  };

  const handleExecuteWorkflow = async () => {
    try {
      const input = JSON.parse(executeInput);
      await dispatch(executeWorkflow({ id: selectedWorkflow.id, input })).unwrap();
      toast.success('Workflow execution started');
      setExecuteModalOpen(false);
      setSelectedWorkflow(null);
      setExecuteInput('{}');
    } catch (error) {
      if (error instanceof SyntaxError) {
        toast.error('Invalid JSON input');
      } else {
        toast.error(error || 'Failed to execute workflow');
      }
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      active: { variant: 'success', label: 'Active' },
      draft: { variant: 'warning', label: 'Draft' },
      archived: { variant: 'secondary', label: 'Archived' },
      inactive: { variant: 'secondary', label: 'Inactive' },
    };

    const config = statusConfig[status] || statusConfig.draft;
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  const columns = [
    {
      key: 'name',
      label: 'Name',
      render: (value, row) => (
        <div className="flex flex-col">
          <span className="font-medium text-gray-900">{value}</span>
          {row.description && (
            <span className="text-sm text-gray-500 truncate max-w-md">{row.description}</span>
          )}
        </div>
      ),
    },
    {
      key: 'category',
      label: 'Category',
      render: (value) => (
        <Badge variant="outline">{value || 'Uncategorized'}</Badge>
      ),
    },
    {
      key: 'status',
      label: 'Status',
      render: (value) => getStatusBadge(value),
    },
    {
      key: 'executions_count',
      label: 'Executions',
      render: (value) => (
        <span className="text-sm text-gray-900">{value || 0}</span>
      ),
    },
    {
      key: 'success_rate',
      label: 'Success Rate',
      render: (value) => (
        <span className="text-sm text-gray-900">{value ? `${value}%` : 'N/A'}</span>
      ),
    },
    {
      key: 'updated_at',
      label: 'Last Updated',
      render: (value) => (
        <span className="text-sm text-gray-500">{formatRelativeTime(value)}</span>
      ),
    },
    {
      key: 'actions',
      label: 'Actions',
      sortable: false,
      render: (_, row) => (
        <div className="flex items-center space-x-2">
          <Button
            variant="ghost"
            size="sm"
            leftIcon={PlayIcon}
            onClick={(e) => {
              e.stopPropagation();
              setSelectedWorkflow(row);
              setExecuteModalOpen(true);
            }}
            title="Execute"
          />
          <Button
            variant="ghost"
            size="sm"
            leftIcon={PencilIcon}
            onClick={(e) => {
              e.stopPropagation();
              navigate(`/workflows/${row.id}/builder`);
            }}
            title="Edit"
          />
          <Button
            variant="ghost"
            size="sm"
            leftIcon={DocumentDuplicateIcon}
            onClick={(e) => {
              e.stopPropagation();
              handleDuplicateWorkflow(row);
            }}
            title="Duplicate"
          />
          <Button
            variant="ghost"
            size="sm"
            leftIcon={TrashIcon}
            onClick={(e) => {
              e.stopPropagation();
              setSelectedWorkflow(row);
              setDeleteModalOpen(true);
            }}
            className="text-error-600 hover:text-error-700"
            title="Delete"
          />
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Workflows</h1>
          <p className="mt-1 text-sm text-gray-500">
            Create and manage AI-powered workflow automations
          </p>
        </div>
        <Button
          leftIcon={PlusIcon}
          onClick={() => setCreateModalOpen(true)}
        >
          Create Workflow
        </Button>
      </div>

      {/* Workflows Table */}
      <DataTable
        data={workflows}
        columns={columns}
        loading={loading}
        searchable
        filterable
        pagination
        onRowClick={(row) => navigate(`/workflows/${row.id}`)}
        emptyMessage="No workflows found. Create your first workflow to get started."
      />

      {/* Create Workflow Modal */}
      <Modal
        isOpen={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        title="Create New Workflow"
      >
        <div className="space-y-4">
          <FormInput
            label="Workflow Name"
            required
            placeholder="Enter workflow name"
            value={newWorkflow.name}
            onChange={(e) => setNewWorkflow({ ...newWorkflow, name: e.target.value })}
          />
          <FormTextarea
            label="Description"
            placeholder="Describe what this workflow does"
            rows={3}
            value={newWorkflow.description}
            onChange={(e) => setNewWorkflow({ ...newWorkflow, description: e.target.value })}
          />
          <FormSelect
            label="Category"
            placeholder="Select a category"
            value={newWorkflow.category}
            onChange={(e) => setNewWorkflow({ ...newWorkflow, category: e.target.value })}
            options={[
              { label: 'Email Automation', value: 'email' },
              { label: 'Data Processing', value: 'data' },
              { label: 'Document Processing', value: 'document' },
              { label: 'Integration', value: 'integration' },
              { label: 'Analytics', value: 'analytics' },
              { label: 'Other', value: 'other' },
            ]}
          />
        </div>
        <div className="mt-6 flex justify-end space-x-3">
          <Button variant="outline" onClick={() => setCreateModalOpen(false)}>
            Cancel
          </Button>
          <Button onClick={handleCreateWorkflow}>
            Create & Build
          </Button>
        </div>
      </Modal>

      {/* Execute Workflow Modal */}
      <Modal
        isOpen={executeModalOpen}
        onClose={() => setExecuteModalOpen(false)}
        title="Execute Workflow"
      >
        <div className="space-y-4">
          <p className="text-sm text-gray-600">
            Executing: <span className="font-medium">{selectedWorkflow?.name}</span>
          </p>
          <FormTextarea
            label="Input Data (JSON)"
            rows={8}
            value={executeInput}
            onChange={(e) => setExecuteInput(e.target.value)}
            placeholder='{"key": "value"}'
            className="font-mono text-sm"
          />
          <p className="text-xs text-gray-500">
            Provide input data as JSON. Leave empty for no input.
          </p>
        </div>
        <div className="mt-6 flex justify-end space-x-3">
          <Button variant="outline" onClick={() => setExecuteModalOpen(false)}>
            Cancel
          </Button>
          <Button onClick={handleExecuteWorkflow} leftIcon={PlayIcon}>
            Execute
          </Button>
        </div>
      </Modal>

      {/* Delete Confirmation Modal */}
      <ConfirmModal
        isOpen={deleteModalOpen}
        onClose={() => setDeleteModalOpen(false)}
        onConfirm={handleDeleteWorkflow}
        title="Delete Workflow"
        message={`Are you sure you want to delete "${selectedWorkflow?.name}"? This action cannot be undone.`}
        confirmText="Delete"
        variant="danger"
      />
    </div>
  );
}
