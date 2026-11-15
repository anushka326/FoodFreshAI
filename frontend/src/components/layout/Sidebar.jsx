import React from 'react';
import { BRANDING_ASSETS } from '../../assets/branding/index.js';
import { MASCOT_ASSETS } from '../../assets/mascot/index.js';
import { authService } from '../../services/authService.js';
import { useAuth } from '../../hooks/useAuth.js';
import { UserAvatar } from '../common/UserAvatar.jsx';
import { PwaInstallPrompt } from '../common/PwaInstallPrompt.jsx';

export function Sidebar({ currentRoute, navigate, isOpen, onClose }) {
  const { user } = useAuth();
  const navItems = [
    {
      id: 'dashboard',
      path: '/dashboard',
      label: 'Dashboard',
      icon: 'dashboard',
    },
    {
      id: 'analyze',
      path: '/analyze',
      label: 'Analyze Food',
      icon: 'search_insights',
    },
    {
      id: 'packaged-food',
      path: '/packaged-food',
      label: 'Packaged Foods',
      icon: 'barcode_scanner',
      badge: 'OCR',
    },
    {
      id: 'history',
      path: '/history',
      label: 'History',
      icon: 'history',
    },
    {
      id: 'alerts',
      path: '/alerts',
      label: 'Expiry Alerts',
      icon: 'notifications_active',
      badge: 'ALERTS',
    },
    {
      id: 'recipes',
      path: '/recipes',
      label: 'Recipe Ideas',
      icon: 'restaurant_menu',
      badge: 'NEW',
    },
    {
      id: 'analytics',
      path: '/analytics',
      label: 'Impact Analytics',
      icon: 'insights',
    },
    {
      id: 'fresho-buddy',
      path: '/fresho-buddy',
      label: 'FreshoBuddy AI',
      icon: 'leaf',
      isCustomMascot: true,
      badge: 'AI',
    },
    {
      id: 'settings',
      path: '/settings',
      label: 'Settings',
      icon: 'settings',
    },
  ];

  const handleNavClick = (path) => {
    navigate(path);
    if (onClose) onClose();
  };

  const handleLogout = async () => {
    await authService.logout();
    if (onClose) onClose();
    navigate('/login');
  };

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 bg-primary/25 backdrop-blur-xs z-40 lg:hidden transition-opacity"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed left-0 top-0 h-full w-72 bg-surface-container-lowest z-50 flex flex-col justify-between shadow-[0_4px_24px_rgba(30,81,40,0.05)] border-r border-surface-container-high/60 transition-transform duration-300 ${
          isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        <div className="flex flex-col">
          {/* Header & Logo */}
          <div className="h-20 px-6 flex items-center justify-between border-b border-surface-container-low">
            <button
              type="button"
              onClick={() => handleNavClick('/')}
              className="flex items-center gap-3 text-left group"
            >
              <div className="w-10 h-10 rounded-2xl bg-white border border-surface-container-high/80 flex items-center justify-center p-1.5 shadow-2xs group-hover:scale-105 transition-transform">
                <img
                  src={BRANDING_ASSETS.logoUrl}
                  alt={BRANDING_ASSETS.logoAlt}
                  className="w-full h-full object-contain"
                />
              </div>
              <div className="flex flex-col">
                <span className="font-extrabold text-lg text-primary tracking-tight leading-tight">
                  FoodFresh <span className="text-secondary">AI</span>
                </span>
                <span className="text-[11px] font-semibold text-on-surface-variant leading-tight">
                  Know. Save. Waste Less.
                </span>
              </div>
            </button>

            {/* Mobile Close Button */}
            <button
              type="button"
              onClick={onClose}
              className="lg:hidden p-1.5 rounded-lg text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface"
              aria-label="Close menu"
            >
              <span className="material-symbols-outlined text-[20px]">close</span>
            </button>
          </div>

          {/* Navigation Links */}
          <div className="px-4 py-6">
            <nav className="flex flex-col gap-1.5">
              {navItems.map((item) => {
                const isActive = currentRoute === item.path;
                return (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => handleNavClick(item.path)}
                    className={`flex items-center justify-between px-4 py-3 rounded-full text-sm font-semibold transition-all cursor-pointer ${
                      isActive
                        ? 'bg-primary-container text-on-primary shadow-[0_4px_12px_-2px_rgba(30,81,40,0.14)]'
                        : 'text-on-surface-variant hover:bg-surface-container-high/70 hover:text-on-surface'
                    }`}
                  >
                    <div className="flex items-center gap-3.5">
                      {item.isCustomMascot ? (
                        <div className="w-5 h-5 flex items-center justify-center">
                          <img
                            src={MASCOT_ASSETS.freshoBuddyUrl}
                            alt="FreshoBuddy"
                            className="w-5 h-5 object-contain"
                          />
                        </div>
                      ) : (
                        <span className={`material-symbols-outlined text-[20px] ${isActive ? 'text-on-primary' : 'text-secondary'}`}>
                          {item.icon}
                        </span>
                      )}
                      <span>{item.label}</span>
                    </div>

                    {item.badge && (
                      <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider ${
                        isActive ? 'bg-white/20 text-white' : 'bg-secondary-container text-on-secondary-container'
                      }`}>
                        {item.badge}
                      </span>
                    )}
                  </button>
                );
              })}
            </nav>
          </div>
        </div>

        {/* Bottom Section: User Profile, Pantry Ecology & Logout */}
        <div className="p-4 space-y-3">
          {/* User Profile Quick Card */}
          <button
            type="button"
            onClick={() => handleNavClick('/settings')}
            className="w-full p-2 rounded-2xl bg-surface hover:bg-surface-container-high/60 border border-surface-container-high/60 flex items-center gap-2.5 transition-all text-left group cursor-pointer shadow-2xs"
            title="View Profile and Change Avatar"
          >
            <UserAvatar
              avatar={user?.avatar || user?.avatarUrl}
              src={user?.avatar || user?.avatarUrl}
              name={user?.fullName || 'Kitchen Chef'}
              size="sm"
            />
            <div className="flex-1 min-w-0">
              <p className="text-xs font-bold text-on-surface truncate group-hover:text-primary transition-colors">
                {user?.fullName || 'Kitchen Chef'}
              </p>
              <p className="text-[10px] text-on-surface-variant truncate">
                View Settings
              </p>
            </div>
            <span className="material-symbols-outlined text-[16px] text-on-surface-variant group-hover:text-primary transition-colors">
              chevron_right
            </span>
          </button>

          {/* PWA Install Card (when installable) */}
          <PwaInstallPrompt variant="sidebar-card" />

          {/* Pantry Ecology Micro Badge */}
          <div className="p-3.5 rounded-2xl bg-surface-container-low/80 border border-surface-container-high/60 shadow-2xs">
            <div className="flex items-center gap-2 text-xs font-bold text-primary">
              <span className="material-symbols-outlined text-secondary text-[18px]">eco</span>
              <span>Pantry Ecology</span>
            </div>
            <p className="text-[11px] text-on-surface-variant mt-1 leading-snug">
              Food longevity index at 94% this week.
            </p>
          </div>

          {/* Logout Trigger */}
          <button
            type="button"
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-4 py-2.5 rounded-full text-sm font-semibold text-on-surface-variant hover:text-red-700 hover:bg-red-50/70 transition-colors cursor-pointer"
          >
            <span className="material-symbols-outlined text-[20px]">logout</span>
            <span>Logout</span>
          </button>
        </div>
      </aside>
    </>
  );
}

export default Sidebar;
