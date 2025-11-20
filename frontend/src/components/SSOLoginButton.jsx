/**
 * SSO Login Button Component
 * Reusable button for initiating SSO login
 */
import { useState } from 'react';
import ssoService from '../services/ssoService';

export default function SSOLoginButton({ provider, connectionId, className = '' }) {
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    try {
      setLoading(true);

      const redirectUri = `${window.location.origin}/sso/callback`;
      const result = await ssoService.initiateLogin(connectionId, redirectUri);

      // Redirect to authorization URL
      if (result.authorization_url) {
        window.location.href = result.authorization_url;
      }
    } catch (error) {
      console.error('SSO login failed:', error);
      alert('Failed to initiate SSO login');
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleLogin}
      disabled={loading}
      className={`group relative flex w-full items-center justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 ${className}`}
    >
      {provider?.logo_url && (
        <img
          src={provider.logo_url}
          alt={provider.display_name}
          className="absolute left-4 h-5 w-5"
        />
      )}
      <span>{loading ? 'Redirecting...' : `Continue with ${provider?.display_name || 'SSO'}`}</span>
    </button>
  );
}
