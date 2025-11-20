/**
 * WorkflowNode Component
 * Individual configurable workflow node for drag-and-drop canvas
 */

import { useState } from 'react';
import { XMarkIcon, Cog6ToothIcon, TrashIcon } from '@heroicons/react/24/outline';
import * as HeroIcons from '@heroicons/react/24/outline';
import { Badge } from '@components/ui';

/**
 * Get icon component from icon name
 */
const getIconComponent = (iconName) => {
  return HeroIcons[iconName] || HeroIcons.CubeIcon;
};

/**
 * WorkflowNode Component
 */
export default function WorkflowNode({
  node,
  isSelected,
  onSelect,
  onDelete,
  onConfigure,
  onConnect,
  position = { x: 0, y: 0 },
}) {
  const [isDragging, setIsDragging] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);

  const Icon = getIconComponent(node.icon);

  /**
   * Handle node click
   */
  const handleClick = (e) => {
    e.stopPropagation();
    onSelect(node.id);
  };

  /**
   * Handle configure button
   */
  const handleConfigure = (e) => {
    e.stopPropagation();
    onConfigure(node.id);
  };

  /**
   * Handle delete button
   */
  const handleDelete = (e) => {
    e.stopPropagation();
    onDelete(node.id);
  };

  /**
   * Handle connection point click
   */
  const handleConnectClick = (type) => (e) => {
    e.stopPropagation();
    setIsConnecting(true);
    if (onConnect) {
      onConnect(node.id, type);
    }
  };

  return (
    <div
      className={`
        absolute workflow-node
        bg-white rounded-lg shadow-md border-2
        transition-all duration-200
        ${isSelected ? 'border-blue-500 shadow-lg ring-2 ring-blue-200' : 'border-gray-200'}
        ${isDragging ? 'opacity-50 cursor-grabbing' : 'cursor-grab'}
        hover:shadow-lg
        w-64
      `}
      style={{
        left: `${position.x}px`,
        top: `${position.y}px`,
      }}
      onClick={handleClick}
      draggable
      onDragStart={() => setIsDragging(true)}
      onDragEnd={() => setIsDragging(false)}
    >
      {/* Header */}
      <div
        className="flex items-center gap-3 p-3 rounded-t-lg"
        style={{ backgroundColor: `${node.color}15` }}
      >
        <div
          className="flex items-center justify-center w-10 h-10 rounded-lg"
          style={{ backgroundColor: node.color }}
        >
          <Icon className="w-6 h-6 text-white" />
        </div>

        <div className="flex-1 min-w-0">
          <h4 className="font-semibold text-sm text-gray-900 truncate">
            {node.name}
          </h4>
          <p className="text-xs text-gray-500 truncate">{node.type}</p>
        </div>

        <div className="flex items-center gap-1">
          <button
            onClick={handleConfigure}
            className="p-1 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded transition-colors"
            title="Configure"
          >
            <Cog6ToothIcon className="w-4 h-4" />
          </button>
          <button
            onClick={handleDelete}
            className="p-1 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
            title="Delete"
          >
            <TrashIcon className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Body */}
      <div className="p-3 space-y-3">
        {/* Description */}
        <p className="text-xs text-gray-600">{node.description}</p>

        {/* Status Badge */}
        {node.status && (
          <div className="flex justify-end">
            <Badge variant={node.status === 'configured' ? 'success' : 'warning'}>
              {node.status}
            </Badge>
          </div>
        )}

        {/* Configuration Summary */}
        {node.config && Object.keys(node.config).length > 0 && (
          <div className="p-2 bg-gray-50 rounded text-xs space-y-1">
            <div className="font-medium text-gray-700">Configuration:</div>
            {Object.entries(node.config)
              .slice(0, 2)
              .map(([key, value]) => (
                <div key={key} className="text-gray-600 truncate">
                  <span className="font-medium">{key}:</span>{' '}
                  {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                </div>
              ))}
            {Object.keys(node.config).length > 2 && (
              <div className="text-gray-500">
                +{Object.keys(node.config).length - 2} more
              </div>
            )}
          </div>
        )}
      </div>

      {/* Connection Points */}
      <div className="absolute -top-2 left-1/2 transform -translate-x-1/2">
        <button
          onClick={handleConnectClick('input')}
          className="w-4 h-4 bg-white border-2 border-gray-400 rounded-full hover:border-blue-500 hover:bg-blue-50 transition-colors"
          title="Input connection"
        />
      </div>
      <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2">
        <button
          onClick={handleConnectClick('output')}
          className="w-4 h-4 bg-white border-2 border-gray-400 rounded-full hover:border-blue-500 hover:bg-blue-50 transition-colors"
          title="Output connection"
        />
      </div>
    </div>
  );
}
