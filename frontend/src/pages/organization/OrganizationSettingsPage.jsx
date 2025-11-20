/**
 * OrganizationSettingsPage Component
 * Organization settings with API keys, webhooks, and billing information
 */

import { useEffect, useState } from 'react';
import {
  BuildingOfficeIcon,
  KeyIcon,
  GlobeAltIcon,
  CreditCardIcon,
  PlusIcon,
  TrashIcon,
  ClipboardDocumentIcon,
} from '@heroicons/react/24/outline';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';
import Card, { CardHeader, CardTitle, CardDescription, CardBody } from '@/components/ui/Card';
import Modal, { ConfirmModal } from '@/components/ui/Modal';
import DataTable from '@/components/ui/DataTable';
import { FormInput, FormSelect, FormTextarea } from '@/components/ui/Form';
import organizationService from '@/services/organizationService';
import { formatDate, formatRelativeTime } from '@/utils/formatters';
import toast from 'react-hot-toast';

/**
 * OrganizationSettingsPage Component
 */
export default function OrganizationSettingsPage() {
  const [organization, setOrganization] = useState(null);
  const [apiKeys, setApiKeys] = useState([]);
  const [billing, setBilling] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [createKeyModalOpen, setCreateKeyModalOpen] = useState(false);
  const [revokeKeyModalOpen, setRevokeKeyModalOpen] = useState(false);
  const [selectedKey, setSelectedKey] = useState(null);
  const [newApiKey, setNewApiKey] = useState(null);

  const [orgForm, setOrgForm] = useState({
    name: '',
    timezone: '',
    locale: '',
  });

  const [apiKeyForm, setApiKeyForm] = useState({
    name: '',
    permissions: 'read',
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [orgResponse, keysResponse, billingResponse] = await Promise.all([
        organizationService.getOrganization(),
        organizationService.getAPIKeys(),
        organizationService.getBilling().catch(() => ({ data: null })),
      ]);

      setOrganization(orgResponse.data);
      setApiKeys(keysResponse.data || []);
      setBilling(billingResponse.data);

      setOrgForm({
        name: orgResponse.data.name || '',
        timezone: orgResponse.data.timezone || '',
        locale: orgResponse.data.locale || '',
      });
    } catch (error) {
      toast.error(error.message || 'Failed to fetch organization data');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveOrganization = async () => {
    try {
      setSaving(true);
      await organizationService.updateOrganization(orgForm);
      toast.success('Organization settings updated');
      fetchData();
    } catch (error) {
      toast.error(error.message || 'Failed to update organization');
    } finally {
      setSaving(false);
    }
  };

  const handleCreateApiKey = async () => {
    try {
      const response = await organizationService.createAPIKey(apiKeyForm);
      setNewApiKey(response.data);
      toast.success('API key created successfully');
      setApiKeyForm({ name: '', permissions: 'read' });
      fetchData();
    } catch (error) {
      toast.error(error.message || 'Failed to create API key');
    }
  };

  const handleRevokeApiKey = async () => {
    try {
      await organizationService.revokeAPIKey(selectedKey.id);
      toast.success('API key revoked');
      setRevokeKeyModalOpen(false);
      setSelectedKey(null);
      fetchData();
    } catch (error) {
      toast.error(error.message || 'Failed to revoke API key');
    }
  };

  const handleCopyKey = (key) => {
    navigator.clipboard.writeText(key);
    toast.success('API key copied to clipboard');
  };

  const apiKeyColumns = [
    {
      key: 'name',
      label: 'Name',
      render: (value, row) => (
        <div className="flex flex-col">
          <span className="font-medium text-gray-900">{value}</span>
          <span className="text-xs text-gray-500">ID: {row.id?.slice(0, 8)}</span>
        </div>
      ),
    },
    {
      key: 'key_preview',
      label: 'Key',
      render: (value) => (
        <span className="font-mono text-sm text-gray-600">{value || 'sk_*******************'}</span>
      ),
    },
    {
      key: 'permissions',
      label: 'Permissions',
      render: (value) => (
        <Badge variant="secondary">{value}</Badge>
      ),
    },
    {
      key: 'last_used_at',
      label: 'Last Used',
      render: (value) => (
        <span className="text-sm text-gray-500">
          {value ? formatRelativeTime(value) : 'Never'}
        </span>
      ),
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
            setSelectedKey(row);
            setRevokeKeyModalOpen(true);
          }}
          className="text-error-600 hover:text-error-700"
          title="Revoke"
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

  return (
    <div className="space-y-6 max-w-5xl">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Organization Settings</h1>
        <p className="mt-1 text-sm text-gray-500">
          Manage your organization configuration and integrations
        </p>
      </div>

      {/* Organization Details */}
      <Card>
        <CardHeader>
          <div className="flex items-center space-x-2">
            <BuildingOfficeIcon className="w-5 h-5 text-gray-400" />
            <CardTitle>Organization Details</CardTitle>
          </div>
          <CardDescription>
            Basic information about your organization
          </CardDescription>
        </CardHeader>
        <CardBody>
          <div className="space-y-4">
            <FormInput
              label="Organization Name"
              required
              value={orgForm.name}
              onChange={(e) => setOrgForm({ ...orgForm, name: e.target.value })}
              placeholder="Enter organization name"
            />
            <FormSelect
              label="Timezone"
              value={orgForm.timezone}
              onChange={(e) => setOrgForm({ ...orgForm, timezone: e.target.value })}
              options={[
                { label: 'UTC', value: 'UTC' },
                { label: 'America/New_York', value: 'America/New_York' },
                { label: 'America/Chicago', value: 'America/Chicago' },
                { label: 'America/Los_Angeles', value: 'America/Los_Angeles' },
                { label: 'Europe/London', value: 'Europe/London' },
                { label: 'Asia/Tokyo', value: 'Asia/Tokyo' },
              ]}
            />
            <FormSelect
              label="Locale"
              value={orgForm.locale}
              onChange={(e) => setOrgForm({ ...orgForm, locale: e.target.value })}
              options={[
                { label: 'English (US)', value: 'en-US' },
                { label: 'English (UK)', value: 'en-GB' },
                { label: 'Spanish', value: 'es' },
                { label: 'French', value: 'fr' },
                { label: 'German', value: 'de' },
                { label: 'Japanese', value: 'ja' },
              ]}
            />
            <div className="flex justify-end">
              <Button onClick={handleSaveOrganization} loading={saving}>
                Save Changes
              </Button>
            </div>
          </div>
        </CardBody>
      </Card>

      {/* API Keys */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center space-x-2">
                <KeyIcon className="w-5 h-5 text-gray-400" />
                <CardTitle>API Keys</CardTitle>
              </div>
              <CardDescription>
                Manage API keys for programmatic access
              </CardDescription>
            </div>
            <Button
              leftIcon={PlusIcon}
              size="sm"
              onClick={() => setCreateKeyModalOpen(true)}
            >
              Create Key
            </Button>
          </div>
        </CardHeader>
        <CardBody>
          <DataTable
            data={apiKeys}
            columns={apiKeyColumns}
            emptyMessage="No API keys created yet"
          />
        </CardBody>
      </Card>

      {/* Billing & Usage */}
      {billing && (
        <Card>
          <CardHeader>
            <div className="flex items-center space-x-2">
              <CreditCardIcon className="w-5 h-5 text-gray-400" />
              <CardTitle>Billing & Usage</CardTitle>
            </div>
            <CardDescription>
              Current plan and usage information
            </CardDescription>
          </CardHeader>
          <CardBody>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <p className="text-sm font-medium text-gray-500">Current Plan</p>
                <p className="mt-1 text-lg font-semibold text-gray-900">
                  {billing.plan || 'Free'}
                </p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">Monthly Usage</p>
                <p className="mt-1 text-lg font-semibold text-gray-900">
                  {billing.usage || 0} executions
                </p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">Next Billing Date</p>
                <p className="mt-1 text-lg font-semibold text-gray-900">
                  {billing.next_billing_date ? formatDate(billing.next_billing_date) : 'N/A'}
                </p>
              </div>
            </div>
          </CardBody>
        </Card>
      )}

      {/* Create API Key Modal */}
      <Modal
        isOpen={createKeyModalOpen}
        onClose={() => {
          setCreateKeyModalOpen(false);
          setNewApiKey(null);
        }}
        title="Create API Key"
      >
        {newApiKey ? (
          <div className="space-y-4">
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <p className="text-sm font-medium text-yellow-800 mb-2">
                Save this API key - it will only be shown once!
              </p>
              <div className="flex items-center space-x-2">
                <code className="flex-1 bg-white px-3 py-2 rounded border border-yellow-300 text-sm font-mono text-gray-900">
                  {newApiKey.key}
                </code>
                <Button
                  variant="outline"
                  size="sm"
                  leftIcon={ClipboardDocumentIcon}
                  onClick={() => handleCopyKey(newApiKey.key)}
                >
                  Copy
                </Button>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <FormInput
              label="Key Name"
              required
              placeholder="Production API Key"
              value={apiKeyForm.name}
              onChange={(e) => setApiKeyForm({ ...apiKeyForm, name: e.target.value })}
            />
            <FormSelect
              label="Permissions"
              required
              value={apiKeyForm.permissions}
              onChange={(e) => setApiKeyForm({ ...apiKeyForm, permissions: e.target.value })}
              options={[
                { label: 'Read Only', value: 'read' },
                { label: 'Read & Write', value: 'write' },
                { label: 'Full Access', value: 'admin' },
              ]}
            />
          </div>
        )}
        <div className="mt-6 flex justify-end space-x-3">
          <Button
            variant="outline"
            onClick={() => {
              setCreateKeyModalOpen(false);
              setNewApiKey(null);
            }}
          >
            {newApiKey ? 'Close' : 'Cancel'}
          </Button>
          {!newApiKey && (
            <Button onClick={handleCreateApiKey}>
              Create Key
            </Button>
          )}
        </div>
      </Modal>

      {/* Revoke API Key Confirmation Modal */}
      <ConfirmModal
        isOpen={revokeKeyModalOpen}
        onClose={() => setRevokeKeyModalOpen(false)}
        onConfirm={handleRevokeApiKey}
        title="Revoke API Key"
        message={`Are you sure you want to revoke "${selectedKey?.name}"? Applications using this key will lose access immediately.`}
        confirmText="Revoke"
        variant="danger"
      />
    </div>
  );
}
