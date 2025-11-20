/**
 * ConnectorsPage Component
 * Displays available connectors and manages OAuth integrations
 */

import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  LinkIcon,
  CheckCircleIcon,
  XCircleIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';
import Card, { CardBody } from '@/components/ui/Card';
import { ConfirmModal } from '@/components/ui/Modal';
import connectorService from '@/services/connectorService';
import toast from 'react-hot-toast';

/**
 * Available connector configurations
 */
const AVAILABLE_CONNECTORS = [
  {
    id: 'gmail',
    name: 'Gmail',
    description: 'Send and receive emails, manage labels and filters',
    logo: '📧',
    category: 'Email',
    color: 'bg-red-100 text-red-600',
  },
  {
    id: 'slack',
    name: 'Slack',
    description: 'Send messages, manage channels and users',
    logo: '💬',
    category: 'Communication',
    color: 'bg-purple-100 text-purple-600',
  },
  {
    id: 'notion',
    name: 'Notion',
    description: 'Create and update pages, databases, and blocks',
    logo: '📝',
    category: 'Productivity',
    color: 'bg-gray-100 text-gray-600',
  },
  {
    id: 'google-drive',
    name: 'Google Drive',
    description: 'Upload, download, and manage files',
    logo: '📁',
    category: 'Storage',
    color: 'bg-blue-100 text-blue-600',
  },
  {
    id: 'salesforce',
    name: 'Salesforce',
    description: 'Manage leads, opportunities, and accounts',
    logo: '☁️',
    category: 'CRM',
    color: 'bg-cyan-100 text-cyan-600',
  },
  {
    id: 'hubspot',
    name: 'HubSpot',
    description: 'Manage contacts, deals, and marketing campaigns',
    logo: '🎯',
    category: 'CRM',
    color: 'bg-orange-100 text-orange-600',
  },
  {
    id: 'jira',
    name: 'Jira',
    description: 'Create and manage issues, projects, and sprints',
    logo: '📊',
    category: 'Project Management',
    color: 'bg-blue-100 text-blue-600',
  },
  {
    id: 'trello',
    name: 'Trello',
    description: 'Manage boards, lists, and cards',
    logo: '📋',
    category: 'Project Management',
    color: 'bg-sky-100 text-sky-600',
  },
  {
    id: 'outlook',
    name: 'Outlook',
    description: 'Send emails and manage calendar events',
    logo: '📨',
    category: 'Email',
    color: 'bg-blue-100 text-blue-600',
  },
  {
    id: 'teams',
    name: 'Microsoft Teams',
    description: 'Send messages and manage team channels',
    logo: '👥',
    category: 'Communication',
    color: 'bg-indigo-100 text-indigo-600',
  },
  {
    id: 'dropbox',
    name: 'Dropbox',
    description: 'Upload and manage files in your Dropbox',
    logo: '📦',
    category: 'Storage',
    color: 'bg-blue-100 text-blue-600',
  },
  {
    id: 'asana',
    name: 'Asana',
    description: 'Create tasks, projects, and track progress',
    logo: '✅',
    category: 'Project Management',
    color: 'bg-pink-100 text-pink-600',
  },
];

/**
 * ConnectorsPage Component
 */
