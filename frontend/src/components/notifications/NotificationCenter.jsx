import React, { useState, useEffect, useCallback, useRef } from 'react';
import { createPortal } from 'react-dom';
import { notificationService } from '../../services/notificationService.js';

const TYPE_CONFIG = {
  expired: {
    label: 'Expired',
    badgeClass: 'bg-red-100 text-red-800 border-red-200',
    icon: 'dangerous',
    iconColor: 'text-red-600',
  },
  expiring_today: {
    label: 'Expires Today 🔥',
    badgeClass: 'bg-rose-100 text-rose-800 border-rose-200 font-extrabold',
    icon: 'alarm',
    iconColor: 'text-rose-600',
  },
  expiring_soon: {
    label: 'Expiring Soon ⏳',
    badgeClass: 'bg-amber-100 text-amber-800 border-amber-200',
    icon: 'hourglass_bottom',
    iconColor: 'text-amber-600',
  },
  high_priority: {
    label: 'Eat First ⭐',
    badgeClass: 'bg-orange-100 text-orange-800 border-orange-200',
    icon: 'priority_high',
    iconColor: 'text-orange-600',
  },
};

export function NotificationCenter({ navigate }) {
  const [isOpen, setIsOpen] = useState(false);
  const [data, setData] = useState({
    notifications: [],
    unread_count: 0,
    total_count: 0,
    summary: {},
  });
  const [activeFilter, setActiveFilter] = useState('all'); // 'all' | 'unread' | 'critical' | 'expiring_soon'
  const [loading, setLoading] = useState(false);
  const drawerRef = useRef(null);

  const fetchNotifications = useCallback(async () => {
    setLoading(true);
    try {
      const res = await notificationService.getNotifications();
      setData(res);
    } catch (e) {
      console.warn('Failed to fetch notifications:', e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchNotifications();
    // Periodically sync alerts every 45 seconds while user is active
    const interval = setInterval(fetchNotifications, 45000);
    return () => clearInterval(interval);
  }, [fetchNotifications]);

  // Lock background scrolling and attach ESC key listener when drawer is open
  useEffect(() => {
    if (!isOpen) return;
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        setIsOpen(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => {
      document.body.style.overflow = prevOverflow;
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen]);

  const handleToggle = () => {
    setIsOpen((prev) => {
      const next = !prev;
      if (next) {
        fetchNotifications();
      }
      return next;
    });
  };

  const handleMarkAsRead = async (id, e) => {
    if (e) e.stopPropagation();
    await notificationService.markAsRead(id);
    setData((prev) => ({
      ...prev,
      unread_count: Math.max(0, prev.unread_count - 1),
      notifications: prev.notifications.map((n) => (n.id === id ? { ...n, isRead: true } : n)),
    }));
  };

  const handleMarkAsUnread = async (id, e) => {
    if (e) e.stopPropagation();
    await notificationService.markAsUnread(id);
    setData((prev) => ({
      ...prev,
      unread_count: prev.unread_count + 1,
      notifications: prev.notifications.map((n) => (n.id === id ? { ...n, isRead: false } : n)),
    }));
  };

  const handleMarkAllRead = async () => {
    const unreadIds = data.notifications.filter((n) => !n.isRead).map((n) => n.id);
    if (unreadIds.length === 0) return;
    await notificationService.markAllAsRead(unreadIds);
    setData((prev) => ({
      ...prev,
      unread_count: 0,
      notifications: prev.notifications.map((n) => ({ ...n, isRead: true })),
    }));
  };

  const handleActionClick = (url) => {
    setIsOpen(false);
    if (navigate && url) {
      navigate(url);
    }
  };

  // Filter items
  const filteredNotifications = data.notifications.filter((n) => {
    if (activeFilter === 'unread') return !n.isRead;
    if (activeFilter === 'critical') return n.type === 'expired' || n.type === 'expiring_today';
    if (activeFilter === 'expiring_soon') return n.type === 'expiring_soon';
    return true;
  });

  const hasCritical = (data.summary.expired || 0) + (data.summary.expiring_today || 0) > 0;

  return (
    <>
      {/* ── BELL TRIGGER BUTTON ── */}
      <button
        type="button"
        onClick={handleToggle}
        className="relative p-2 rounded-full text-on-surface-variant hover:text-primary hover:bg-surface-container transition-all cursor-pointer"
        aria-label={`Pantry notifications (${data.unread_count} unread)`}
        title="Pantry Expiry Alerts & Smart Notifications"
      >
        <span className="material-symbols-outlined text-[24px]">notifications</span>

        {data.unread_count > 0 && (
          <span
            className={`absolute top-1 right-1 flex items-center justify-center min-w-[18px] h-[18px] px-1 text-[10px] font-extrabold text-white rounded-full shadow-sm animate-pulse ${
              hasCritical ? 'bg-error' : 'bg-secondary'
            }`}
          >
            {data.unread_count > 99 ? '99+' : data.unread_count}
          </span>
        )}
      </button>

      {/* ── NOTIFICATION DRAWER / OVERLAY PORTAL (ESCAPES NAVBAR BACKDROP-BLUR CONTAINING BLOCK) ── */}
      {isOpen &&
        typeof document !== 'undefined' &&
        createPortal(
          <div className="fixed inset-0 z-[9999] flex justify-end animate-in fade-in duration-200">
            {/* Backdrop */}
            <div
              onClick={() => setIsOpen(false)}
              className="fixed inset-0 bg-primary/40 backdrop-blur-xs transition-opacity duration-300"
              aria-hidden="true"
            />

            {/* Full-Height Drawer Container */}
            <div
              ref={drawerRef}
              className="relative w-full max-w-md sm:max-w-lg bg-white h-screen shadow-2xl flex flex-col justify-between overflow-hidden z-10 border-l border-surface-container-high animate-in slide-in-from-right duration-300"
            >
              {/* Top Bar */}
              <div className="p-5 sm:p-6 border-b border-surface-container-low bg-surface-container-lowest/90 backdrop-blur-xs">
                <div className="flex items-center justify-between gap-3 mb-2">
                  <div className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-secondary text-[22px]">
                      notifications_active
                    </span>
                    <h2 className="text-lg font-extrabold text-primary tracking-tight">
                      Expiry Alerts & Notifications
                    </h2>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <button
                      type="button"
                      onClick={() => handleActionClick('/alerts')}
                      className="px-2.5 py-1 rounded-full bg-secondary-container hover:bg-secondary text-on-secondary-container hover:text-white text-[11px] font-bold transition-all flex items-center gap-1 cursor-pointer"
                      title="Open full page alert view"
                    >
                      <span className="material-symbols-outlined text-[14px]">open_in_new</span>
                      <span className="hidden sm:inline">Alerts Page</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => setIsOpen(false)}
                      className="p-1.5 text-on-surface-variant hover:text-on-surface rounded-full hover:bg-surface-container cursor-pointer"
                      aria-label="Close notifications panel"
                    >
                      <span className="material-symbols-outlined text-[20px]">close</span>
                    </button>
                  </div>
                </div>

                <p className="text-xs text-on-surface-variant">
                  Live alerts based on your actual pantry inventory and Eat First priority.
                </p>

                {/* Metric Counters & Mark All As Read */}
                <div className="mt-4 flex items-center justify-between gap-2 pt-3 border-t border-surface-container-low">
                  <div className="flex items-center gap-2 text-xs font-semibold">
                    <span className="px-2 py-0.5 rounded-full bg-surface-container-high text-primary font-bold">
                      {data.total_count} total
                    </span>
                    {data.unread_count > 0 ? (
                      <span className="px-2 py-0.5 rounded-full bg-secondary-container text-on-secondary-container font-extrabold">
                        {data.unread_count} unread
                      </span>
                    ) : (
                      <span className="text-emerald-700 font-medium">All caught up</span>
                    )}
                  </div>

                  {data.unread_count > 0 && (
                    <button
                      type="button"
                      onClick={handleMarkAllRead}
                      className="text-xs font-bold text-secondary hover:text-primary transition-colors cursor-pointer"
                    >
                      Mark all read
                    </button>
                  )}
                </div>

                {/* Filter Tabs */}
                <div className="mt-3 flex items-center gap-1.5 overflow-x-auto pb-1">
                  {[
                    { id: 'all', label: `All (${data.total_count})` },
                    { id: 'unread', label: `Unread (${data.unread_count})` },
                    {
                      id: 'critical',
                      label: `Critical (${(data.summary.expired || 0) + (data.summary.expiring_today || 0)})`,
                    },
                    { id: 'expiring_soon', label: `Expiring Soon (${data.summary.expiring_soon || 0})` },
                  ].map((tab) => (
                    <button
                      key={tab.id}
                      type="button"
                      onClick={() => setActiveFilter(tab.id)}
                      className={`px-3 py-1 rounded-full text-[11px] font-bold whitespace-nowrap transition-all cursor-pointer ${
                        activeFilter === tab.id
                          ? 'bg-primary text-white shadow-2xs'
                          : 'bg-surface-container-low text-on-surface-variant hover:bg-surface-container'
                      }`}
                    >
                      {tab.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Notification List Scrollable Area */}
              <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-3">
                {loading && data.notifications.length === 0 ? (
                  <div className="flex flex-col items-center justify-center py-16 space-y-3 text-on-surface-variant">
                    <div className="w-8 h-8 border-3 border-primary border-t-transparent rounded-full animate-spin" />
                    <span className="text-xs font-medium">Checking live pantry shelf life…</span>
                  </div>
                ) : filteredNotifications.length === 0 ? (
                  /* Empty state */
                  <div className="p-8 rounded-3xl bg-surface-container-low text-center border border-dashed border-surface-container-high my-4">
                    {data.total_count === 0 ? (
                      <>
                        <span className="text-4xl block mb-2">🎉</span>
                        <h3 className="text-sm font-bold text-primary">No Active Alerts</h3>
                        <p className="text-xs text-on-surface-variant mt-1 max-w-xs mx-auto leading-relaxed">
                          All pantry items are fresh and within safe shelf-life windows. No immediate food waste risk detected!
                        </p>
                        <button
                          type="button"
                          onClick={() => handleActionClick('/history')}
                          className="mt-4 px-4 py-2 rounded-full bg-primary text-white text-xs font-bold cursor-pointer"
                        >
                          View Pantry Log
                        </button>
                      </>
                    ) : (
                      <>
                        <span className="text-3xl block mb-2">✅</span>
                        <h3 className="text-sm font-bold text-primary">No alerts in this view</h3>
                        <p className="text-xs text-on-surface-variant mt-1">
                          Try selecting another filter above to review active pantry notices.
                        </p>
                        <button
                          type="button"
                          onClick={() => setActiveFilter('all')}
                          className="mt-3 px-3 py-1.5 rounded-full bg-surface-container-high text-primary text-xs font-bold cursor-pointer"
                        >
                          Show All
                        </button>
                      </>
                    )}
                  </div>
                ) : (
                  filteredNotifications.map((notif) => {
                    const cfg = TYPE_CONFIG[notif.type] || TYPE_CONFIG.expiring_soon;

                    return (
                      <div
                        key={notif.id}
                        className={`p-4 rounded-2xl border transition-all flex flex-col gap-2 relative ${
                          notif.isRead
                            ? 'bg-white/80 border-surface-container-high/80 opacity-80'
                            : 'bg-white border-secondary/40 shadow-xs ring-1 ring-secondary/20'
                        }`}
                      >
                        {/* Unread indicator dot */}
                        {!notif.isRead && (
                          <span className="absolute top-3.5 right-3.5 w-2 h-2 rounded-full bg-secondary animate-pulse" />
                        )}

                        {/* Header: Type Badge & Severity Icon */}
                        <div className="flex items-center gap-2 pr-4">
                          <span className={`material-symbols-outlined text-[18px] ${cfg.iconColor}`}>
                            {cfg.icon}
                          </span>
                          <span
                            className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider border ${cfg.badgeClass}`}
                          >
                            {cfg.label}
                          </span>
                          {notif.eatFirstPriority && notif.eatFirstPriority !== 'NORMAL' && notif.type !== 'high_priority' && (
                            <span className="px-1.5 py-0.5 rounded text-[9px] font-extrabold uppercase bg-amber-100 text-amber-900 border border-amber-200">
                              {notif.eatFirstPriority}
                            </span>
                          )}
                        </div>

                        {/* Body: Food Image + Title & Message */}
                        <div className="flex items-start gap-3 mt-1">
                          {notif.imageSrc && (
                            <div className="w-12 h-12 rounded-xl overflow-hidden shrink-0 border border-surface-container-high">
                              <img
                                src={notif.imageSrc}
                                alt={notif.foodName}
                                className="w-full h-full object-cover"
                              />
                            </div>
                          )}
                          <div className="flex-1 min-w-0">
                            <h4 className="text-xs font-bold text-primary truncate leading-tight">
                              {notif.title}
                            </h4>
                            <p className="text-[11px] text-on-surface-variant font-medium mt-0.5 leading-snug">
                              {notif.message}
                            </p>
                            {notif.storageEnvironment && (
                              <span className="inline-block mt-1 text-[10px] text-outline font-medium">
                                📍 {notif.storageEnvironment}
                              </span>
                            )}
                          </div>
                        </div>

                        {/* Footer Actions: Find Recipes, View in Pantry, Mark Read */}
                        <div className="pt-2 mt-1 border-t border-surface-container-low flex items-center justify-between text-xs">
                          <div className="flex items-center gap-2">
                            <button
                              type="button"
                              onClick={() => handleActionClick('/recipes')}
                              className="text-[11px] font-bold text-secondary hover:text-primary transition-colors flex items-center gap-1 cursor-pointer"
                            >
                              <span className="material-symbols-outlined text-[13px]">restaurant_menu</span>
                              <span>Recipes</span>
                            </button>
                            <button
                              type="button"
                              onClick={() => handleActionClick('/history')}
                              className="text-[11px] font-bold text-on-surface-variant hover:text-primary transition-colors flex items-center gap-1 cursor-pointer"
                            >
                              <span className="material-symbols-outlined text-[13px]">inventory_2</span>
                              <span>Pantry</span>
                            </button>
                          </div>

                          <div>
                            {notif.isRead ? (
                              <button
                                type="button"
                                onClick={(e) => handleMarkAsUnread(notif.id, e)}
                                className="text-[10px] text-outline hover:text-on-surface transition-colors cursor-pointer"
                              >
                                Mark unread
                              </button>
                            ) : (
                              <button
                                type="button"
                                onClick={(e) => handleMarkAsRead(notif.id, e)}
                                className="text-[10px] font-bold text-primary hover:text-secondary transition-colors cursor-pointer"
                              >
                                Mark read
                              </button>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>

              {/* Bottom Footer */}
              <div className="p-4 border-t border-surface-container-low bg-surface-container-lowest flex items-center justify-between text-xs text-on-surface-variant">
                <button
                  type="button"
                  onClick={() => handleActionClick('/alerts')}
                  className="text-xs font-bold text-secondary hover:text-primary transition-colors flex items-center gap-1 cursor-pointer"
                >
                  <span>Open Full Alerts Page</span>
                  <span className="material-symbols-outlined text-[14px]">arrow_forward</span>
                </button>
                <button
                  type="button"
                  onClick={fetchNotifications}
                  className="flex items-center gap-1 text-[11px] font-bold text-primary hover:text-secondary transition-colors cursor-pointer"
                >
                  <span className="material-symbols-outlined text-[14px]">refresh</span>
                  <span>Refresh Alerts</span>
                </button>
              </div>
            </div>
          </div>,
          document.body
        )}
    </>
  );
}

export default NotificationCenter;

