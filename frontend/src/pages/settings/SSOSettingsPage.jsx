/**
 * SSO Settings Page
 * Manage organization SSO configurations
 */
import { useState, useEffect } from 'react';
import { PlusIcon, TrashIcon, CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/outline';
import ssoService from '../../services/ssoService';
import SSOConnectionModal from './SSOConnectionModal';
import SSOTestModal from './SSOTestModal';

export default function SSOSettingsPage() {
  const [connections, setConnections] = useState([]);
  const [providers, setProviders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showConnectionModal, setShowConnectionModal] = useState(false);
  const [showTestModal, setShowTestModal] = useState(false);
  const [selectedConnection, setSelectedConnection] = useState(null);
  const [selectedProvider, setSelectedProvider] = useState(null);
  const [organizationId, setOrganizationId] = useState(null);

  useEffect(() => {
    // Get organization ID from context or localStorage
    const orgId = localStorage.getItem('current_organization_id');
    setOrganizationId(orgId);

    if (orgId) {
      loadData(orgId);
    }
  }, []);

  const loadData = async (orgId) => {
    try {
      setLoading(true);
      const [connectionsData, providersData] = await Promise.all([
        ssoService.getConnections(orgId),
        ssoService.getAvailableProviders(orgId)
      ]);
      setConnections(connectionsData);
      setProviders(providersData);
    } catch (error) {
      console.error('Failed to load SSO data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateConnection = async (provider) => {
    setSelectedProvider(provider);
    setSelectedConnection(null);
    setShowConnectionModal(true);
  };

  const handleEditConnection = async (connection) => {
    setSelectedConnection(connection);
    setSelectedProvider(providers.find(p => p.id === connection.provider));
    setShowConnectionModal(true);
  };

  const handleDeleteConnection = async (connectionId) => {
    if (!confirm('Are you sure you want to delete this SSO connection?')) {
      return;
    }

    try {
      await ssoService.deleteConnection(connectionId);
      await loadData(organizationId);
    } catch (error) {
      console.error('Failed to delete connection:', error);
      alert('Failed to delete SSO connection');
    }
  };

  const handleTestConnection = (connection) => {
    setSelectedConnection(connection);
    setShowTestModal(true);
  };

  const handleToggleConnection = async (connection) => {
    try {
      if (connection.status === 'active') {
        await ssoService.deactivateConnection(connection.id);
      } else {
        await ssoService.activateConnection(connection.id);
      }
      await loadData(organizationId);
    } catch (error) {
      console.error('Failed to toggle connection:', error);
      alert('Failed to update connection status');
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      active: { color: 'bg-green-100 text-green-800', label: 'Active' },
      inactive: { color: 'bg-gray-100 text-gray-800', label: 'Inactive' },
      pending: { color: 'bg-yellow-100 text-yellow-800', label: 'Pending' },
      error: { color: 'bg-red-100 text-red-800', label: 'Error' }
    };

    const config = statusConfig[status] || statusConfig.pending;

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.color}`}>
        {config.label}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Single Sign-On (SSO)</h1>
        <p className="mt-2 text-sm text-gray-600">
          Configure enterprise SSO for your organization using Google, Microsoft, Okta, or other identity providers.
        </p>
      </div>

      {/* Existing Connections */}
      {connections.length > 0 && (
        <div className="mb-8">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Configured SSO Connections</h2>
          <div className="bg-white shadow overflow-hidden sm:rounded-lg">
            <ul className="divide-y divide-gray-200">
              {connections.map((connection) => (
                <li key={connection.id} className="px-6 py-4 hover:bg-gray-50">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center flex-1">
                      {connection.provider_details?.logo_url && (
                        <img
                          src={connection.provider_details.logo_url}
                          alt={connection.provider_details.display_name}
                          className="h-10 w-10 rounded"
                        />
                      )}
                      <div className="ml-4">
                        <div className="flex items-center">
                          <h3 className="text-sm font-medium text-gray-900">{connection.name}</h3>
                          <span className="ml-3">{getStatusBadge(connection.status)}</span>
                          {connection.is_default && (
                            <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                              Default
                            </span>
                          )}
                        </div>
                        <p className="mt-1 text-sm text-gray-500">
                          {connection.provider_details?.display_name} • {connection.provider_details?.provider_type?.toUpperCase()}
                        </p>
                        {connection.allowed_domains?.length > 0 && (
                          <p className="mt-1 text-xs text-gray-400">
                            Allowed domains: {connection.allowed_domains.join(', ')}
                          </p>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleTestConnection(connection)}
                        className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                      >
                        Test
                      </button>
                      <button
                        onClick={() => handleEditConnection(connection)}
                        className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleToggleConnection(connection)}
                        className={`inline-flex items-center px-3 py-2 border shadow-sm text-sm font-medium rounded-md ${
                          connection.status === 'active'
                            ? 'border-red-300 text-red-700 bg-white hover:bg-red-50'
                            : 'border-green-300 text-green-700 bg-white hover:bg-green-50'
                        }`}
                      >
                        {connection.status === 'active' ? 'Deactivate' : 'Activate'}
                      </button>
                      <button
                        onClick={() => handleDeleteConnection(connection.id)}
                        className="inline-flex items-center p-2 border border-transparent rounded-md text-red-600 hover:bg-red-50"
                      >
                        <TrashIcon className="h-5 w-5" />
                      </button>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Available Providers */}
      <div>
        <h2 className="text-lg font-medium text-gray-900 mb-4">Add SSO Provider</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {providers.map((provider) => (
            <div
              key={provider.id}
              className="relative rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm hover:border-gray-400"
            >
              <div className="flex items-center space-x-3">
                {provider.logo_url && (
                  <img src={provider.logo_url} alt={provider.display_name} className="h-12 w-12 rounded" />
                )}
                <div className="flex-1">
                  <h3 className="text-sm font-medium text-gray-900">{provider.display_name}</h3>
                  <p className="text-xs text-gray-500 mt-1">{provider.provider_type?.toUpperCase()}</p>
                </div>
                {provider.is_configured ? (
                  <CheckCircleIcon className="h-5 w-5 text-green-500" />
                ) : (
                  <button
                    onClick={() => handleCreateConnection(provider)}
                    className="inline-flex items-center p-2 border border-transparent rounded-md text-blue-600 hover:bg-blue-50"
                  >
                    <PlusIcon className="h-5 w-5" />
                  </button>
                )}
              </div>
              {provider.description && (
                <p className="mt-2 text-xs text-gray-500">{provider.description}</p>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Modals */}
      {showConnectionModal && (
        <SSOConnectionModal
          connection={selectedConnection}
          provider={selectedProvider}
          organizationId={organizationId}
          onClose={() => {
            setShowConnectionModal(false);
            setSelectedConnection(null);
            setSelectedProvider(null);
          }}
          onSuccess={() => {
            setShowConnectionModal(false);
            setSelectedConnection(null);
            setSelectedProvider(null);
            loadData(organizationId);
          }}
        />
      )}

      {showTestModal && selectedConnection && (
        <SSOTestModal
          connection={selectedConnection}
          onClose={() => {
            setShowTestModal(false);
            setSelectedConnection(null);
          }}
        />
      )}
    </div>
  );
}
