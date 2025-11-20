/**
 * Badge Component
 * Reusable badge component for status indicators
 */

import { cn } from '@utils';

const badgeVariants = {
  primary: 'bg-primary-100 text-primary-800',
  secondary: 'bg-gray-100 text-gray-800',
  success: 'bg-success-100 text-success-800',
  warning: 'bg-warning-100 text-warning-800',
  error: 'bg-error-100 text-error-800',
  info: 'bg-blue-100 text-blue-800',
};

const badgeSizes = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-2.5 py-0.5 text-xs',
  lg: 'px-3 py-1 text-sm',
};

export default function Badge({
  children,
  variant = 'primary',
  size = 'md',
  dot = false,
  className = '',
  ...props
}) {
  return (
    <span
      className={cn(
        'inline-flex items-center font-medium rounded-full',
        badgeVariants[variant],
        badgeSizes[size],
        className
      )}
      {...props}
    >
      {dot && (
        <span
          className={cn(
            'w-1.5 h-1.5 rounded-full mr-1.5',
            variant === 'primary' && 'bg-primary-600',
            variant === 'secondary' && 'bg-gray-600',
            variant === 'success' && 'bg-success-600',
            variant === 'warning' && 'bg-warning-600',
            variant === 'error' && 'bg-error-600',
            variant === 'info' && 'bg-blue-600'
          )}
        />
      )}
      {children}
    </span>
  );
}
