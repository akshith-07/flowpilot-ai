/**
 * SSO Callback Page
 * Handles OAuth/OIDC callback and completes authentication
 */
import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/outline';

export default function SSOCallbackPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState('processing'); // processing, success, error
  const [message, setMessage] = useState('Processing SSO login...');

  useEffect(() => {
    handleCallback();
  }, []);

  const handleCallback = async () => {
    try {
      // Check for errors in URL
      const error = searchParams.get('error');
      if (error) {
        const errorDescription = searchParams.get('error_description') || 'Unknown error';
        setStatus('error');
        setMessage(`SSO login failed: ${errorDescription}`);
        return;
      }

      // Check for access_token in URL (from SAML or direct token response)
      const accessToken = searchParams.get('access_token');
      const refreshToken = searchParams.get('refresh_token');

      if (accessToken && refreshToken) {
        // Store tokens
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('refresh_token', refreshToken);

        setStatus('success');
        setMessage('SSO login successful! Redirecting...');

        // Redirect to dashboard after 1 second
        setTimeout(() => {
          navigate('/dashboard');
        }, 1000);

        return;
      }

      // If we get here, we have an authorization code that needs to be exchanged
      // This would typically be handled by your auth service
      const code = searchParams.get('code');
      const state = searchParams.get('state');

      if (!code || !state) {
        setStatus('error');
        setMessage('Invalid callback parameters');
        return;
      }

      // Exchange code for tokens via your API
      // This is handled by the backend SSO callback endpoint
      setStatus('error');
      setMessage('Code exchange not implemented in demo. Please use backend callback endpoint.');

    } catch (err) {
      console.error('SSO callback error:', err);
      setStatus('error');
      setMessage('Failed to complete SSO login');
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="w-full max-w-md">
        <div className="rounded-lg bg-white p-8 shadow">
          <div className="flex flex-col items-center">
            {status === 'processing' && (
              <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mb-4"></div>
            )}

            {status === 'success' && (
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-green-100 mb-4">
                <CheckCircleIcon className="h-10 w-10 text-green-600" />
              </div>
            )}

            {status === 'error' && (
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-red-100 mb-4">
                <XCircleIcon className="h-10 w-10 text-red-600" />
              </div>
            )}

            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              {status === 'processing' && 'Processing...'}
              {status === 'success' && 'Success!'}
              {status === 'error' && 'Error'}
            </h2>

            <p className="text-center text-sm text-gray-600 mb-6">
              {message}
            </p>

            {status === 'error' && (
              <button
                onClick={() => navigate('/login')}
                className="inline-flex items-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700"
              >
                Back to Login
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
