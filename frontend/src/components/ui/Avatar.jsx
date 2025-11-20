/**
 * Avatar Component
 * Reusable avatar component with fallback to initials
 */

import { cn, getInitials } from '@utils';

const avatarSizes = {
  xs: 'h-6 w-6 text-xs',
  sm: 'h-8 w-8 text-sm',
  md: 'h-10 w-10 text-base',
  lg: 'h-12 w-12 text-lg',
  xl: 'h-16 w-16 text-xl',
  '2xl': 'h-20 w-20 text-2xl',
};

export default function Avatar({
  src,
  name,
  size = 'md',
  className = '',
  ...props
}) {
  const initials = name ? getInitials(name) : '?';

  return (
    <div
      className={cn(
        'relative inline-flex items-center justify-center rounded-full overflow-hidden bg-gray-300',
        avatarSizes[size],
        className
      )}
      {...props}
    >
      {src ? (
        <img
          src={src}
          alt={name || 'Avatar'}
          className="h-full w-full object-cover"
        />
      ) : (
        <span className="font-medium text-gray-700">{initials}</span>
      )}
    </div>
  );
}

/**
 * Avatar Group Component
 */
export function AvatarGroup({ avatars = [], max = 3, size = 'md', className = '' }) {
  const displayAvatars = avatars.slice(0, max);
  const remaining = avatars.length - max;

  return (
    <div className={cn('flex -space-x-2', className)}>
      {displayAvatars.map((avatar, index) => (
        <Avatar
          key={index}
          src={avatar.src}
          name={avatar.name}
          size={size}
          className="ring-2 ring-white"
        />
      ))}
      {remaining > 0 && (
        <div
          className={cn(
            'relative inline-flex items-center justify-center rounded-full bg-gray-200 ring-2 ring-white font-medium text-gray-600',
            avatarSizes[size]
          )}
        >
          +{remaining}
        </div>
      )}
    </div>
  );
}
