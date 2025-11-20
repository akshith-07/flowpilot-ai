/**
 * NodePalette Component
 * Palette of available workflow step types
 */

import { useState } from 'react';
import {
  MagnifyingGlassIcon,
  FunnelIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline';
import * as HeroIcons from '@heroicons/react/24/outline';
import {
  AI_STEPS,
  ACTION_STEPS,
  LOGIC_STEPS,
  INTEGRATION_STEPS,
  STEP_CATEGORIES,
} from '@constants/workflowSteps';
import { Badge, Input } from '@components/ui';

/**
 * Get icon component from icon name
 */
const getIconComponent = (iconName) => {
  return HeroIcons[iconName] || HeroIcons.CubeIcon;
};

/**
 * Category sections
 */
const CATEGORY_SECTIONS = {
  [STEP_CATEGORIES.AI]: {
    title: 'AI Steps',
    steps: AI_STEPS,
    color: '#8b5cf6',
  },
  [STEP_CATEGORIES.ACTION]: {
    title: 'Actions',
    steps: ACTION_STEPS,
    color: '#3b82f6',
  },
  [STEP_CATEGORIES.LOGIC]: {
    title: 'Logic',
    steps: LOGIC_STEPS,
    color: '#10b981',
  },
  [STEP_CATEGORIES.INTEGRATION]: {
    title: 'Integrations',
    steps: INTEGRATION_STEPS,
    color: '#f59e0b',
  },
};

/**
 * Step Card Component
 */
function StepCard({ step, onDragStart }) {
  const Icon = getIconComponent(step.icon);

  const handleDragStart = (e) => {
    e.dataTransfer.effectAllowed = 'copy';
    e.dataTransfer.setData('stepType', step.type);
    e.dataTransfer.setData('stepData', JSON.stringify(step));
    if (onDragStart) {
      onDragStart(step);
    }
  };

  return (
    <div
      draggable
      onDragStart={handleDragStart}
      className="flex items-center gap-3 p-3 bg-white border border-gray-200 rounded-lg cursor-grab hover:border-gray-300 hover:shadow-md transition-all active:cursor-grabbing"
    >
      <div
        className="flex items-center justify-center w-10 h-10 rounded-lg flex-shrink-0"
        style={{ backgroundColor: step.color }}
      >
        <Icon className="w-6 h-6 text-white" />
      </div>

      <div className="flex-1 min-w-0">
        <h4 className="font-medium text-sm text-gray-900 truncate">
          {step.name}
        </h4>
        <p className="text-xs text-gray-500 truncate">{step.description}</p>
      </div>
    </div>
  );
}

/**
 * NodePalette Component
 */
export default function NodePalette({ onStepDragStart, isCollapsed, onToggle }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState(null);

  /**
   * Filter steps based on search and category
   */
  const filterSteps = (steps) => {
    return Object.values(steps).filter((step) => {
      const matchesSearch =
        !searchQuery ||
        step.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        step.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        step.type.toLowerCase().includes(searchQuery.toLowerCase());

      const matchesCategory =
        !selectedCategory || step.category === selectedCategory;

      return matchesSearch && matchesCategory;
    });
  };

  /**
   * Get all filtered steps grouped by category
   */
  const getFilteredSections = () => {
    return Object.entries(CATEGORY_SECTIONS)
      .map(([category, section]) => ({
        ...section,
        category,
        steps: filterSteps(section.steps),
      }))
      .filter((section) => section.steps.length > 0);
  };

  const filteredSections = getFilteredSections();

  if (isCollapsed) {
    return null;
  }

  return (
    <div className="h-full bg-gray-50 border-r border-gray-200 overflow-hidden flex flex-col">
      {/* Header */}
      <div className="p-4 bg-white border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Node Palette</h3>
          {onToggle && (
            <button
              onClick={onToggle}
              className="p-1 text-gray-400 hover:text-gray-600 rounded transition-colors"
            >
              <XMarkIcon className="w-5 h-5" />
            </button>
          )}
        </div>

        {/* Search */}
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search steps..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* Category Filter */}
        <div className="flex flex-wrap gap-2 mt-3">
          <button
            onClick={() => setSelectedCategory(null)}
            className={`px-3 py-1 text-xs font-medium rounded-full transition-colors ${
              selectedCategory === null
                ? 'bg-blue-100 text-blue-700'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            All
          </button>
          {Object.entries(STEP_CATEGORIES).map(([key, value]) => (
            <button
              key={key}
              onClick={() =>
                setSelectedCategory(selectedCategory === value ? null : value)
              }
              className={`px-3 py-1 text-xs font-medium rounded-full transition-colors ${
                selectedCategory === value
                  ? 'bg-blue-100 text-blue-700'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {key.charAt(0) + key.slice(1).toLowerCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Step Categories */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {filteredSections.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500 text-sm">No steps found</p>
            <p className="text-gray-400 text-xs mt-1">
              Try adjusting your search or filters
            </p>
          </div>
        ) : (
          filteredSections.map((section) => (
            <div key={section.category}>
              {/* Category Header */}
              <div className="flex items-center gap-2 mb-3">
                <div
                  className="w-1 h-4 rounded-full"
                  style={{ backgroundColor: section.color }}
                />
                <h4 className="font-semibold text-sm text-gray-700">
                  {section.title}
                </h4>
                <Badge variant="secondary" size="sm">
                  {section.steps.length}
                </Badge>
              </div>

              {/* Steps */}
              <div className="space-y-2">
                {section.steps.map((step) => (
                  <StepCard
                    key={step.type}
                    step={step}
                    onDragStart={onStepDragStart}
                  />
                ))}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Footer */}
      <div className="p-3 bg-white border-t border-gray-200">
        <p className="text-xs text-gray-500 text-center">
          Drag and drop steps onto the canvas
        </p>
      </div>
    </div>
  );
}
