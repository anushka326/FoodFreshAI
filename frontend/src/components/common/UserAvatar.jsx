import React from 'react';
import { getAvatarById } from '../../assets/avatars/avatarCatalog.jsx';

/**
 * Neutral User Avatar Component
 * Displays user's themed avatar (from catalog), custom uploaded photo if present,
 * or falls back to a clean initials/icon badge in the Stitch brand palette.
 */
export function UserAvatar({
  src = null,
  avatar = null,
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

  // 1. Check if avatar identifier from themed catalog
  const avatarKey = avatar || src;
  const themedAvatar = typeof avatarKey === 'string' && !avatarKey.startsWith('http') && !avatarKey.startsWith('data:') && !avatarKey.startsWith('/')
    ? getAvatarById(avatarKey)
    : null;

  if (themedAvatar) {
    return (
      <div
        className={`${sizeClasses[size] || sizeClasses.md} rounded-full flex items-center justify-center p-0.5 overflow-hidden shrink-0 select-none shadow-2xs border border-primary/20 ${className}`}
        style={{ backgroundColor: themedAvatar.bg || '#f0fdf4' }}
        title={`${themedAvatar.name} (${themedAvatar.subtitle})`}
        aria-label={`${themedAvatar.name} Avatar`}
      >
        <div className="w-full h-full flex items-center justify-center">
          {themedAvatar.svg}
        </div>
      </div>
    );
  }

  // 2. Uploaded image URL if present
  if (src && (src.startsWith('http') || src.startsWith('data:') || src.startsWith('/'))) {
    return (
      <img
        src={src}
        alt={name ? `${name} Profile` : 'Kitchen Profile'}
        className={`${sizeClasses[size] || sizeClasses.md} rounded-full object-cover border border-surface-container-high shrink-0 ${className}`}
      />
    );
  }

  // 3. Fallback initials or icon
  const initials = name && name.trim() && name !== 'Chef'
    ? name
        .trim()
        .split(' ')
        .filter(Boolean)
        .slice(0, 2)
        .map((n) => n[0].toUpperCase())
        .join('')
    : null;

  return (
    <div
      className={`${sizeClasses[size] || sizeClasses.md} rounded-full bg-secondary-container/60 border border-secondary/30 text-primary font-extrabold flex items-center justify-center select-none shadow-2xs shrink-0 ${className}`}
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
