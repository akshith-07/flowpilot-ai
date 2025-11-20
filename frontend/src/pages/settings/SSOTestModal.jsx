/**
 * SSO Test Modal
 * Test SSO connection
 */
import { useState } from 'react';
import { XMarkIcon, CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/outline';
import ssoService from '../../services/ssoService';

export default function SSOTestModal({ connection, onClose }) {
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState(null);
  const [error, setError] = useState(null);

  const handleTest = async () => {
    setTesting(true);
    setError(null);
    setTestResult(null);

    try {
      const result = await ssoService.testConnection(connection.id);
      setTestResult(result);

      // Open test URL in new window
      if (result.test_url) {
        window.open(result.test_url, '_blank', 'width=600,height=700');
      }
    } catch (err) {
      console.error('Test failed:', err);
      setError(err.response?.data?.error || 'Failed to test SSO connection');
    } finally {
      setTesting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4">
        {/* Backdrop */}
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={onClose}></div>

        {/* Modal */}
        <div className="relative w-full max-w-lg transform rounded-lg bg-white shadow-xl transition-all">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-gray-200 px-6 py-4">
            <h3 className="text-lg font-medium text-gray-900">
              Test SSO Connection
            </h3>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-500">
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>

          {/* Content */}
          <div className="px-6 py-4">
            <div className="mb-4">
              <h4 className="text-sm font-medium text-gray-900">{connection.name}</h4>
              <p className="text-sm text-gray-500">
                {connection.provider_details?.display_name}
              </p>
            </div>

            {error && (
              <div className="mb-4 rounded-md bg-red-50 p-4">
                <div className="flex">
                  <XCircleIcon className="h-5 w-5 text-red-400" />
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-red-800">Test Failed</h3>
                    <p className="mt-1 text-sm text-red-700">{error}</p>
                  </div>
                </div>
              </div>
            )}

            {testResult && !error && (
              <div className="mb-4 rounded-md bg-green-50 p-4">
                <div className="flex">
                  <CheckCircleIcon className="h-5 w-5 text-green-400" />
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-green-800">Test Initiated</h3>
                    <p className="mt-1 text-sm text-green-700">
                      {testResult.message}
                    </p>
                    <p className="mt-2 text-xs text-green-600">
                      A new window should have opened. Complete the login flow to test the connection.
                    </p>
                  </div>
                </div>
              </div>
            )}

            <div className="rounded-lg border border-gray-200 bg-gray-50 p-4">
              <h4 className="text-sm font-medium text-gray-900 mb-2">Testing Instructions</h4>
              <ol className="list-decimal list-inside space-y-1 text-sm text-gray-600">
                <li>Click "Start Test" to open the SSO login page</li>
                <li>Complete the authentication with your identity provider</li>
                <li>Verify that you are redirected back successfully</li>
                <li>Check the SSO logs for any errors</li>
              </ol>
            </div>
          </div>

          {/* Footer */}
          <div className="flex justify-end space-x-3 border-t border-gray-200 px-6 py-4">
            <button
              type="button"
              onClick={onClose}
              className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50"
            >
              Close
            </button>
            <button
              type="button"
              onClick={handleTest}
              disabled={testing}
              className="inline-flex items-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
            >
              {testing ? 'Starting Test...' : 'Start Test'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
