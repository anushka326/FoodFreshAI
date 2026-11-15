import React, { useState, useEffect, useCallback } from 'react';
import { notificationService } from '../../services/notificationService.js';

const TYPE_CONFIG = {
  expired: {
    label: 'Expired',
    badgeClass: 'bg-red-100 text-red-800 border-red-200',
    icon: 'dangerous',
    iconColor: 'text-red-600',
    borderClass: 'border-red-200 hover:border-red-300',
  },
  expiring_today: {
    label: 'Expires Today 🔥',
    badgeClass: 'bg-rose-100 text-rose-800 border-rose-200 font-extrabold',
    icon: 'alarm',
    iconColor: 'text-rose-600',
    borderClass: 'border-rose-200 hover:border-rose-300',
  },
  expiring_soon: {
    label: 'Expiring Soon ⏳',
    badgeClass: 'bg-amber-100 text-amber-800 border-amber-200',
    icon: 'hourglass_bottom',
    iconColor: 'text-amber-600',
    borderClass: 'border-amber-200 hover:border-amber-300',
  },
  high_priority: {
    label: 'Eat First ⭐',
    badgeClass: 'bg-orange-100 text-orange-800 border-orange-200',
    icon: 'priority_high',
    iconColor: 'text-orange-600',
    borderClass: 'border-orange-200 hover:border-orange-300',
  },
};

