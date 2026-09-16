import React from 'react';

/**
 * Neutral User Avatar Component
 * Displays user's uploaded avatar if present, or falls back to a clean
 * initials/icon badge in the Stitch brand palette.
 */
export function UserAvatar({
  src = null,
  name = 'Chef',
  size = 'md', // 'sm' | 'md' | 'lg' | 'xl'
  className = '',
}) {
  const sizeClasses = {
    sm: 'w-7 h-7 text-xs',
    md: 'w-9 h-9 text-xs',
    lg: 'w-12 h-12 text-sm',
    xl: 'w-16 h-16 text-lg',
  };

  const iconSizes = {
    sm: 'text-[16px]',
    md: 'text-[18px]',
    lg: 'text-[24px]',
    xl: 'text-[32px]',
  };

  // Extract initials if name is provided
  const initials = name && name.trim() && name !== 'Chef'
    ? name
        .trim()
        .split(' ')
        .filter(Boolean)
        .slice(0, 2)
        .map((n) => n[0].toUpperCase())
        .join('')
    : null;

  if (src) {
    return (
      <img
        src={src}
        alt={name ? `${name} Profile` : 'Kitchen Profile'}
        className={`${sizeClasses[size] || sizeClasses.md} rounded-full object-cover border border-surface-container-high ${className}`}
      />
    );
  }

  return (
    <div
      className={`${sizeClasses[size] || sizeClasses.md} rounded-full bg-secondary-container/60 border border-secondary/30 text-primary font-extrabold flex items-center justify-center select-none shadow-2xs ${className}`}
      title={name || 'Kitchen Profile'}
      aria-label={name || 'Kitchen Profile'}
    >
      {initials ? (
        <span>{initials}</span>
      ) : (
        <span className={`material-symbols-outlined ${iconSizes[size] || iconSizes.md} text-primary`}>
          person
        </span>
      )}
    </div>
  );
}

export default UserAvatar;
