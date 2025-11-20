/**
 * ExecutionTimeline Component
 * Step-by-step visualization for workflow executions
 */

import {
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  ArrowPathIcon,
  ExclamationCircleIcon,
} from '@heroicons/react/24/outline';
import { Badge } from '@components/ui';
import { formatDate, formatDuration } from '@utils/formatters';

/**
 * Get status icon
 */
const getStatusIcon = (status) => {
  const icons = {
    completed: CheckCircleIcon,
    failed: XCircleIcon,
    running: ArrowPathIcon,
    pending: ClockIcon,
    skipped: ExclamationCircleIcon,
  };
  return icons[status] || ClockIcon;
};

/**
 * Get status color
 */
const getStatusColor = (status) => {
  const colors = {
    completed: 'text-green-600 bg-green-100',
    failed: 'text-red-600 bg-red-100',
    running: 'text-blue-600 bg-blue-100',
    pending: 'text-gray-600 bg-gray-100',
    skipped: 'text-yellow-600 bg-yellow-100',
  };
  return colors[status] || 'text-gray-600 bg-gray-100';
};

/**
 * TimelineStep Component
 */
function TimelineStep({ step, isLast }) {
  const StatusIcon = getStatusIcon(step.status);
  const statusColor = getStatusColor(step.status);

  return (
    <div className="relative flex gap-4">
      {/* Timeline Line */}
      {!isLast && (
        <div className="absolute left-4 top-12 w-0.5 h-full bg-gray-200" />
      )}

      {/* Icon */}
      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${statusColor} z-10`}>
        <StatusIcon className="w-5 h-5" />
      </div>

      {/* Content */}
      <div className="flex-1 pb-8">
        <div className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
          {/* Header */}
          <div className="flex items-start justify-between mb-2">
            <div className="flex-1">
              <h4 className="font-medium text-gray-900">{step.name}</h4>
              <p className="text-sm text-gray-500 mt-1">{step.type}</p>
            </div>
            <div className="ml-4">
              <Badge
                variant={
                  step.status === 'completed'
                    ? 'success'
                    : step.status === 'failed'
                    ? 'error'
                    : step.status === 'running'
                    ? 'primary'
                    : 'secondary'
                }
              >
                {step.status}
              </Badge>
            </div>
          </div>

          {/* Metadata */}
          <div className="grid grid-cols-2 gap-2 text-xs text-gray-600 mb-3">
            {step.started_at && (
              <div>
                <span className="font-medium">Started:</span>{' '}
                {new Date(step.started_at).toLocaleTimeString()}
              </div>
            )}
            {step.completed_at && (
              <div>
                <span className="font-medium">Completed:</span>{' '}
                {new Date(step.completed_at).toLocaleTimeString()}
              </div>
            )}
            {step.duration && (
              <div>
                <span className="font-medium">Duration:</span>{' '}
                {formatDuration(step.duration)}
              </div>
            )}
          </div>

          {/* Input/Output */}
          {(step.input || step.output) && (
            <div className="space-y-2">
              {step.input && (
                <details className="group">
                  <summary className="text-sm font-medium text-gray-700 cursor-pointer hover:text-gray-900 flex items-center gap-2">
                    <span>Input</span>
                    <span className="text-xs text-gray-500">
                      ({JSON.stringify(step.input).length} bytes)
                    </span>
                  </summary>
                  <pre className="mt-2 p-3 bg-gray-50 rounded text-xs overflow-auto max-h-48 font-mono">
                    {JSON.stringify(step.input, null, 2)}
                  </pre>
                </details>
              )}

              {step.output && (
                <details className="group">
                  <summary className="text-sm font-medium text-gray-700 cursor-pointer hover:text-gray-900 flex items-center gap-2">
                    <span>Output</span>
                    <span className="text-xs text-gray-500">
                      ({JSON.stringify(step.output).length} bytes)
                    </span>
                  </summary>
                  <pre className="mt-2 p-3 bg-gray-50 rounded text-xs overflow-auto max-h-48 font-mono">
                    {JSON.stringify(step.output, null, 2)}
                  </pre>
                </details>
              )}
            </div>
          )}

          {/* Error Message */}
          {step.error && (
            <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm font-medium text-red-800 mb-1">Error</p>
              <p className="text-sm text-red-700">{step.error}</p>
            </div>
          )}

          {/* Logs */}
          {step.logs && step.logs.length > 0 && (
            <details className="mt-3">
              <summary className="text-sm font-medium text-gray-700 cursor-pointer hover:text-gray-900">
                Logs ({step.logs.length})
              </summary>
              <div className="mt-2 space-y-1 max-h-48 overflow-auto">
                {step.logs.map((log, index) => (
                  <div
                    key={index}
                    className="text-xs font-mono bg-gray-50 p-2 rounded"
                  >
                    <span className="text-gray-500">
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </span>
                    <span className="mx-2 text-gray-300">|</span>
                    <span className={
                      log.level === 'ERROR' ? 'text-red-600' :
                      log.level === 'WARNING' ? 'text-yellow-600' :
                      log.level === 'INFO' ? 'text-blue-600' :
                      'text-gray-600'
                    }>
                      {log.level}
                    </span>
                    <span className="mx-2 text-gray-300">|</span>
                    <span className="text-gray-700">{log.message}</span>
                  </div>
                ))}
              </div>
            </details>
          )}
        </div>
      </div>
    </div>
  );
}

/**
 * ExecutionTimeline Component
 */
export default function ExecutionTimeline({ steps = [] }) {
  if (steps.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No execution steps available</p>
      </div>
    );
  }

  return (
    <div className="space-y-0">
      {steps.map((step, index) => (
        <TimelineStep
          key={step.id || index}
          step={step}
          isLast={index === steps.length - 1}
        />
      ))}
    </div>
  );
}
