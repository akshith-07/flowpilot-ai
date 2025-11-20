/**
 * Tabs Component
 * Reusable tabs component for navigation between different views
 */

import { useState } from 'react';

/**
 * Tabs Component
 */
export function Tabs({ tabs, defaultTab, onChange, className = '' }) {
  const [activeTab, setActiveTab] = useState(defaultTab || tabs[0]?.id);

  const handleTabClick = (tabId) => {
    setActiveTab(tabId);
    if (onChange) {
      onChange(tabId);
    }
  };

  return (
    <div className={className}>
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8" aria-label="Tabs">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => handleTabClick(tab.id)}
              className={`
                whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors
                ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }
              `}
              aria-current={activeTab === tab.id ? 'page' : undefined}
            >
              {tab.icon && <tab.icon className="w-5 h-5 inline-block mr-2" />}
              {tab.label}
              {tab.count !== undefined && (
                <span
                  className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    activeTab === tab.id
                      ? 'bg-blue-100 text-blue-600'
                      : 'bg-gray-100 text-gray-600'
                  }`}
                >
                  {tab.count}
                </span>
              )}
            </button>
          ))}
        </nav>
      </div>
    </div>
  );
}

/**
 * TabPanel Component
 */
export function TabPanel({ children, value, activeValue, className = '' }) {
  if (value !== activeValue) {
    return null;
  }

  return <div className={className}>{children}</div>;
}

export default Tabs;