export function NotificationsPage({ navigate }) {
  const [data, setData] = useState({
    notifications: [],
    unread_count: 0,
    total_count: 0,
    summary: {},
  });
  const [activeFilter, setActiveFilter] = useState('all'); // 'all' | 'unread' | 'critical' | 'expiring_soon'
  const [loading, setLoading] = useState(false);

  const fetchNotifications = useCallback(async () => {
    setLoading(true);
    try {
      const res = await notificationService.getNotifications();
      setData(res);
    } catch (e) {
      console.warn('Failed to load notifications page data:', e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 30000);
    return () => clearInterval(interval);
  }, [fetchNotifications]);

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

  // Filter items
  const filteredNotifications = data.notifications.filter((n) => {
    if (activeFilter === 'unread') return !n.isRead;
    if (activeFilter === 'critical') return n.type === 'expired' || n.type === 'expiring_today';
    if (activeFilter === 'expiring_soon') return n.type === 'expiring_soon';
    return true;
  });

  const criticalCount = (data.summary.expired || 0) + (data.summary.expiring_today || 0);

  return (
    <div className="space-y-6 pb-16 font-sans">
      {/* ── HEADER ── */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-secondary text-[26px]">
              notifications_active
            </span>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-primary tracking-tight">
              Expiry Alerts & Smart Notifications
            </h1>
          </div>
          <p className="text-xs sm:text-sm text-on-surface-variant mt-1 max-w-2xl leading-relaxed">
            Real-time proactive food waste alerts and shelf-life countdowns evaluated continuously from your kitchen inventory.
          </p>
        </div>

        <div className="flex items-center gap-2.5 shrink-0">
          <button
            type="button"
            onClick={fetchNotifications}
            disabled={loading}
            className="px-4 py-2 rounded-full bg-white border border-surface-container-high hover:bg-surface-container text-primary font-bold text-xs shadow-2xs flex items-center gap-1.5 transition-all cursor-pointer"
          >
            <span className={`material-symbols-outlined text-[16px] ${loading ? 'animate-spin' : ''}`}>
              refresh
            </span>
            <span>Refresh</span>
          </button>

          {data.unread_count > 0 && (
            <button
              type="button"
              onClick={handleMarkAllRead}
              className="px-4 py-2 rounded-full bg-secondary text-white hover:bg-secondary/90 font-bold text-xs shadow-sm flex items-center gap-1.5 transition-all cursor-pointer"
            >
              <span className="material-symbols-outlined text-[16px]">done_all</span>
              <span>Mark All Read</span>
            </button>
          )}
        </div>
      </div>

      {/* ── METRIC TILES ── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        <div className="p-4 sm:p-5 rounded-3xl bg-white border border-surface-container-high/80 shadow-2xs">
          <div className="flex items-center justify-between text-on-surface-variant mb-1">
            <span className="text-xs font-bold uppercase tracking-wider">Total Alerts</span>
            <span className="material-symbols-outlined text-[20px] text-primary">notifications</span>
          </div>
          <span className="text-2xl sm:text-3xl font-extrabold text-primary block mt-1">
            {data.total_count}
          </span>
          <span className="text-[11px] text-outline mt-1 block">Monitored kitchen items</span>
        </div>

        <div className="p-4 sm:p-5 rounded-3xl bg-white border border-rose-200 shadow-2xs">
          <div className="flex items-center justify-between text-rose-700 mb-1">
            <span className="text-xs font-bold uppercase tracking-wider">Critical / Expired</span>
            <span className="material-symbols-outlined text-[20px] text-rose-600">dangerous</span>
          </div>
          <span className="text-2xl sm:text-3xl font-extrabold text-rose-700 block mt-1">
            {criticalCount}
          </span>
          <span className="text-[11px] text-rose-600/80 mt-1 block">Requires prompt action</span>
        </div>

        <div className="p-4 sm:p-5 rounded-3xl bg-white border border-amber-200 shadow-2xs">
          <div className="flex items-center justify-between text-amber-700 mb-1">
            <span className="text-xs font-bold uppercase tracking-wider">Expiring Soon</span>
            <span className="material-symbols-outlined text-[20px] text-amber-600">hourglass_bottom</span>
          </div>
          <span className="text-2xl sm:text-3xl font-extrabold text-amber-700 block mt-1">
            {data.summary.expiring_soon || 0}
          </span>
          <span className="text-[11px] text-amber-600/80 mt-1 block">Next 48–72 hours</span>
        </div>

        <div className="p-4 sm:p-5 rounded-3xl bg-white border border-surface-container-high/80 shadow-2xs">
          <div className="flex items-center justify-between text-secondary mb-1">
            <span className="text-xs font-bold uppercase tracking-wider">Unread Notices</span>
            <span className="material-symbols-outlined text-[20px] text-secondary">mark_chat_unread</span>
          </div>
          <span className="text-2xl sm:text-3xl font-extrabold text-secondary block mt-1">
            {data.unread_count}
          </span>
          <span className="text-[11px] text-outline mt-1 block">Pending kitchen reviews</span>
        </div>
      </div>

      {/* ── FILTER CHIPS ── */}
      <div className="flex flex-wrap items-center gap-2 pt-2">
        {[
          { id: 'all', label: `All Alerts (${data.total_count})`, icon: 'list' },
          { id: 'unread', label: `Unread (${data.unread_count})`, icon: 'mark_chat_unread' },
          { id: 'critical', label: `Critical (${criticalCount})`, icon: 'alarm' },
          { id: 'expiring_soon', label: `Expiring Soon (${data.summary.expiring_soon || 0})`, icon: 'hourglass_bottom' },
        ].map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveFilter(tab.id)}
            className={`px-4 py-2 rounded-full text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer ${
              activeFilter === tab.id
                ? 'bg-primary text-white shadow-sm'
                : 'bg-white border border-surface-container-high text-on-surface-variant hover:bg-surface-container-low'
            }`}
          >
            <span className="material-symbols-outlined text-[16px]">{tab.icon}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* ── NOTIFICATIONS GRID ── */}
      {loading && data.notifications.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-24 space-y-3 text-on-surface-variant bg-white rounded-3xl border border-surface-container-high">
          <div className="w-10 h-10 border-3 border-primary border-t-transparent rounded-full animate-spin" />
          <span className="text-sm font-semibold">Scanning live pantry records and shelf-life metrics…</span>
        </div>
      ) : filteredNotifications.length === 0 ? (
        /* Empty State */
        <div className="p-12 rounded-3xl bg-white border border-dashed border-surface-container-high text-center">
          <span className="text-5xl block mb-3">🍃</span>
          <h3 className="text-base sm:text-lg font-bold text-primary">
            {data.total_count === 0 ? 'All Pantry Items Are Fresh!' : 'No Alerts in Selected Filter'}
          </h3>
          <p className="text-xs sm:text-sm text-on-surface-variant mt-1.5 max-w-md mx-auto leading-relaxed">
            {data.total_count === 0
              ? 'Your tracked pantry items are safely within their recommended freshness windows. No immediate food waste risk detected.'
              : 'Try selecting a different filter above to inspect all active notifications.'}
          </p>
          <div className="mt-6 flex flex-wrap justify-center gap-3">
            <button
              type="button"
              onClick={() => navigate('/analyze')}
              className="px-5 py-2.5 rounded-full bg-primary text-white text-xs font-bold shadow-sm hover:shadow transition-all cursor-pointer"
            >
              Scan & Inspect Food
            </button>
            <button
              type="button"
              onClick={() => navigate('/history')}
              className="px-5 py-2.5 rounded-full bg-surface-container-low hover:bg-surface-container text-primary text-xs font-bold transition-all cursor-pointer"
            >
              View Smart Pantry
            </button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredNotifications.map((notif) => {
            const cfg = TYPE_CONFIG[notif.type] || TYPE_CONFIG.expiring_soon;

            return (
              <div
                key={notif.id}
                className={`p-5 rounded-3xl border bg-white shadow-2xs hover:shadow-md transition-all flex flex-col justify-between relative ${
                  notif.isRead ? 'border-surface-container-high/80 opacity-90' : `${cfg.borderClass} ring-1 ring-secondary/20`
                }`}
              >
                {/* Top unread dot */}
                {!notif.isRead && (
                  <span className="absolute top-4 right-4 w-2.5 h-2.5 rounded-full bg-secondary animate-pulse" />
                )}

                <div>
                  {/* Category Badge & Priority Header */}
                  <div className="flex flex-wrap items-center gap-2 mb-3 pr-6">
                    <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-bold uppercase tracking-wider border ${cfg.badgeClass}`}>
                      {cfg.label}
                    </span>
                    {notif.eatFirstPriority && notif.eatFirstPriority !== 'NORMAL' && notif.type !== 'high_priority' && (
                      <span className="px-2 py-0.5 rounded text-[10px] font-extrabold uppercase bg-amber-100 text-amber-900 border border-amber-200">
                        {notif.eatFirstPriority}
                      </span>
                    )}
                  </div>

                  {/* Food visual and core info */}
                  <div className="flex items-start gap-3.5">
                    {notif.imageSrc && (
                      <div className="w-14 h-14 rounded-2xl overflow-hidden shrink-0 border border-surface-container-high bg-surface-container-low">
                        <img
                          src={notif.imageSrc}
                          alt={notif.foodName}
                          className="w-full h-full object-cover"
                        />
                      </div>
                    )}
                    <div className="flex-1 min-w-0">
                      <h3 className="text-sm font-bold text-primary truncate leading-tight">
                        {notif.title}
                      </h3>
                      <p className="text-xs text-on-surface-variant font-medium mt-1 leading-relaxed">
                        {notif.message}
                      </p>
                      {notif.storageEnvironment && (
                        <span className="inline-block mt-1.5 text-[11px] text-outline font-medium">
                          📍 {notif.storageEnvironment}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Bottom Actions */}
                <div className="pt-4 mt-4 border-t border-surface-container-low flex items-center justify-between gap-2">
                  <div className="flex items-center gap-1.5">
                    <button
                      type="button"
                      onClick={() => navigate('/recipes')}
                      className="px-3 py-1 rounded-full bg-secondary-container hover:bg-secondary text-on-secondary-container hover:text-white text-xs font-bold transition-all cursor-pointer flex items-center gap-1"
                    >
                      <span className="material-symbols-outlined text-[14px]">restaurant_menu</span>
                      <span>Recipes</span>
                    </button>

                    <button
                      type="button"
                      onClick={() => navigate('/history')}
                      className="px-3 py-1 rounded-full bg-surface-container-low hover:bg-surface-container text-primary text-xs font-bold transition-all cursor-pointer flex items-center gap-1"
                    >
                      <span className="material-symbols-outlined text-[14px]">inventory_2</span>
                      <span>Pantry</span>
                    </button>
                  </div>

                  <div>
                    {notif.isRead ? (
                      <button
                        type="button"
                        onClick={(e) => handleMarkAsUnread(notif.id, e)}
                        className="text-xs text-outline hover:text-on-surface transition-colors cursor-pointer"
                      >
                        Mark unread
                      </button>
                    ) : (
                      <button
                        type="button"
                        onClick={(e) => handleMarkAsRead(notif.id, e)}
                        className="text-xs font-bold text-primary hover:text-secondary transition-colors cursor-pointer"
                      >
                        Mark read
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default NotificationsPage;

