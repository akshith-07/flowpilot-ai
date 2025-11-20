/**
 * Auth Layout
 * Layout for authentication pages (login, register, etc.)
 */

import { APP_CONFIG } from '@constants';

export default function AuthLayout({ children }) {
  return (
    <div className="min-h-screen flex">
      {/* Left Side - Branding */}
      <div className="hidden lg:flex lg:flex-1 bg-gradient-to-br from-primary-600 to-primary-800 items-center justify-center p-12">
        <div className="max-w-md text-white">
          <h1 className="text-4xl font-bold mb-4">{APP_CONFIG.name}</h1>
          <p className="text-xl text-primary-100 mb-8">
            Enterprise AI Workflow Automation Platform
          </p>
          <div className="space-y-4">
            <div className="flex items-start">
              <svg
                className="h-6 w-6 text-primary-200 mr-3 flex-shrink-0"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
              <div>
                <h3 className="font-semibold mb-1">AI-Powered Automation</h3>
                <p className="text-primary-100 text-sm">
                  Leverage advanced AI models to automate complex workflows
                </p>
              </div>
            </div>
            <div className="flex items-start">
              <svg
                className="h-6 w-6 text-primary-200 mr-3 flex-shrink-0"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
              <div>
                <h3 className="font-semibold mb-1">Enterprise-Grade Security</h3>
                <p className="text-primary-100 text-sm">
                  SOC 2 compliant with enterprise-grade security features
                </p>
              </div>
            </div>
            <div className="flex items-start">
              <svg
                className="h-6 w-6 text-primary-200 mr-3 flex-shrink-0"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
              <div>
                <h3 className="font-semibold mb-1">Seamless Integrations</h3>
                <p className="text-primary-100 text-sm">
                  Connect with your favorite tools and services
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Right Side - Auth Form */}
      <div className="flex-1 flex items-center justify-center p-8 bg-gray-50">
        <div className="w-full max-w-md">
          {/* Mobile Logo */}
          <div className="lg:hidden text-center mb-8">
            <h1 className="text-2xl font-bold text-gray-900">{APP_CONFIG.name}</h1>
          </div>

          {/* Content */}
          <div className="bg-white rounded-lg shadow-md p-8">
            {children}
          </div>

          {/* Footer */}
          <p className="text-center text-sm text-gray-600 mt-8">
            © {new Date().getFullYear()} {APP_CONFIG.name}. All rights reserved.
          </p>
        </div>
      </div>
    </div>
  );
}
