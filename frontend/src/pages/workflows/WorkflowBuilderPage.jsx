/**
 * WorkflowBuilderPage Component
 * Visual workflow builder with drag-and-drop interface
 */

import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import {
  ArrowLeftIcon,
  PlayIcon,
  DocumentDuplicateIcon,
  CheckIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
} from '@heroicons/react/24/outline';
import { Button, FormInput, Loading } from '@components/ui';
import WorkflowCanvas from '@components/workflows/WorkflowCanvas';
import NodePalette from '@components/workflows/NodePalette';
import NodeConfigModal from '@components/workflows/NodeConfigModal';
import { workflowService } from '@services';
import { ROUTES } from '@constants';
import toast from 'react-hot-toast';

/**
 * WorkflowBuilderPage Component
 */
export default function WorkflowBuilderPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [workflow, setWorkflow] = useState(null);
  const [workflowName, setWorkflowName] = useState('Untitled Workflow');
  const [workflowDescription, setWorkflowDescription] = useState('');
  const [nodes, setNodes] = useState([]);
  const [connections, setConnections] = useState([]);
  const [selectedNodeId, setSelectedNodeId] = useState(null);
  const [configModalOpen, setConfigModalOpen] = useState(false);
  const [isPaletteCollapsed, setIsPaletteCollapsed] = useState(false);

  /**
   * Load workflow if editing
   */
  useEffect(() => {
    if (id) {
      loadWorkflow();
    }
  }, [id]);

  /**
   * Load workflow
   */
  const loadWorkflow = async () => {
    try {
      setLoading(true);
      const data = await workflowService.getWorkflowById(id);

      setWorkflow(data);
      setWorkflowName(data.name);
      setWorkflowDescription(data.description || '');

      // Parse workflow definition
      if (data.definition) {
        setNodes(data.definition.nodes || []);
        setConnections(data.definition.connections || []);
      }
    } catch (error) {
      console.error('Error loading workflow:', error);
      toast.error('Failed to load workflow');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle save workflow
   */
  const handleSave = async () => {
    try {
      setSaving(true);

      const workflowData = {
        name: workflowName,
        description: workflowDescription,
        definition: {
          nodes,
          connections,
        },
        status: 'draft',
      };

      if (id) {
        await workflowService.updateWorkflow(id, workflowData);
        toast.success('Workflow updated successfully');
      } else {
        const newWorkflow = await workflowService.createWorkflow(workflowData);
        toast.success('Workflow created successfully');
        navigate(`${ROUTES.WORKFLOW_BUILDER}/${newWorkflow.id}`);
      }
    } catch (error) {
      console.error('Error saving workflow:', error);
      toast.error('Failed to save workflow');
    } finally {
      setSaving(false);
    }
  };

  /**
   * Handle publish workflow
   */
  const handlePublish = async () => {
    try {
      setSaving(true);

      const workflowData = {
        name: workflowName,
        description: workflowDescription,
        definition: {
          nodes,
          connections,
        },
        status: 'active',
      };

      if (id) {
        await workflowService.updateWorkflow(id, workflowData);
        toast.success('Workflow published successfully');
      } else {
        const newWorkflow = await workflowService.createWorkflow(workflowData);
        await workflowService.updateWorkflow(newWorkflow.id, {
          status: 'active',
        });
        toast.success('Workflow published successfully');
        navigate(`${ROUTES.WORKFLOW_DETAIL}/${newWorkflow.id}`);
      }
    } catch (error) {
      console.error('Error publishing workflow:', error);
      toast.error('Failed to publish workflow');
    } finally {
      setSaving(false);
    }
  };

  /**
   * Handle test workflow
   */
  const handleTest = async () => {
    if (nodes.length === 0) {
      toast.error('Add at least one step to test the workflow');
      return;
    }

    try {
      toast.success('Test execution started');
      // In a real app, this would trigger a test execution
    } catch (error) {
      console.error('Error testing workflow:', error);
      toast.error('Failed to start test execution');
    }
  };

  /**
   * Handle node configure
   */
  const handleNodeConfigure = (nodeId) => {
    setSelectedNodeId(nodeId);
    setConfigModalOpen(true);
  };

  /**
   * Handle save node configuration
   */
  const handleSaveNodeConfig = (updatedNode) => {
    setNodes((prev) =>
      prev.map((node) => (node.id === updatedNode.id ? updatedNode : node))
    );
    setConfigModalOpen(false);
  };

  /**
   * Get selected node
   */
  const selectedNode = nodes.find((node) => node.id === selectedNodeId);

  if (loading) {
    return <Loading.LoadingPage />;
  }

  return (
    <div className="h-screen flex flex-col bg-white">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 bg-white">
        <div className="flex items-center gap-4 flex-1 min-w-0">
          <button
            onClick={() => navigate(ROUTES.WORKFLOWS)}
            className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <ArrowLeftIcon className="w-5 h-5" />
          </button>

          <div className="flex-1 min-w-0">
            <FormInput
              type="text"
              value={workflowName}
              onChange={(e) => setWorkflowName(e.target.value)}
              className="text-lg font-semibold border-0 focus:ring-0 px-0"
              placeholder="Workflow Name"
            />
            <FormInput
              type="text"
              value={workflowDescription}
              onChange={(e) => setWorkflowDescription(e.target.value)}
              className="text-sm text-gray-600 border-0 focus:ring-0 px-0 mt-1"
              placeholder="Add a description..."
            />
          </div>
        </div>

        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="sm"
            onClick={handleTest}
            disabled={saving || nodes.length === 0}
          >
            <PlayIcon className="w-4 h-4 mr-2" />
            Test
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={handleSave}
            disabled={saving}
          >
            {saving ? (
              <>
                <Loading.Spinner size="sm" className="mr-2" />
                Saving...
              </>
            ) : (
              <>
                <DocumentDuplicateIcon className="w-4 h-4 mr-2" />
                Save Draft
              </>
            )}
          </Button>

          <Button size="sm" onClick={handlePublish} disabled={saving}>
            {saving ? (
              <>
                <Loading.Spinner size="sm" className="mr-2" />
                Publishing...
              </>
            ) : (
              <>
                <CheckIcon className="w-4 h-4 mr-2" />
                Publish
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Node Palette */}
        <div
          className={`${
            isPaletteCollapsed ? 'w-0' : 'w-80'
          } transition-all duration-300 flex-shrink-0`}
        >
          <NodePalette
            onStepDragStart={() => {}}
            isCollapsed={isPaletteCollapsed}
            onToggle={() => setIsPaletteCollapsed(true)}
          />
        </div>

        {/* Palette Toggle (when collapsed) */}
        {isPaletteCollapsed && (
          <button
            onClick={() => setIsPaletteCollapsed(false)}
            className="absolute left-0 top-1/2 transform -translate-y-1/2 z-10 p-2 bg-white border border-gray-300 rounded-r-lg shadow-md hover:bg-gray-50 transition-colors"
          >
            <ChevronRightIcon className="w-5 h-5 text-gray-600" />
          </button>
        )}

        {/* Canvas */}
        <div className="flex-1">
          <WorkflowCanvas
            nodes={nodes}
            connections={connections}
            onNodesChange={setNodes}
            onConnectionsChange={setConnections}
            onNodeSelect={setSelectedNodeId}
            onNodeConfigure={handleNodeConfigure}
            selectedNodeId={selectedNodeId}
          />
        </div>

        {/* Properties Panel (when node selected) */}
        {selectedNode && !configModalOpen && (
          <div className="w-80 border-l border-gray-200 bg-white p-6 overflow-y-auto">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Node Properties
            </h3>

            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">
                  Type
                </h4>
                <div className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: selectedNode.color }}
                  />
                  <span className="text-sm text-gray-900">
                    {selectedNode.name}
                  </span>
                </div>
              </div>

              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">
                  Description
                </h4>
                <p className="text-sm text-gray-600">
                  {selectedNode.description}
                </p>
              </div>

              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">
                  Status
                </h4>
                <span
                  className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    selectedNode.status === 'configured'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-yellow-100 text-yellow-800'
                  }`}
                >
                  {selectedNode.status || 'Not Configured'}
                </span>
              </div>

              {selectedNode.config && Object.keys(selectedNode.config).length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-2">
                    Configuration
                  </h4>
                  <pre className="text-xs bg-gray-50 p-3 rounded-lg overflow-auto max-h-64">
                    {JSON.stringify(selectedNode.config, null, 2)}
                  </pre>
                </div>
              )}

              <Button
                variant="outline"
                size="sm"
                onClick={() => handleNodeConfigure(selectedNode.id)}
                className="w-full"
              >
                Configure Node
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Status Bar */}
      <div className="px-6 py-3 border-t border-gray-200 bg-gray-50 flex items-center justify-between">
        <div className="flex items-center gap-6 text-sm text-gray-600">
          <span>
            <span className="font-medium">{nodes.length}</span> nodes
          </span>
          <span>
            <span className="font-medium">{connections.length}</span> connections
          </span>
          <span>
            Status:{' '}
            <span className="font-medium">
              {workflow?.status || 'Draft'}
            </span>
          </span>
        </div>

        <div className="text-xs text-gray-500">
          {workflow?.updated_at
            ? `Last saved: ${new Date(workflow.updated_at).toLocaleString()}`
            : 'Not saved yet'}
        </div>
      </div>

      {/* Node Configuration Modal */}
      <NodeConfigModal
        node={selectedNode}
        isOpen={configModalOpen}
        onClose={() => setConfigModalOpen(false)}
        onSave={handleSaveNodeConfig}
      />
    </div>
  );
}
