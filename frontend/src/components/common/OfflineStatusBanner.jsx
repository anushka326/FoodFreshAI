import React, { useState, useEffect } from 'react';
import { offlineSyncService } from '../../services/offlineSyncService.js';

export function OfflineStatusBanner() {
  const [networkState, setNetworkState] = useState({
    isOnline: typeof navigator !== 'undefined' ? navigator.onLine : true,
    isSyncing: false,
    pendingCount: 0,
  });
  const [showSyncedNotice, setShowSyncedNotice] = useState(false);

  useEffect(() => {
    const unsubscribe = offlineSyncService.subscribe((state) => {
      setNetworkState(state);
      if (state.event === 'synced' && state.syncedCount > 0) {
        setShowSyncedNotice(true);
        const timer = setTimeout(() => setShowSyncedNotice(false), 4000);
        return () => clearTimeout(timer);
      }
    });

    return unsubscribe;
  }, []);

  const { isOnline, isSyncing, pendingCount } = networkState;

  // If online, not syncing, and no recent sync toast, don't show anything
  if (isOnline && !isSyncing && !showSyncedNotice) {
    return null;
  }

  return (
    <aside
      aria-label="Network status notification"
      className="fixed bottom-4 left-4 right-4 sm:left-auto sm:right-6 sm:max-w-md z-50 animate-in fade-in slide-in-from-bottom duration-300 pointer-events-auto"
    >
      {/* 1. Offline Banner */}
      {!isOnline && (
        <div className="p-3.5 sm:p-4 rounded-2xl bg-surface-container-lowest/95 backdrop-blur-md border border-amber-300 shadow-xl flex items-center justify-between gap-3 text-xs sm:text-sm">
          <div className="flex items-center gap-3 text-amber-900">
            <div className="w-8 h-8 rounded-xl bg-amber-100 flex items-center justify-center shrink-0 text-amber-700">
              <span className="material-symbols-outlined text-[20px]">cloud_off</span>
            </div>
            <div>
              <div className="font-extrabold flex items-center gap-2">
                <span>Offline Mode Active</span>
                {pendingCount > 0 && (
                  <span className="px-2 py-0.5 rounded-full bg-amber-200 text-amber-900 text-[10px] font-bold">
                    {pendingCount} queued
                  </span>
                )}
              </div>
              <p className="text-[11px] text-amber-800/80 leading-snug mt-0.5">
                Viewing cached views. Pantry actions will automatically sync when connection returns.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* 2. Reconnecting / Syncing Banner */}
      {isOnline && isSyncing && (
        <div className="p-3.5 sm:p-4 rounded-2xl bg-surface-container-lowest/95 backdrop-blur-md border border-secondary shadow-xl flex items-center gap-3 text-xs sm:text-sm">
          <div className="w-8 h-8 rounded-xl bg-secondary-container flex items-center justify-center shrink-0 text-secondary">
            <span className="material-symbols-outlined text-[20px] animate-spin">sync</span>
          </div>
          <div>
            <span className="font-extrabold text-primary block">Reconnecting & Syncing</span>
            <p className="text-[11px] text-on-surface-variant leading-snug">
              Syncing pending pantry records with FoodFresh AI servers...
            </p>
          </div>
        </div>
      )}

      {/* 3. Reconnected & Sync Complete Notice */}
      {isOnline && !isSyncing && showSyncedNotice && (
        <div className="p-3.5 sm:p-4 rounded-2xl bg-surface-container-lowest/95 backdrop-blur-md border border-emerald-400 shadow-xl flex items-center justify-between gap-3 text-xs sm:text-sm">
          <div className="flex items-center gap-3 text-emerald-900">
            <div className="w-8 h-8 rounded-xl bg-emerald-100 flex items-center justify-center shrink-0 text-emerald-700">
              <span className="material-symbols-outlined text-[20px]">cloud_done</span>
            </div>
            <div>
              <span className="font-extrabold block">All Synced & Back Online</span>
              <p className="text-[11px] text-emerald-800/80 leading-snug">
                Your pending changes have been recorded on the server.
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={() => setShowSyncedNotice(false)}
            className="p-1 rounded-lg text-emerald-700 hover:bg-emerald-100 cursor-pointer"
            aria-label="Dismiss sync notification"
          >
            <span className="material-symbols-outlined text-[16px]">close</span>
          </button>
        </div>
      )}
    </aside>
  );
}

export default OfflineStatusBanner;

