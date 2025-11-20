/**
 * NodeConfigModal Component
 * Modal for configuring workflow node settings
 */

import { useState, useEffect } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import { Modal, Button, FormInput, FormSelect, FormTextarea } from '@components/ui';

/**
 * NodeConfigModal Component
 */
export default function NodeConfigModal({ node, isOpen, onClose, onSave }) {
  const [config, setConfig] = useState({});
  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (node) {
      setConfig(node.config || {});
      setErrors({});
    }
  }, [node]);

  if (!node) return null;

  /**
   * Handle field change
   */
  const handleChange = (field, value) => {
    setConfig((prev) => ({
      ...prev,
      [field]: value,
    }));

    // Clear error for this field
    if (errors[field]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  /**
   * Validate configuration
   */
  const validate = () => {
    const newErrors = {};

    // Basic validation - can be extended based on step type
    if (!config.name || config.name.trim() === '') {
      newErrors.name = 'Step name is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  /**
   * Handle save
   */
  const handleSave = () => {
    if (validate()) {
      onSave({
        ...node,
        config,
        status: 'configured',
      });
      onClose();
    }
  };

  /**
   * Render field based on type
   */
  const renderField = (field, index) => {
    const value = config[field] || '';

    // Determine field type based on name
    if (field === 'prompt' || field === 'description') {
      return (
        <FormTextarea
          key={field}
          label={field.charAt(0).toUpperCase() + field.slice(1).replace(/_/g, ' ')}
          name={field}
          value={value}
          onChange={(e) => handleChange(field, e.target.value)}
          error={errors[field]}
          rows={4}
          placeholder={`Enter ${field}...`}
        />
      );
    }

    if (field === 'temperature') {
      return (
        <FormInput
          key={field}
          label="Temperature"
          name={field}
          type="number"
          min="0"
          max="1"
          step="0.1"
          value={value}
          onChange={(e) => handleChange(field, parseFloat(e.target.value))}
          error={errors[field]}
          placeholder="0.7"
        />
      );
    }

    if (field === 'max_length' || field === 'maxLength') {
      return (
        <FormInput
          key={field}
          label="Max Length"
          name={field}
          type="number"
          min="1"
          value={value}
          onChange={(e) => handleChange(field, parseInt(e.target.value))}
          error={errors[field]}
          placeholder="1000"
        />
      );
    }

    if (field === 'method') {
      return (
        <FormSelect
          key={field}
          label="HTTP Method"
          name={field}
          value={value}
          onChange={(e) => handleChange(field, e.target.value)}
          error={errors[field]}
          options={[
            { value: '', label: 'Select method' },
            { value: 'GET', label: 'GET' },
            { value: 'POST', label: 'POST' },
            { value: 'PUT', label: 'PUT' },
            { value: 'PATCH', label: 'PATCH' },
            { value: 'DELETE', label: 'DELETE' },
          ]}
        />
      );
    }

    // Default to text input
    return (
      <FormInput
        key={field}
        label={field.charAt(0).toUpperCase() + field.slice(1).replace(/_/g, ' ')}
        name={field}
        type="text"
        value={value}
        onChange={(e) => handleChange(field, e.target.value)}
        error={errors[field]}
        placeholder={`Enter ${field}...`}
      />
    );
  };

  // Get configuration fields based on step type
  const getConfigFields = () => {
    const fields = ['name'];

    // Add step-specific fields
    if (node.config?.settings) {
      fields.push(...node.config.settings);
    }

    // Add input fields
    if (node.config?.inputs) {
      fields.push(...node.config.inputs);
    }

    return [...new Set(fields)]; // Remove duplicates
  };

  const configFields = getConfigFields();

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`Configure ${node.name}`}
      maxWidth="2xl"
    >
      <div className="space-y-4">
        {/* Node Info */}
        <div className="p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-medium text-gray-900">{node.name}</h4>
              <p className="text-sm text-gray-600 mt-1">{node.description}</p>
            </div>
            <div
              className="px-3 py-1 text-xs font-medium text-white rounded-full"
              style={{ backgroundColor: node.color }}
            >
              {node.category}
            </div>
          </div>
        </div>

        {/* Configuration Form */}
        <div className="space-y-4">
          {configFields.map((field, index) => renderField(field, index))}
        </div>

        {/* JSON Preview */}
        <details className="mt-4">
          <summary className="text-sm font-medium text-gray-700 cursor-pointer hover:text-gray-900">
            View JSON Configuration
          </summary>
          <pre className="mt-2 p-4 bg-gray-50 rounded-lg text-xs overflow-auto max-h-48">
            {JSON.stringify(config, null, 2)}
          </pre>
        </details>

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-4 border-t">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleSave}>Save Configuration</Button>
        </div>
      </div>
    </Modal>
  );
}
