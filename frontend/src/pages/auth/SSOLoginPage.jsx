/**
 * SSO Login Page
 * Display available SSO providers and initiate login
 */
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ssoService from '../../services/ssoService';

export default function SSOLoginPage() {
  const navigate = useNavigate();
  const [providers, setProviders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadProviders();
  }, []);

  const loadProviders = async () => {
    try {
      const data = await ssoService.getProviders();
      setProviders(data.filter(p => p.is_enabled));
    } catch (err) {
      console.error('Failed to load SSO providers:', err);
      setError('Failed to load SSO providers');
    } finally {
      setLoading(false);
    }
  };

  const handleSSOLogin = async (provider) => {
    try {
      // In a real app, you'd select the connection based on email domain or organization
      // For now, we'll just redirect to SSO initiation
      const redirectUri = `${window.location.origin}/sso/callback`;

      // You would typically have a way to determine which connection to use
      // For example, by email domain or by letting user select organization
      // This is simplified for demo purposes
      alert('Please configure SSO connection for your organization first');

    } catch (err) {
      console.error('SSO login failed:', err);
      setError('Failed to initiate SSO login');
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-bold tracking-tight text-gray-900">
            Sign in with SSO
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Choose your identity provider
          </p>
        </div>

        {error && (
          <div className="rounded-md bg-red-50 p-4">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        <div className="mt-8 space-y-3">
          {providers.map((provider) => (
            <button
              key={provider.id}
              onClick={() => handleSSOLogin(provider)}
              className="group relative flex w-full items-center justify-center rounded-md border border-gray-300 bg-white px-4 py-3 text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              {provider.logo_url && (
                <img
                  src={provider.logo_url}
                  alt={provider.display_name}
                  className="absolute left-4 h-5 w-5"
                />
              )}
              <span>Continue with {provider.display_name}</span>
            </button>
          ))}
        </div>

        <div className="text-center">
          <button
            onClick={() => navigate('/login')}
            className="text-sm font-medium text-blue-600 hover:text-blue-500"
          >
            Back to login
          </button>
        </div>
      </div>
    </div>
  );
}
