/**
 * Card Component
 * Reusable card container component
 */

import { cn } from '@utils';

export default function Card({
  children,
  className = '',
  padding = true,
  hover = false,
  ...props
}) {
  return (
    <div
      className={cn(
        'bg-white rounded-lg shadow-sm border border-gray-200',
        padding && 'p-6',
        hover && 'hover:shadow-md transition-shadow duration-200',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

export function CardHeader({ children, className = '', ...props }) {
  return (
    <div
      className={cn('mb-4 pb-4 border-b border-gray-200', className)}
      {...props}
    >
      {children}
    </div>
  );
}

export function CardTitle({ children, className = '', ...props }) {
  return (
    <h3
      className={cn('text-lg font-semibold text-gray-900', className)}
      {...props}
    >
      {children}
    </h3>
  );
}

export function CardDescription({ children, className = '', ...props }) {
  return (
    <p className={cn('text-sm text-gray-600 mt-1', className)} {...props}>
      {children}
    </p>
  );
}

export function CardBody({ children, className = '', ...props }) {
  return (
    <div className={cn('', className)} {...props}>
      {children}
    </div>
  );
}

export function CardFooter({ children, className = '', ...props }) {
  return (
    <div
      className={cn('mt-4 pt-4 border-t border-gray-200', className)}
      {...props}
    >
      {children}
    </div>
  );
}
