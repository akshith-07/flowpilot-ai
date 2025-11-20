/**
 * WorkflowCanvas Component
 * Drag-and-drop canvas for workflow building
 */

import { useState, useRef, useEffect } from 'react';
import {
  PlusIcon,
  ArrowsPointingOutIcon,
  ArrowsPointingInIcon,
} from '@heroicons/react/24/outline';
import WorkflowNode from './WorkflowNode';
import { getStepByType } from '@constants/workflowSteps';

/**
 * Connection Line Component
 */
function ConnectionLine({ from, to }) {
  if (!from || !to) return null;

  // Calculate control points for bezier curve
  const midY = (from.y + to.y) / 2;

  const path = `M ${from.x} ${from.y}
                 C ${from.x} ${midY},
                   ${to.x} ${midY},
                   ${to.x} ${to.y}`;

  return (
    <g>
      <path
        d={path}
        fill="none"
        stroke="#94a3b8"
        strokeWidth="2"
        markerEnd="url(#arrowhead)"
      />
      <circle cx={from.x} cy={from.y} r="4" fill="#94a3b8" />
      <circle cx={to.x} cy={to.y} r="4" fill="#94a3b8" />
    </g>
  );
}

/**
 * WorkflowCanvas Component
 */
export default function WorkflowCanvas({
  nodes = [],
  connections = [],
  onNodesChange,
  onConnectionsChange,
  onNodeSelect,
  onNodeConfigure,
  selectedNodeId,
}) {
  const canvasRef = useRef(null);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState(false);
  const [panStart, setPanStart] = useState({ x: 0, y: 0 });
  const [connectingFrom, setConnectingFrom] = useState(null);

  /**
   * Handle drop on canvas
   */
  const handleDrop = (e) => {
    e.preventDefault();

    const stepType = e.dataTransfer.getData('stepType');
    const stepDataStr = e.dataTransfer.getData('stepData');

    if (!stepType || !stepDataStr) return;

    try {
      const stepData = JSON.parse(stepDataStr);
      const canvasRect = canvasRef.current.getBoundingClientRect();

      // Calculate position relative to canvas with zoom and pan
      const x = (e.clientX - canvasRect.left - pan.x) / zoom;
      const y = (e.clientY - canvasRect.top - pan.y) / zoom;

      // Create new node
      const newNode = {
        id: `node_${Date.now()}`,
        ...stepData,
        position: { x, y },
        config: {},
        status: 'not_configured',
      };

      onNodesChange([...nodes, newNode]);
    } catch (error) {
      console.error('Error adding node:', error);
    }
  };

  /**
   * Handle drag over
   */
  const handleDragOver = (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'copy';
  };

  /**
   * Handle node deletion
   */
  const handleNodeDelete = (nodeId) => {
    onNodesChange(nodes.filter((node) => node.id !== nodeId));

    // Remove connections involving this node
    onConnectionsChange(
      connections.filter(
        (conn) => conn.from !== nodeId && conn.to !== nodeId
      )
    );
  };

  /**
   * Handle node connection
   */
  const handleNodeConnect = (nodeId, type) => {
    if (type === 'output') {
      setConnectingFrom(nodeId);
    } else if (type === 'input' && connectingFrom) {
      // Create connection
      const newConnection = {
        id: `conn_${Date.now()}`,
        from: connectingFrom,
        to: nodeId,
      };

      onConnectionsChange([...connections, newConnection]);
      setConnectingFrom(null);
    }
  };

  /**
   * Handle canvas click (deselect)
   */
  const handleCanvasClick = () => {
    onNodeSelect(null);
    setConnectingFrom(null);
  };

  /**
   * Handle mouse down for panning
   */
  const handleMouseDown = (e) => {
    if (e.button === 1 || (e.button === 0 && e.metaKey)) {
      // Middle mouse or Cmd+Left click
      setIsPanning(true);
      setPanStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
    }
  };

  /**
   * Handle mouse move for panning
   */
  const handleMouseMove = (e) => {
    if (isPanning) {
      setPan({
        x: e.clientX - panStart.x,
        y: e.clientY - panStart.y,
      });
    }
  };

  /**
   * Handle mouse up
   */
  const handleMouseUp = () => {
    setIsPanning(false);
  };

  /**
   * Handle zoom
   */
  const handleZoom = (delta) => {
    setZoom((prev) => Math.max(0.1, Math.min(2, prev + delta)));
  };

  /**
   * Reset view
   */
  const handleResetView = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  /**
   * Get connection coordinates
   */
  const getConnectionCoordinates = (connection) => {
    const fromNode = nodes.find((n) => n.id === connection.from);
    const toNode = nodes.find((n) => n.id === connection.to);

    if (!fromNode || !toNode) return null;

    return {
      from: {
        x: fromNode.position.x * zoom + pan.x + 128 * zoom,
        y: (fromNode.position.y + 120) * zoom + pan.y,
      },
      to: {
        x: toNode.position.x * zoom + pan.x + 128 * zoom,
        y: toNode.position.y * zoom + pan.y,
      },
    };
  };

  return (
    <div className="relative w-full h-full bg-gray-50 overflow-hidden">
      {/* Controls */}
      <div className="absolute top-4 right-4 z-10 flex gap-2">
        <button
          onClick={() => handleZoom(0.1)}
          className="p-2 bg-white border border-gray-300 rounded-lg shadow-sm hover:bg-gray-50 transition-colors"
          title="Zoom In"
        >
          <PlusIcon className="w-5 h-5 text-gray-700" />
        </button>
        <button
          onClick={() => handleZoom(-0.1)}
          className="p-2 bg-white border border-gray-300 rounded-lg shadow-sm hover:bg-gray-50 transition-colors"
          title="Zoom Out"
        >
          <ArrowsPointingInIcon className="w-5 h-5 text-gray-700" />
        </button>
        <button
          onClick={handleResetView}
          className="p-2 bg-white border border-gray-300 rounded-lg shadow-sm hover:bg-gray-50 transition-colors"
          title="Reset View"
        >
          <ArrowsPointingOutIcon className="w-5 h-5 text-gray-700" />
        </button>
        <div className="px-3 py-2 bg-white border border-gray-300 rounded-lg shadow-sm text-sm font-medium text-gray-700">
          {Math.round(zoom * 100)}%
        </div>
      </div>

      {/* Info */}
      {nodes.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="text-center">
            <p className="text-lg font-medium text-gray-400">
              Drag steps from the palette to start building
            </p>
            <p className="text-sm text-gray-400 mt-2">
              Connect nodes by clicking the connection points
            </p>
          </div>
        </div>
      )}

      {/* Canvas */}
      <div
        ref={canvasRef}
        className={`w-full h-full ${
          isPanning ? 'cursor-grabbing' : 'cursor-grab'
        }`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onClick={handleCanvasClick}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        {/* Grid Background */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none">
          <defs>
            <pattern
              id="grid"
              width="20"
              height="20"
              patternUnits="userSpaceOnUse"
            >
              <circle cx="1" cy="1" r="1" fill="#e5e7eb" />
            </pattern>
            <marker
              id="arrowhead"
              markerWidth="10"
              markerHeight="10"
              refX="9"
              refY="3"
              orient="auto"
            >
              <polygon points="0 0, 10 3, 0 6" fill="#94a3b8" />
            </marker>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />

          {/* Connection Lines */}
          {connections.map((connection) => {
            const coords = getConnectionCoordinates(connection);
            return coords ? (
              <ConnectionLine
                key={connection.id}
                from={coords.from}
                to={coords.to}
              />
            ) : null;
          })}
        </svg>

        {/* Nodes Container */}
        <div
          className="relative"
          style={{
            transform: `scale(${zoom}) translate(${pan.x / zoom}px, ${
              pan.y / zoom
            }px)`,
            transformOrigin: '0 0',
          }}
        >
          {nodes.map((node) => (
            <WorkflowNode
              key={node.id}
              node={node}
              isSelected={selectedNodeId === node.id}
              onSelect={onNodeSelect}
              onDelete={handleNodeDelete}
              onConfigure={onNodeConfigure}
              onConnect={handleNodeConnect}
              position={node.position}
            />
          ))}
        </div>
      </div>

      {/* Connection Mode Indicator */}
      {connectingFrom && (
        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg shadow-lg">
          Click on a node's input to complete the connection
          <button
            onClick={() => setConnectingFrom(null)}
            className="ml-3 underline hover:no-underline"
          >
            Cancel
          </button>
        </div>
      )}
    </div>
  );
}
