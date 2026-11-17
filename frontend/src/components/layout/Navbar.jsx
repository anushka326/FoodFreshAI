import React, { useState, useEffect } from 'react';
import { useAuth } from '../../hooks/useAuth.js';
import { UserAvatar } from '../common/UserAvatar.jsx';
import { NotificationCenter } from '../notifications/NotificationCenter.jsx';
import { PwaInstallPrompt } from '../common/PwaInstallPrompt.jsx';
import { offlineSyncService } from '../../services/offlineSyncService.js';
import { ENDPOINTS } from '../../config/api.js';

export function Navbar({ onMenuToggle, currentRoute, navigate }) {
  const { user } = useAuth();
  const displayName = user?.fullName || 'Kitchen Chef';
  const [isOnline, setIsOnline] = useState(typeof navigator !== 'undefined' ? navigator.onLine : true);
  const [backendLive, setBackendLive] = useState(false);

  useEffect(() => {
    let active = true;
    const probe = async () => {
      try {
        const res = await fetch(ENDPOINTS.HEALTH, { signal: AbortSignal.timeout(2500) });
        if (active) setBackendLive(res.ok);
      } catch {
        if (active) setBackendLive(false);
      }
    };
    probe();
    const timer = setInterval(probe, 8000);
    return () => {
      active = false;
      clearInterval(timer);
    };
  }, []);

  useEffect(() => {
    const unsub = offlineSyncService.subscribe((state) => {
      setIsOnline(state.isOnline);
    });
    return unsub;
  }, []);

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
      <div className="flex items-center gap-2.5 sm:gap-4">
        {/* Backend Live Indicator */}
        <div
          className={`hidden md:flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold border transition-colors shadow-2xs ${
            backendLive
              ? 'bg-emerald-50 text-emerald-800 border-emerald-300'
              : 'bg-surface-container text-on-surface-variant border-surface-container-high'
          }`}
          title={
            backendLive
              ? 'FastAPI Backend is running on http://127.0.0.1:8000'
              : 'Backend disconnected (Demo mode active)'
          }
        >
          <span
            className={`w-2 h-2 rounded-full ${
              backendLive ? 'bg-emerald-500 animate-pulse' : 'bg-outline'
            }`}
          />
          <span>{backendLive ? 'Backend Live (:8000)' : 'Demo Mode'}</span>
        </div>

        {/* PWA Install Button */}
        <PwaInstallPrompt variant="navbar-pill" />

        {/* Online / Offline Status Badge */}
        {!isOnline ? (
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-100 text-amber-900 border border-amber-300 text-xs font-bold shadow-2xs">
            <span className="w-2 h-2 rounded-full bg-amber-600 animate-pulse" />
            <span>Offline</span>
          </div>
        ) : (
          <div className="hidden sm:flex items-center gap-2 px-3 py-1 rounded-full bg-surface-container-low shadow-2xs border border-surface-container-high/50">
            <span className="w-2 h-2 rounded-full bg-secondary animate-pulse" />
            <span className="text-xs font-semibold text-primary">Pantry Guard Active</span>
          </div>
        )}

        {/* Smart Notifications Bell & Drawer */}
        <NotificationCenter navigate={navigate} />

        {/* User Profile Pill */}
        <button
          type="button"
          onClick={() => navigate('/settings')}
          className="flex items-center gap-2.5 p-1 sm:pr-3 rounded-full hover:bg-surface-container-high transition-colors cursor-pointer"
        >
          <div className="relative">
            <UserAvatar
              avatar={user?.avatar || user?.avatarUrl}
              src={user?.avatar || user?.avatarUrl}
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