export default function ConnectorsPage() {
  const navigate = useNavigate();
  const [connectors, setConnectors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [disconnectModalOpen, setDisconnectModalOpen] = useState(false);
  const [selectedConnector, setSelectedConnector] = useState(null);
  const [connectingProvider, setConnectingProvider] = useState(null);
  const [categoryFilter, setCategoryFilter] = useState('');

  useEffect(() => {
    fetchConnectors();
  }, []);

  const fetchConnectors = async () => {
    try {
      setLoading(true);
      const response = await connectorService.getConnectors();
      setConnectors(response.data || []);
    } catch (error) {
      toast.error(error.message || 'Failed to fetch connectors');
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async (provider) => {
    try {
      setConnectingProvider(provider.id);
      const redirectUrl = `${window.location.origin}/connectors/callback`;
      const response = await connectorService.authorizeConnector(provider.id, redirectUrl);

      if (response.data.authorization_url) {
        window.location.href = response.data.authorization_url;
      }
    } catch (error) {
      toast.error(error.message || 'Failed to initiate connection');
      setConnectingProvider(null);
    }
  };

  const handleDisconnect = async () => {
    try {
      await connectorService.disconnectConnector(selectedConnector.id);
      toast.success('Connector disconnected successfully');
      setDisconnectModalOpen(false);
      setSelectedConnector(null);
      fetchConnectors();
    } catch (error) {
      toast.error(error.message || 'Failed to disconnect connector');
    }
  };

  const isConnected = (providerId) => {
    return connectors.some((c) => c.provider === providerId && c.status === 'connected');
  };

  const getConnectorByProvider = (providerId) => {
    return connectors.find((c) => c.provider === providerId);
  };

  const categories = [...new Set(AVAILABLE_CONNECTORS.map((c) => c.category))];

  const filteredConnectors = categoryFilter
    ? AVAILABLE_CONNECTORS.filter((c) => c.category === categoryFilter)
    : AVAILABLE_CONNECTORS;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Connectors</h1>
          <p className="mt-1 text-sm text-gray-500">
            Connect your favorite tools and services to automate workflows
          </p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardBody>
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <LinkIcon className="w-8 h-8 text-primary-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Available Connectors</p>
                <p className="text-2xl font-bold text-gray-900">{AVAILABLE_CONNECTORS.length}</p>
              </div>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardBody>
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CheckCircleIcon className="w-8 h-8 text-success-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Connected</p>
                <p className="text-2xl font-bold text-gray-900">
                  {connectors.filter((c) => c.status === 'connected').length}
                </p>
              </div>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardBody>
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <XCircleIcon className="w-8 h-8 text-error-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Disconnected</p>
                <p className="text-2xl font-bold text-gray-900">
                  {AVAILABLE_CONNECTORS.length - connectors.filter((c) => c.status === 'connected').length}
                </p>
              </div>
            </div>
          </CardBody>
        </Card>
      </div>

      {/* Category Filter */}
      <div className="flex items-center space-x-2 overflow-x-auto">
        <Button
          variant={categoryFilter === '' ? 'primary' : 'outline'}
          size="sm"
          onClick={() => setCategoryFilter('')}
        >
          All
        </Button>
        {categories.map((category) => (
          <Button
            key={category}
            variant={categoryFilter === category ? 'primary' : 'outline'}
            size="sm"
            onClick={() => setCategoryFilter(category)}
          >
            {category}
          </Button>
        ))}
      </div>

      {/* Connectors Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredConnectors.map((provider) => {
          const connected = isConnected(provider.id);
          const connector = getConnectorByProvider(provider.id);
          const connecting = connectingProvider === provider.id;

          return (
            <Card
              key={provider.id}
              className="hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => connected && navigate(`/connectors/${connector.id}`)}
            >
              <CardBody>
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3 flex-1">
                    <div className={`w-12 h-12 rounded-lg flex items-center justify-center text-2xl ${provider.color}`}>
                      {provider.logo}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="text-lg font-semibold text-gray-900">{provider.name}</h3>
                      <p className="text-sm text-gray-500 mt-1">{provider.description}</p>
                      <div className="mt-2">
                        <Badge variant="secondary" size="sm">{provider.category}</Badge>
                      </div>
                    </div>
                  </div>
                  {connected && (
                    <CheckCircleIcon className="w-6 h-6 text-success-600 flex-shrink-0" />
                  )}
                </div>

                <div className="mt-4 flex items-center space-x-2">
                  {connected ? (
                    <>
                      <Button
                        variant="outline"
                        size="sm"
                        fullWidth
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/connectors/${connector.id}`);
                        }}
                      >
                        Manage
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedConnector(connector);
                          setDisconnectModalOpen(true);
                        }}
                        className="text-error-600 hover:text-error-700"
                      >
                        Disconnect
                      </Button>
                    </>
                  ) : (
                    <Button
                      variant="primary"
                      size="sm"
                      fullWidth
                      leftIcon={LinkIcon}
                      loading={connecting}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleConnect(provider);
                      }}
                    >
                      Connect
                    </Button>
                  )}
                </div>
              </CardBody>
            </Card>
          );
        })}
      </div>

      {filteredConnectors.length === 0 && (
        <div className="text-center py-12">
          <LinkIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-sm text-gray-500">No connectors found in this category</p>
        </div>
      )}

      {/* Disconnect Confirmation Modal */}
      <ConfirmModal
        isOpen={disconnectModalOpen}
        onClose={() => setDisconnectModalOpen(false)}
        onConfirm={handleDisconnect}
        title="Disconnect Connector"
        message={`Are you sure you want to disconnect ${selectedConnector?.provider}? Your workflows using this connector will stop working.`}
        confirmText="Disconnect"
        variant="danger"
      />
    </div>
  );
}
