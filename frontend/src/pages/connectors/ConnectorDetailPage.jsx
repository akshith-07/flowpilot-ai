/**
 * ConnectorDetailPage Component
 * Detailed view of a connector with configuration, webhooks, and sync logs
 */

import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeftIcon,
  LinkIcon,
  WrenchScrewdriverIcon,
  BoltIcon,
  ClockIcon,
  PlusIcon,
  TrashIcon,
  CheckCircleIcon,
  XCircleIcon,
} from '@heroicons/react/24/outline';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';
import Card, { CardHeader, CardTitle, CardDescription, CardBody } from '@/components/ui/Card';
import Modal, { ConfirmModal } from '@/components/ui/Modal';
import DataTable from '@/components/ui/DataTable';
import { FormInput, FormTextarea } from '@/components/ui/Form';
import connectorService from '@/services/connectorService';
import { formatDate, formatRelativeTime } from '@/utils/formatters';
import toast from 'react-hot-toast';

/**
 * ConnectorDetailPage Component
 */
export default function ConnectorDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [connector, setConnector] = useState(null);
  const [webhooks, setWebhooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [testingConnection, setTestingConnection] = useState(false);
  const [createWebhookModalOpen, setCreateWebhookModalOpen] = useState(false);
  const [deleteWebhookModalOpen, setDeleteWebhookModalOpen] = useState(false);
  const [selectedWebhook, setSelectedWebhook] = useState(null);
  const [activeTab, setActiveTab] = useState('details');

  const [webhookForm, setWebhookForm] = useState({
    url: '',
    event_types: '',
    description: '',
  });

  useEffect(() => {
    fetchConnector();
    fetchWebhooks();
  }, [id]);

  const fetchConnector = async () => {
    try {
      setLoading(true);
      const response = await connectorService.getConnectorById(id);
      setConnector(response.data);
    } catch (error) {
      toast.error(error.message || 'Failed to fetch connector');
      navigate('/connectors');
    } finally {
      setLoading(false);
    }
  };

  const fetchWebhooks = async () => {
    try {
      const response = await connectorService.getWebhooks(id);
      setWebhooks(response.data || []);
    } catch (error) {
      console.error('Failed to fetch webhooks:', error);
    }
  };

  const handleTestConnection = async () => {
    try {
      setTestingConnection(true);
      await connectorService.testConnection(id);
      toast.success('Connection test successful');
    } catch (error) {
      toast.error(error.message || 'Connection test failed');
    } finally {
      setTestingConnection(false);
    }
  };

  const handleCreateWebhook = async () => {
    try {
      const eventTypes = webhookForm.event_types.split(',').map((e) => e.trim());
      await connectorService.registerWebhook(id, {
        url: webhookForm.url,
        event_types: eventTypes,
        description: webhookForm.description,
      });
      toast.success('Webhook created successfully');
      setCreateWebhookModalOpen(false);
      setWebhookForm({ url: '', event_types: '', description: '' });
      fetchWebhooks();
    } catch (error) {
      toast.error(error.message || 'Failed to create webhook');
    }
  };

  const handleDeleteWebhook = async () => {
    try {
      await connectorService.deleteWebhook(selectedWebhook.id);
      toast.success('Webhook deleted successfully');
      setDeleteWebhookModalOpen(false);
      setSelectedWebhook(null);
      fetchWebhooks();
    } catch (error) {
      toast.error(error.message || 'Failed to delete webhook');
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      connected: { variant: 'success', label: 'Connected', icon: CheckCircleIcon },
      disconnected: { variant: 'error', label: 'Disconnected', icon: XCircleIcon },
      error: { variant: 'error', label: 'Error', icon: XCircleIcon },
    };
    const config = statusConfig[status] || statusConfig.disconnected;
    const Icon = config.icon;
    return (
      <Badge variant={config.variant}>
        <Icon className="w-3 h-3 inline mr-1" />
        {config.label}
      </Badge>
    );
  };

  const tabs = [
    { id: 'details', label: 'Details', icon: WrenchScrewdriverIcon },
    { id: 'webhooks', label: 'Webhooks', icon: BoltIcon },
    { id: 'logs', label: 'Sync Logs', icon: ClockIcon },
  ];

  const webhookColumns = [
    {
      key: 'url',
      label: 'Webhook URL',
      render: (value) => (
        <span className="font-mono text-sm text-gray-900">{value}</span>
      ),
    },
    {
      key: 'event_types',
      label: 'Event Types',
      render: (value) => (
        <div className="flex flex-wrap gap-1">
          {value?.map((event, index) => (
            <Badge key={index} variant="secondary" size="sm">{event}</Badge>
          ))}
        </div>
      ),
    },
    {
      key: 'status',
      label: 'Status',
      render: (value) => getStatusBadge(value),
    },
    {
      key: 'created_at',
      label: 'Created',
      render: (value) => (
        <span className="text-sm text-gray-500">{formatRelativeTime(value)}</span>
      ),
    },
    {
      key: 'actions',
      label: 'Actions',
      sortable: false,
      render: (_, row) => (
        <Button
          variant="ghost"
          size="sm"
          leftIcon={TrashIcon}
          onClick={(e) => {
            e.stopPropagation();
            setSelectedWebhook(row);
            setDeleteWebhookModalOpen(true);
          }}
          className="text-error-600 hover:text-error-700"
          title="Delete"
        />
      ),
    },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!connector) {
    return null;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button
            variant="ghost"
            leftIcon={ArrowLeftIcon}
            onClick={() => navigate('/connectors')}
          >
            Back
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {connector.provider} Connector
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              Connector ID: {connector.id}
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <Button
            variant="outline"
            onClick={handleTestConnection}
            loading={testingConnection}
          >
            Test Connection
          </Button>
        </div>
      </div>

      {/* Status Card */}
      <Card>
        <CardBody>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div>
              <p className="text-sm font-medium text-gray-500">Status</p>
              <div className="mt-1">{getStatusBadge(connector.status)}</div>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Provider</p>
              <p className="mt-1 text-sm text-gray-900">{connector.provider}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Last Synced</p>
              <p className="mt-1 text-sm text-gray-900">
                {connector.last_sync_at ? formatRelativeTime(connector.last_sync_at) : 'Never'}
              </p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Connected</p>
              <p className="mt-1 text-sm text-gray-900">{formatDate(connector.created_at)}</p>
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm
                  ${
                    activeTab === tab.id
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <Icon className="w-5 h-5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        {/* Details Tab */}
        {activeTab === 'details' && (
          <Card>
            <CardHeader>
              <CardTitle>Connector Details</CardTitle>
              <CardDescription>
                Configuration and settings for this connector
              </CardDescription>
            </CardHeader>
            <CardBody>
              <dl className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <dt className="text-sm font-medium text-gray-500">Connector ID</dt>
                  <dd className="mt-1 text-sm text-gray-900 font-mono">{connector.id}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Provider</dt>
                  <dd className="mt-1 text-sm text-gray-900">{connector.provider}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Status</dt>
                  <dd className="mt-1">{getStatusBadge(connector.status)}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Created At</dt>
                  <dd className="mt-1 text-sm text-gray-900">{formatDate(connector.created_at)}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Last Updated</dt>
                  <dd className="mt-1 text-sm text-gray-900">{formatDate(connector.updated_at)}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Last Sync</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {connector.last_sync_at ? formatDate(connector.last_sync_at) : 'Never'}
                  </dd>
                </div>
                {connector.settings && Object.keys(connector.settings).length > 0 && (
                  <>
                    {Object.entries(connector.settings).map(([key, value]) => (
                      <div key={key}>
                        <dt className="text-sm font-medium text-gray-500">{key}</dt>
                        <dd className="mt-1 text-sm text-gray-900">{String(value)}</dd>
                      </div>
                    ))}
                  </>
                )}
              </dl>
            </CardBody>
          </Card>
        )}

        {/* Webhooks Tab */}
        {activeTab === 'webhooks' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Webhooks</h3>
                <p className="text-sm text-gray-500">
                  Configure webhooks to receive real-time notifications
                </p>
              </div>
              <Button
                leftIcon={PlusIcon}
                onClick={() => setCreateWebhookModalOpen(true)}
              >
                Create Webhook
              </Button>
            </div>

            <DataTable
              data={webhooks}
              columns={webhookColumns}
              emptyMessage="No webhooks configured"
            />
          </div>
        )}

        {/* Logs Tab */}
        {activeTab === 'logs' && (
          <Card>
            <CardHeader>
              <CardTitle>Sync Logs</CardTitle>
              <CardDescription>
                History of synchronization activities
              </CardDescription>
            </CardHeader>
            <CardBody>
              <div className="text-center py-12">
                <ClockIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-sm text-gray-500">No sync logs available</p>
              </div>
            </CardBody>
          </Card>
        )}
      </div>

      {/* Create Webhook Modal */}
      <Modal
        isOpen={createWebhookModalOpen}
        onClose={() => setCreateWebhookModalOpen(false)}
        title="Create Webhook"
      >
        <div className="space-y-4">
          <FormInput
            label="Webhook URL"
            required
            placeholder="https://your-domain.com/webhooks"
            value={webhookForm.url}
            onChange={(e) => setWebhookForm({ ...webhookForm, url: e.target.value })}
          />
          <FormInput
            label="Event Types"
            required
            placeholder="created, updated, deleted (comma-separated)"
            value={webhookForm.event_types}
            onChange={(e) => setWebhookForm({ ...webhookForm, event_types: e.target.value })}
          />
          <FormTextarea
            label="Description"
            placeholder="Describe what this webhook is used for"
            rows={3}
            value={webhookForm.description}
            onChange={(e) => setWebhookForm({ ...webhookForm, description: e.target.value })}
          />
        </div>
        <div className="mt-6 flex justify-end space-x-3">
          <Button variant="outline" onClick={() => setCreateWebhookModalOpen(false)}>
            Cancel
          </Button>
          <Button onClick={handleCreateWebhook}>
            Create
          </Button>
        </div>
      </Modal>

      {/* Delete Webhook Confirmation Modal */}
      <ConfirmModal
        isOpen={deleteWebhookModalOpen}
        onClose={() => setDeleteWebhookModalOpen(false)}
        onConfirm={handleDeleteWebhook}
        title="Delete Webhook"
        message={`Are you sure you want to delete this webhook? This action cannot be undone.`}
        confirmText="Delete"
        variant="danger"
      />
    </div>
  );
}
