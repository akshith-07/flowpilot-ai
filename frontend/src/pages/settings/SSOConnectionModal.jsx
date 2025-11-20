/**
 * SSO Connection Modal
 * Create or edit SSO connection
 */
import { useState, useEffect } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import ssoService from '../../services/ssoService';

export default function SSOConnectionModal({ connection, provider, organizationId, onClose, onSuccess }) {
  const isEdit = !!connection;
  const [formData, setFormData] = useState({
    name: '',
    client_id: '',
    client_secret: '',
    redirect_uri: window.location.origin + '/sso/callback',
    allowed_domains: [],
    auto_provision_users: true,
    auto_activate_users: true,
    require_email_verification: false,
    enforce_sso: false,
    pkce_required: true,
    attribute_mapping: {
      email: 'email',
      first_name: 'given_name',
      last_name: 'family_name',
      avatar_url: 'picture'
    },
    role_mapping: {}
  });

  const [domainInput, setDomainInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (connection) {
      setFormData({
        name: connection.name || '',
        client_id: connection.client_id || '',
        client_secret: '',  // Never pre-fill password
        redirect_uri: connection.redirect_uri || window.location.origin + '/sso/callback',
        allowed_domains: connection.allowed_domains || [],
        auto_provision_users: connection.auto_provision_users ?? true,
        auto_activate_users: connection.auto_activate_users ?? true,
        require_email_verification: connection.require_email_verification ?? false,
        enforce_sso: connection.enforce_sso ?? false,
        pkce_required: connection.pkce_required ?? true,
        attribute_mapping: connection.attribute_mapping || {
          email: 'email',
          first_name: 'given_name',
          last_name: 'family_name',
          avatar_url: 'picture'
        },
        role_mapping: connection.role_mapping || {}
      });
    } else if (provider) {
      // Set defaults based on provider
      const defaults = getProviderDefaults(provider.provider_name);
      setFormData(prev => ({
        ...prev,
        ...defaults,
        name: `${provider.display_name} SSO`
      }));
    }
  }, [connection, provider]);

  const getProviderDefaults = (providerName) => {
    const defaults = {
      google: {
        attribute_mapping: {
          email: 'email',
          first_name: 'given_name',
          last_name: 'family_name',
          avatar_url: 'picture'
        }
      },
      microsoft: {
        attribute_mapping: {
          email: 'email',
          first_name: 'given_name',
          last_name: 'family_name'
        }
      },
      okta: {
        attribute_mapping: {
          email: 'email',
          first_name: 'firstName',
          last_name: 'lastName',
          groups: 'groups'
        }
      }
    };

    return defaults[providerName] || {};
  };

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleAddDomain = () => {
    if (domainInput && !formData.allowed_domains.includes(domainInput)) {
      setFormData(prev => ({
        ...prev,
        allowed_domains: [...prev.allowed_domains, domainInput]
      }));
      setDomainInput('');
    }
  };

  const handleRemoveDomain = (domain) => {
    setFormData(prev => ({
      ...prev,
      allowed_domains: prev.allowed_domains.filter(d => d !== domain)
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const payload = {
        ...formData,
        organization: organizationId,
        provider: provider.id
      };

      if (isEdit) {
        // Don't send client_secret if empty (not changing it)
        if (!payload.client_secret) {
          delete payload.client_secret;
        }
        await ssoService.updateConnection(connection.id, payload);
      } else {
        await ssoService.createConnection(payload);
      }

      onSuccess();
    } catch (err) {
      console.error('Failed to save SSO connection:', err);
      setError(err.response?.data?.detail || 'Failed to save SSO connection');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4">
        {/* Backdrop */}
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={onClose}></div>

        {/* Modal */}
        <div className="relative w-full max-w-2xl transform rounded-lg bg-white shadow-xl transition-all">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-gray-200 px-6 py-4">
            <h3 className="text-lg font-medium text-gray-900">
              {isEdit ? 'Edit' : 'Configure'} {provider?.display_name} SSO
            </h3>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-500">
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="px-6 py-4">
            {error && (
              <div className="mb-4 rounded-md bg-red-50 p-4">
                <p className="text-sm text-red-800">{error}</p>
              </div>
            )}

            <div className="space-y-4">
              {/* Connection Name */}
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Connection Name
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => handleChange('name', e.target.value)}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  required
                />
              </div>

              {/* Client ID */}
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Client ID / Application ID
                </label>
                <input
                  type="text"
                  value={formData.client_id}
                  onChange={(e) => handleChange('client_id', e.target.value)}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  required
                />
                <p className="mt-1 text-xs text-gray-500">
                  Get this from your {provider?.display_name} admin console
                </p>
              </div>

              {/* Client Secret */}
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Client Secret
                  {isEdit && <span className="text-gray-400"> (leave blank to keep existing)</span>}
                </label>
                <input
                  type="password"
                  value={formData.client_secret}
                  onChange={(e) => handleChange('client_secret', e.target.value)}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  required={!isEdit}
                />
              </div>

              {/* Redirect URI */}
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Redirect URI
                </label>
                <input
                  type="url"
                  value={formData.redirect_uri}
                  onChange={(e) => handleChange('redirect_uri', e.target.value)}
                  className="mt-1 block w-full rounded-md border-gray-300 bg-gray-50 shadow-sm sm:text-sm"
                  readOnly
                />
                <p className="mt-1 text-xs text-gray-500">
                  Add this URL to your {provider?.display_name} authorized redirect URIs
                </p>
              </div>

              {/* Allowed Domains */}
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Allowed Email Domains (Optional)
                </label>
                <div className="mt-1 flex">
                  <input
                    type="text"
                    value={domainInput}
                    onChange={(e) => setDomainInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddDomain())}
                    placeholder="example.com"
                    className="block w-full rounded-l-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  />
                  <button
                    type="button"
                    onClick={handleAddDomain}
                    className="inline-flex items-center rounded-r-md border border-l-0 border-gray-300 bg-gray-50 px-4 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    Add
                  </button>
                </div>
                {formData.allowed_domains.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-2">
                    {formData.allowed_domains.map((domain) => (
                      <span
                        key={domain}
                        className="inline-flex items-center rounded-full bg-blue-100 px-3 py-0.5 text-sm font-medium text-blue-800"
                      >
                        {domain}
                        <button
                          type="button"
                          onClick={() => handleRemoveDomain(domain)}
                          className="ml-1 inline-flex h-4 w-4 flex-shrink-0 items-center justify-center rounded-full text-blue-400 hover:bg-blue-200 hover:text-blue-500"
                        >
                          <span className="sr-only">Remove {domain}</span>
                          <XMarkIcon className="h-3 w-3" />
                        </button>
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* User Provisioning Options */}
              <div className="space-y-3 rounded-lg border border-gray-200 p-4">
                <h4 className="text-sm font-medium text-gray-900">User Provisioning</h4>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.auto_provision_users}
                    onChange={(e) => handleChange('auto_provision_users', e.target.checked)}
                    className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <label className="ml-2 text-sm text-gray-700">
                    Automatically create users on first login
                  </label>
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.auto_activate_users}
                    onChange={(e) => handleChange('auto_activate_users', e.target.checked)}
                    className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <label className="ml-2 text-sm text-gray-700">
                    Automatically activate new users
                  </label>
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.enforce_sso}
                    onChange={(e) => handleChange('enforce_sso', e.target.checked)}
                    className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <label className="ml-2 text-sm text-gray-700">
                    Enforce SSO (disable password login)
                  </label>
                </div>
              </div>

              {/* Security Options */}
              {provider?.provider_type !== 'saml2' && (
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.pkce_required}
                    onChange={(e) => handleChange('pkce_required', e.target.checked)}
                    className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <label className="ml-2 text-sm text-gray-700">
                    Require PKCE (recommended for security)
                  </label>
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="mt-6 flex justify-end space-x-3 border-t border-gray-200 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="inline-flex items-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
              >
                {loading ? 'Saving...' : (isEdit ? 'Save Changes' : 'Create Connection')}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
