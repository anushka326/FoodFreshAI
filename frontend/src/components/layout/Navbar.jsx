import React from 'react';
import { useAuth } from '../../hooks/useAuth.js';
import { UserAvatar } from '../common/UserAvatar.jsx';

export function Navbar({ onMenuToggle, currentRoute, navigate }) {
  const { user } = useAuth();
  const displayName = user?.fullName || 'Kitchen Chef';

  return (
    <header className="fixed top-0 right-0 left-0 lg:left-72 h-20 bg-surface/85 backdrop-blur-xl shadow-[0_1px_8px_rgba(0,0,0,0.04)] z-30 flex items-center justify-between px-4 sm:px-8 lg:px-12 border-b border-surface-container-high/40">
      {/* Left Title & Mobile Menu Trigger */}
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onMenuToggle}
          className="lg:hidden p-2 rounded-xl text-on-surface hover:bg-surface-container-high transition-colors cursor-pointer"
          aria-label="Toggle navigation drawer"
        >
          <span className="material-symbols-outlined text-[24px]">menu</span>
        </button>
        <div className="flex flex-col">
          <span className="text-[11px] font-bold text-secondary tracking-wider uppercase leading-tight">
            Fresh Intelligence
          </span>
          <span className="text-xl font-bold text-on-surface tracking-tight leading-tight">
            Good day, Chef
          </span>
        </div>
      </div>

      {/* Right User Telemetry & Avatar */}
      <div className="flex items-center gap-3 sm:gap-6">
        {/* Pantry Guard Active Indicator */}
        <div className="hidden sm:flex items-center gap-2 px-3 py-1 rounded-full bg-surface-container-low shadow-2xs border border-surface-container-high/50">
          <span className="w-2 h-2 rounded-full bg-secondary animate-pulse" />
          <span className="text-xs font-semibold text-primary">Pantry Guard Active</span>
        </div>

        {/* User Profile Pill */}
        <button
          type="button"
          onClick={() => navigate('/settings')}
          className="flex items-center gap-2.5 p-1 sm:pr-3 rounded-full hover:bg-surface-container-high transition-colors cursor-pointer"
        >
          <div className="relative">
            <UserAvatar
              src={user?.avatarUrl}
              name={displayName}
              size="md"
            />
            <span className="absolute bottom-0 right-0 w-2.5 h-2.5 bg-secondary border-2 border-white rounded-full" />
          </div>
          <span className="hidden md:inline-block text-xs font-bold text-on-surface">
            {displayName}
          </span>
          <span className="material-symbols-outlined text-on-surface-variant text-[18px]">
            expand_more
          </span>
        </button>
      </div>
    </header>
  );
}

export default Navbar;
