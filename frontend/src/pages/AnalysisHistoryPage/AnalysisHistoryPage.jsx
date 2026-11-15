import React, { useState } from 'react';
import { useFoodFresh } from '../../hooks/useFoodFresh.js';
import { MASCOT_ASSETS } from '../../assets/mascot/index.js';
import { freshoBuddyService } from '../../services/freshoBuddyService.js';
import { analyticsService } from '../../services/analyticsService.js';
import { Toast } from '../../components/common/Toast.jsx';

export function AnalysisHistoryPage({ navigate }) {
  const {
    history,
    archivedHistory,
    activityLogs,
    totalTracked,
    deleteHistoryItem,
    restoreHistoryItem,
    permanentlyDeleteHistoryItem,
    refresh,
  } = useFoodFresh();

  const [currentTab, setCurrentTab] = useState('active'); // 'active' | 'removed' | 'logs'
  const [searchTerm, setSearchTerm] = useState('');
  const [activeFilter, setActiveFilter] = useState('all'); // 'all' | 'fresh' | 'semi' | 'attention'
  const [removedFilter, setRemovedFilter] = useState('all'); // 'all' | 'consumed' | 'wasted' | 'removed'
  const [logFilter, setLogFilter] = useState('all'); // 'all' | 'added' | 'consumed' | 'wasted' | 'removed' | 'restored'

  const [selectedItem, setSelectedItem] = useState(null);
  const [outcomeModalItem, setOutcomeModalItem] = useState(null);
  const [outcomeAction, setOutcomeAction] = useState('consumed'); // 'consumed' | 'wasted' | 'removed'
  const [outcomeReason, setOutcomeReason] = useState('');
  const [isSubmittingOutcome, setIsSubmittingOutcome] = useState(false);

  const [toastMessage, setToastMessage] = useState('');
  const [showToast, setShowToast] = useState(false);

  const triggerToast = (msg) => {
    setToastMessage(msg);
    setShowToast(true);
    setTimeout(() => setShowToast(false), 3000);
  };

  const needingCookingSoon = history.filter(
    (item) => item.statusCategory === 'attention' || item.statusCategory === 'semi'
  ).length;

  const pantryLongevityIndex = history.length > 0
    ? Math.round(history.reduce((sum, item) => sum + (Number(item.qualityScore) || 80), 0) / history.length)
    : 0;

  // Active items filter
  const filteredActiveItems = history.filter((item) => {
    const term = searchTerm.toLowerCase();
    const matchesSearch =
      (item.foodName || '').toLowerCase().includes(term) ||
      (item.cultivar || '').toLowerCase().includes(term);
    const matchesFilter = activeFilter === 'all' || item.statusCategory === activeFilter;
    return matchesSearch && matchesFilter;
  });

  // Removed items filter
  const filteredRemovedItems = archivedHistory.filter((item) => {
    const term = searchTerm.toLowerCase();
    const matchesSearch =
      (item.foodName || '').toLowerCase().includes(term) ||
      (item.cultivar || '').toLowerCase().includes(term) ||
      (item.removalReason || '').toLowerCase().includes(term);
    const action = (item.removalAction || 'removed').toLowerCase();
    const matchesFilter = removedFilter === 'all' || action === removedFilter;
    return matchesSearch && matchesFilter;
  });

  // Activity logs filter
  const filteredLogs = activityLogs.filter((log) => {
    const term = searchTerm.toLowerCase();
    const matchesSearch =
      (log.foodName || '').toLowerCase().includes(term) ||
      (log.cultivar || '').toLowerCase().includes(term) ||
      (log.details || '').toLowerCase().includes(term) ||
      (log.actionType || '').toLowerCase().includes(term);
    const matchesFilter = logFilter === 'all' || (log.actionType || '').toLowerCase() === logFilter;
    return matchesSearch && matchesFilter;
  });

  const handleOpenOutcomeModal = (item) => {
    setOutcomeModalItem(item);
    setOutcomeAction('consumed');
    setOutcomeReason('');
  };

  const handleConfirmOutcome = async () => {
    if (!outcomeModalItem) return;
    setIsSubmittingOutcome(true);
    try {
      if (outcomeAction === 'consumed' || outcomeAction === 'wasted') {
        await analyticsService.recordAction({
          foodName: outcomeModalItem.foodName,
          cultivar: outcomeModalItem.cultivar || '',
          action: outcomeAction,
          pantryItemId: outcomeModalItem.id,
          reason: outcomeReason || undefined,
        });
      } else {
        await deleteHistoryItem(outcomeModalItem.id, {
          action: 'removed',
          reason: outcomeReason || 'Removed from pantry storage by user',
        });
      }

      if (selectedItem?.id === outcomeModalItem.id) {
        setSelectedItem(null);
      }

      triggerToast(
        outcomeAction === 'consumed'
          ? `🎉 Saved ${outcomeModalItem.foodName}! Recorded in Impact Analytics & History.`
          : outcomeAction === 'wasted'
          ? `Logged ${outcomeModalItem.foodName} as wasted in Impact Analytics & History.`
          : `Archived ${outcomeModalItem.foodName} into Removed History logs.`
      );
      setOutcomeModalItem(null);
      await refresh();
    } catch (err) {
      console.error('Failed to log outcome:', err);
      triggerToast('Could not record action. Please try again.');
    } finally {
      setIsSubmittingOutcome(false);
    }
  };

  const handleDirectDelete = async (item) => {
    try {
      await deleteHistoryItem(item.id, {
        action: 'removed',
        reason: 'Archived from pantry history',
      });
      if (selectedItem?.id === item.id) {
        setSelectedItem(null);
      }
      triggerToast(`Moved ${item.foodName} to Removed Products Log.`);
      await refresh();
    } catch (err) {
      triggerToast('Could not remove item.');
    }
  };

  const handleRestore = async (item) => {
    try {
      await restoreHistoryItem(item.id);
      if (selectedItem?.id === item.id) {
        setSelectedItem(null);
      }
      triggerToast(`Restored ${item.foodName} back into active pantry!`);
      await refresh();
    } catch (err) {
      triggerToast('Could not restore item.');
    }
  };

  const handlePermanentDelete = async (item) => {
    if (!window.confirm(`Permanently purge ${item.foodName} from database? This cannot be undone.`)) {
      return;
    }
    try {
      await permanentlyDeleteHistoryItem(item.id);
      if (selectedItem?.id === item.id) {
        setSelectedItem(null);
      }
      triggerToast(`Permanently deleted ${item.foodName}.`);
      await refresh();
    } catch (err) {
      triggerToast('Could not delete item.');
    }
  };

  const formatIsoDate = (isoStr) => {
    if (!isoStr) return '—';
    try {
      const d = new Date(isoStr);
      return d.toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return isoStr;
    }
  };

  return (
    <div className="space-y-6 pb-12 font-sans relative">
      <Toast message={toastMessage} visible={showToast} />

      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-2xl">📋</span>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-primary tracking-tight">
              Pantry Produce & Activity History
            </h1>
          </div>
          <p className="text-xs sm:text-sm text-on-surface-variant mt-0.5">
            Active pantry inventory, complete logs of all removed foods, and an immutable audit trail of every project activity.
          </p>
        </div>

        <div className="flex items-center gap-2 self-start sm:self-auto">
          <button
            type="button"
            onClick={() => navigate('/analytics')}
            className="px-4 py-2.5 rounded-full bg-surface-container hover:bg-surface-container-high text-primary text-xs font-bold shadow-2xs transition-all flex items-center gap-1.5 cursor-pointer"
          >
            <span className="material-symbols-outlined text-[16px] text-secondary">insights</span>
            <span>Impact Analytics</span>
          </button>
          <button
            type="button"
            onClick={() => navigate('/analyze')}
            className="px-5 py-2.5 rounded-full bg-primary hover:bg-primary-container text-white text-xs font-bold shadow-sm transition-all flex items-center gap-1.5 cursor-pointer"
          >
            <span className="material-symbols-outlined text-[16px]">add</span>
            <span>New Analysis</span>
          </button>
        </div>
      </div>

      {/* Offline Mode Advisory */}
      {(!navigator.onLine || history.some((i) => i._isOfflineCached)) && (
        <div className="p-3.5 rounded-2xl bg-amber-50 border border-amber-200 flex items-center justify-between gap-3 text-xs text-amber-900">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-[18px] text-amber-700 shrink-0">cloud_off</span>
            <span>
              <strong>Offline Mode:</strong> Showing cached pantry records from your last session. Real-time expiry timers and live sync will resume once reconnected.
            </span>
          </div>
          <span className="px-2 py-0.5 rounded-full bg-amber-200/80 font-bold text-[10px] uppercase shrink-0">Cached Data</span>
        </div>
      )}

      {/* Metric Overview Strip */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <div className="p-4 rounded-2xl bg-white border border-surface-container-high/80 shadow-2xs">
          <span className="text-xs font-semibold text-on-surface-variant block">Total Tracked All-Time</span>
          <span className="text-2xl font-extrabold text-primary block mt-1">{totalTracked} produce</span>
        </div>
        <div className="p-4 rounded-2xl bg-white border border-surface-container-high/80 shadow-2xs">
          <span className="text-xs font-semibold text-on-surface-variant block">Active in Pantry</span>
          <span className="text-2xl font-extrabold text-emerald-700 block mt-1">{history.length} items</span>
        </div>
        <div className="p-4 rounded-2xl bg-white border border-surface-container-high/80 shadow-2xs">
          <span className="text-xs font-semibold text-on-surface-variant block">Removed & History Logs</span>
          <span className="text-2xl font-extrabold text-secondary block mt-1">{archivedHistory.length} archived</span>
        </div>
        <div className="p-4 rounded-2xl bg-white border border-surface-container-high/80 shadow-2xs">
          <span className="text-xs font-semibold text-on-surface-variant block">Project Activity Events</span>
          <span className="text-2xl font-extrabold text-primary block mt-1">{activityLogs.length} events</span>
        </div>
      </div>

      {/* ── Main Tab Navigation ── */}
      <div className="flex border-b border-surface-container-high gap-2 sm:gap-6 text-xs sm:text-sm font-bold">
        <button
          type="button"
          onClick={() => {
            setCurrentTab('active');
            setSearchTerm('');
          }}
          className={`pb-3 px-1.5 sm:px-2 flex items-center gap-2 border-b-2 transition-all cursor-pointer ${
            currentTab === 'active'
              ? 'border-primary text-primary font-black'
              : 'border-transparent text-on-surface-variant hover:text-primary'
          }`}
        >
          <span>Active Pantry Produce</span>
          <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[11px] font-extrabold">
            {history.length}
          </span>
        </button>

        <button
          type="button"
          onClick={() => {
            setCurrentTab('removed');
            setSearchTerm('');
          }}
          className={`pb-3 px-1.5 sm:px-2 flex items-center gap-2 border-b-2 transition-all cursor-pointer ${
            currentTab === 'removed'
              ? 'border-primary text-primary font-black'
              : 'border-transparent text-on-surface-variant hover:text-primary'
          }`}
        >
          <span>Removed Products Log</span>
          <span className="px-2 py-0.5 rounded-full bg-surface-container text-primary text-[11px] font-extrabold">
            {archivedHistory.length}
          </span>
        </button>

        <button
          type="button"
          onClick={() => {
            setCurrentTab('logs');
            setSearchTerm('');
          }}
          className={`pb-3 px-1.5 sm:px-2 flex items-center gap-2 border-b-2 transition-all cursor-pointer ${
            currentTab === 'logs'
              ? 'border-primary text-primary font-black'
              : 'border-transparent text-on-surface-variant hover:text-primary'
          }`}
        >
          <span>Project Activity Logs</span>
          <span className="px-2 py-0.5 rounded-full bg-secondary-container text-on-secondary-container text-[11px] font-extrabold">
            {activityLogs.length}
          </span>
        </button>
      </div>

      {/* Search & Filter Toolbar */}
      <div className="p-4 rounded-3xl bg-white border border-surface-container-high/70 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-4">
        {/* Search Field */}
        <div className="relative w-full sm:w-80">
          <span className="material-symbols-outlined absolute left-3.5 top-2.5 text-on-surface-variant text-[18px]">
            search
          </span>
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder={
              currentTab === 'active'
                ? 'Filter active produce by name...'
                : currentTab === 'removed'
                ? 'Search removed foods, reasons...'
                : 'Filter project activity events...'
            }
            className="w-full pl-10 pr-4 py-2 bg-surface-container-low/60 border border-surface-container-high rounded-full text-xs text-on-surface placeholder:text-outline focus:outline-none focus:ring-2 focus:ring-secondary/40"
          />
        </div>

        {/* Filter Chips depending on tab */}
        {currentTab === 'active' && (
          <div className="flex flex-wrap items-center gap-1.5 w-full sm:w-auto">
            <button
              type="button"
              onClick={() => setActiveFilter('all')}
              className={`px-3 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer ${
                activeFilter === 'all'
                  ? 'bg-primary text-white'
                  : 'bg-surface-container-low text-on-surface-variant hover:bg-surface-container'
              }`}
            >
              All ({history.length})
            </button>
            <button
              type="button"
              onClick={() => setActiveFilter('fresh')}
              className={`px-3 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer ${
                activeFilter === 'fresh'
                  ? 'bg-secondary text-white'
                  : 'bg-surface-container-low text-secondary hover:bg-surface-container'
              }`}
            >
              Fresh
            </button>
            <button
              type="button"
              onClick={() => setActiveFilter('semi')}
              className={`px-3 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer ${
                activeFilter === 'semi'
                  ? 'bg-tertiary-container text-white'
                  : 'bg-surface-container-low text-tertiary-container hover:bg-surface-container'
              }`}
            >
              Semi-Fresh
            </button>
            <button
              type="button"
              onClick={() => setActiveFilter('attention')}
              className={`px-3 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer ${
                activeFilter === 'attention'
                  ? 'bg-error text-white'
                  : 'bg-surface-container-low text-error hover:bg-surface-container'
              }`}
            >
              Needs Attention ({needingCookingSoon})
            </button>
          </div>
        )}

        {currentTab === 'removed' && (
          <div className="flex flex-wrap items-center gap-1.5 w-full sm:w-auto">
            <button
              type="button"
              onClick={() => setRemovedFilter('all')}
              className={`px-3 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer ${
                removedFilter === 'all'
                  ? 'bg-primary text-white'
                  : 'bg-surface-container-low text-on-surface-variant hover:bg-surface-container'
              }`}
            >
              All Removed ({archivedHistory.length})
            </button>
            <button
              type="button"
              onClick={() => setRemovedFilter('consumed')}
              className={`px-3 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer ${
                removedFilter === 'consumed'
                  ? 'bg-emerald-700 text-white'
                  : 'bg-emerald-50 text-emerald-800 hover:bg-emerald-100'
              }`}
            >
              Consumed 🎉 ({archivedHistory.filter((i) => i.removalAction === 'consumed').length})
            </button>
            <button
              type="button"
              onClick={() => setRemovedFilter('wasted')}
              className={`px-3 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer ${
                removedFilter === 'wasted'
                  ? 'bg-red-700 text-white'
                  : 'bg-red-50 text-red-800 hover:bg-red-100'
              }`}
            >
              Discarded 🗑️ ({archivedHistory.filter((i) => i.removalAction === 'wasted').length})
            </button>
            <button
              type="button"
              onClick={() => setRemovedFilter('removed')}
              className={`px-3 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer ${
                removedFilter === 'removed'
                  ? 'bg-slate-700 text-white'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              Archived 📦 ({archivedHistory.filter((i) => !i.removalAction || i.removalAction === 'removed').length})
            </button>
          </div>
        )}

        {currentTab === 'logs' && (
          <div className="flex flex-wrap items-center gap-1.5 w-full sm:w-auto">
            <button
              type="button"
              onClick={() => setLogFilter('all')}
              className={`px-3 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer ${
                logFilter === 'all'
                  ? 'bg-primary text-white'
                  : 'bg-surface-container-low text-on-surface-variant hover:bg-surface-container'
              }`}
            >
              All Events ({activityLogs.length})
            </button>
            <button
              type="button"
              onClick={() => setLogFilter('added')}
              className={`px-3 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer ${
                logFilter === 'added'
                  ? 'bg-blue-700 text-white'
                  : 'bg-blue-50 text-blue-800 hover:bg-blue-100'
              }`}
            >
              Added 📥
            </button>
            <button
              type="button"
              onClick={() => setLogFilter('consumed')}
              className={`px-3 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer ${
                logFilter === 'consumed'
                  ? 'bg-emerald-700 text-white'
                  : 'bg-emerald-50 text-emerald-800 hover:bg-emerald-100'
              }`}
            >
              Consumed 🎉
            </button>
            <button
              type="button"
              onClick={() => setLogFilter('wasted')}
              className={`px-3 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer ${
                logFilter === 'wasted'
                  ? 'bg-red-700 text-white'
                  : 'bg-red-50 text-red-800 hover:bg-red-100'
              }`}
            >
              Wasted 🗑️
            </button>
            <button
              type="button"
              onClick={() => setLogFilter('removed')}
              className={`px-3 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer ${
                logFilter === 'removed'
                  ? 'bg-slate-700 text-white'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              Removed 📦
            </button>
          </div>
        )}
      </div>

      {/* ── TAB 1: ACTIVE PANTRY PRODUCE ── */}
      {currentTab === 'active' && (
        <>
          {filteredActiveItems.length === 0 ? (
            <div className="p-12 rounded-3xl bg-surface-container-low text-center border border-dashed border-surface-container-high">
              {history.length === 0 ? (
                <>
                  <span className="text-3xl block mb-2">🥗</span>
                  <h3 className="text-base font-bold text-primary">Your active pantry is empty</h3>
                  <p className="text-xs text-on-surface-variant mt-1 max-w-md mx-auto">
                    Analyze and save a food product to start tracking estimated quality and countdown timers.
                  </p>
                  <div className="mt-4 flex flex-wrap justify-center gap-3">
                    <button
                      type="button"
                      onClick={() => navigate('/analyze')}
                      className="px-5 py-2.5 rounded-full bg-primary text-white text-xs font-bold cursor-pointer"
                    >
                      Analyze Food
                    </button>
                    {archivedHistory.length > 0 && (
                      <button
                        type="button"
                        onClick={() => setCurrentTab('removed')}
                        className="px-5 py-2.5 rounded-full bg-white border border-surface-container-high text-primary text-xs font-bold cursor-pointer"
                      >
                        View Removed History ({archivedHistory.length})
                      </button>
                    )}
                  </div>
                </>
              ) : (
                <>
                  <span className="text-3xl block mb-2">🔍</span>
                  <h3 className="text-base font-bold text-primary">No matching active produce found</h3>
                  <p className="text-xs text-on-surface-variant mt-1">
                    Try adjusting your search query or filter tags above.
                  </p>
                  <button
                    type="button"
                    onClick={() => {
                      setSearchTerm('');
                      setActiveFilter('all');
                    }}
                    className="mt-4 px-4 py-2 rounded-full bg-primary text-white text-xs font-bold cursor-pointer"
                  >
                    Clear Filters
                  </button>
                </>
              )}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredActiveItems.map((item) => (
                <div
                  key={item.id}
                  className="p-5 rounded-3xl bg-white border border-surface-container-high/70 shadow-2xs hover:shadow-md transition-all flex flex-col justify-between"
                >
                  <div>
                    {/* Photo & Quality Badge */}
                    <div className="relative w-full aspect-video rounded-2xl overflow-hidden mb-3.5 border border-surface-container-high">
                      <img
                        src={item.imageSrc}
                        alt={item.foodName}
                        className="w-full h-full object-cover"
                      />
                      <div className="absolute top-2.5 right-2.5 px-2.5 py-0.5 rounded-full bg-white/90 backdrop-blur-xs text-[10px] font-extrabold text-primary shadow-2xs">
                        Score: {item.qualityScore}%
                      </div>
                      <div className="absolute bottom-2.5 left-2.5 px-2.5 py-0.5 rounded-full bg-black/60 backdrop-blur-xs text-[10px] text-white font-medium">
                        {item.analyzedTime ? formatIsoDate(item.analyzedTime) : 'Freshly Analyzed'}
                      </div>
                    </div>

                    {/* Title, Priority & Status */}
                    <div className="flex items-center justify-between mb-1 gap-2">
                      <h3 className="font-bold text-sm text-primary truncate">{item.foodName}</h3>
                      <div className="flex items-center gap-1.5 shrink-0">
                        {item.eatFirstPriority && item.eatFirstPriority !== 'NORMAL' && (
                          <span className={`px-2 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider ${
                            item.eatFirstPriority === 'VERY_HIGH'
                              ? 'bg-red-100 text-red-700 border border-red-200'
                              : item.eatFirstPriority === 'HIGH'
                              ? 'bg-amber-100 text-amber-800 border border-amber-200'
                              : item.eatFirstPriority === 'MEDIUM'
                              ? 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                              : 'bg-slate-100 text-slate-700'
                          }`}>
                            {item.eatFirstPriority.replace('_', ' ')}
                          </span>
                        )}
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                          item.statusCategory === 'fresh'
                            ? 'bg-secondary-container text-on-secondary-container'
                            : item.statusCategory === 'semi'
                            ? 'bg-tertiary-fixed text-on-tertiary-fixed'
                            : 'bg-error-container text-on-error-container'
                        }`}>
                          {item.status}
                        </span>
                      </div>
                    </div>

                    <div className="flex items-center justify-between gap-1 text-[11px] text-on-surface-variant font-medium mb-3">
                      <span className="truncate">{item.cultivar}</span>
                      {item.itemType === 'packaged' && (
                        <span className="px-1.5 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200 text-[9px] font-bold shrink-0">
                          📦 Packaged
                        </span>
                      )}
                    </div>

                    <p className="text-xs text-on-surface-variant line-clamp-2 leading-relaxed mb-4">
                      {item.guidance}
                    </p>
                  </div>

                  {/* Card Footer Actions */}
                  <div className="pt-3 border-t border-surface-container-low flex items-center justify-between">
                    <div>
                      <span className="text-xs font-bold text-primary block">
                        ⏳ {item.qualityPeriod || (item.remainingDays != null ? `${item.remainingDays} days remaining` : 'Pending estimate')}
                      </span>
                      {item.expiryDate && (
                        <span className="text-[10px] text-secondary font-bold block">
                          📅 Expiry: {item.expiryDate}
                        </span>
                      )}
                      {item.storageEnvironment && (
                        <span className="text-[10px] text-on-surface-variant font-medium block">
                          📍 {item.storageEnvironment}
                        </span>
                      )}
                    </div>

                    <div className="flex items-center gap-1.5">
                      <button
                        type="button"
                        onClick={() => {
                          freshoBuddyService.setFoodContext({
                            foodName: item.foodName,
                            cultivar: item.cultivar,
                            status: item.status,
                            qualityScore: item.qualityScore,
                            qualityPeriod: item.qualityPeriod,
                            storageEnvironment: item.storageEnvironment,
                            guidance: item.guidance,
                            imageSrc: item.imageSrc,
                            analyzedAt: item.analyzedTime,
                          });
                          navigate('/fresho-buddy');
                        }}
                        className="p-1.5 text-on-surface-variant hover:text-primary rounded-full hover:bg-surface-container transition-colors cursor-pointer"
                        title={`Ask FreshoBuddy about ${item.foodName}`}
                        aria-label={`Ask FreshoBuddy about ${item.foodName}`}
                      >
                        <img src={MASCOT_ASSETS.freshoBuddyUrl} alt="Buddy" className="w-4 h-4 object-contain" />
                      </button>
                      <button
                        type="button"
                        onClick={() => setSelectedItem(item)}
                        className="px-3 py-1.5 rounded-full bg-surface-container-low hover:bg-surface-container text-primary text-xs font-bold transition-colors cursor-pointer"
                      >
                        Inspect
                      </button>
                      <button
                        type="button"
                        onClick={() => handleOpenOutcomeModal(item)}
                        className="p-1.5 text-on-surface-variant hover:text-secondary rounded-full hover:bg-surface-container transition-colors cursor-pointer"
                        title="Log food outcome or remove"
                      >
                        <span className="material-symbols-outlined text-[18px]">output</span>
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* ── TAB 2: REMOVED PRODUCTS LOG ── */}
      {currentTab === 'removed' && (
        <>
          {filteredRemovedItems.length === 0 ? (
            <div className="p-12 rounded-3xl bg-surface-container-low text-center border border-dashed border-surface-container-high">
              <span className="text-3xl block mb-2">📦</span>
              <h3 className="text-base font-bold text-primary">No removed products in log</h3>
              <p className="text-xs text-on-surface-variant mt-1 max-w-md mx-auto">
                Whenever you finish, discard, or remove a food item from your active pantry, it will be stored here permanently with its complete historical record.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredRemovedItems.map((item) => {
                const action = (item.removalAction || 'removed').toLowerCase();
                return (
                  <div
                    key={item.id}
                    className="p-5 rounded-3xl bg-white border border-surface-container-high/80 shadow-2xs hover:shadow-md transition-all flex flex-col justify-between"
                  >
                    <div>
                      {/* Photo & Outcome Badge */}
                      <div className="relative w-full aspect-video rounded-2xl overflow-hidden mb-3.5 border border-surface-container-high">
                        <img
                          src={item.imageSrc}
                          alt={item.foodName}
                          className="w-full h-full object-cover filter saturate-90"
                        />
                        <div className="absolute top-2.5 right-2.5 px-2.5 py-0.5 rounded-full text-[10px] font-extrabold shadow-2xs backdrop-blur-xs flex items-center gap-1 uppercase tracking-wider">
                          {action === 'consumed' ? (
                            <span className="bg-emerald-600 text-white px-2 py-0.5 rounded-full">
                              🎉 Consumed
                            </span>
                          ) : action === 'wasted' ? (
                            <span className="bg-red-600 text-white px-2 py-0.5 rounded-full">
                              🗑️ Discarded
                            </span>
                          ) : (
                            <span className="bg-slate-700 text-white px-2 py-0.5 rounded-full">
                              📦 Removed
                            </span>
                          )}
                        </div>
                        <div className="absolute bottom-2.5 left-2.5 px-2.5 py-0.5 rounded-full bg-black/60 backdrop-blur-xs text-[10px] text-white font-medium">
                          Initial Score: {item.qualityScore}%
                        </div>
                      </div>

                      {/* Title & Cultivar */}
                      <div className="flex items-center justify-between mb-1 gap-2">
                        <h3 className="font-bold text-sm text-primary truncate">{item.foodName}</h3>
                        <span className="text-[10px] text-on-surface-variant font-semibold">
                          {item.itemType === 'packaged' ? '📦 Packaged' : '🌱 Fresh'}
                        </span>
                      </div>
                      <p className="text-[11px] text-on-surface-variant font-medium truncate mb-2">
                        {item.cultivar}
                      </p>

                      {/* Removal Log Information */}
                      <div className="p-3 rounded-2xl bg-surface-container-low text-xs space-y-1 mb-3">
                        <div className="flex items-center justify-between text-[11px]">
                          <span className="text-on-surface-variant">Removed:</span>
                          <span className="font-bold text-primary">
                            {formatIsoDate(item.archivedAt || item.updatedAt || item.analyzedTime)}
                          </span>
                        </div>
                        {item.removalReason && (
                          <div className="text-[11px] text-on-surface-variant pt-1 border-t border-surface-container-high/60">
                            <span className="font-semibold text-primary">Note:</span> {item.removalReason}
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Footer Actions */}
                    <div className="pt-3 border-t border-surface-container-low flex items-center justify-between">
                      <button
                        type="button"
                        onClick={() => setSelectedItem(item)}
                        className="px-3 py-1.5 rounded-full bg-surface-container-low hover:bg-surface-container text-primary text-xs font-bold transition-colors cursor-pointer"
                      >
                        Inspect Record
                      </button>

                      <div className="flex items-center gap-2">
                        <button
                          type="button"
                          onClick={() => handleRestore(item)}
                          className="px-3 py-1.5 rounded-full bg-emerald-50 hover:bg-emerald-100 text-emerald-800 text-xs font-bold transition-colors flex items-center gap-1 cursor-pointer"
                          title="Restore product to active pantry"
                        >
                          <span className="material-symbols-outlined text-[15px]">settings_backup_restore</span>
                          <span>Restore</span>
                        </button>
                        <button
                          type="button"
                          onClick={() => handlePermanentDelete(item)}
                          className="p-1.5 text-on-surface-variant hover:text-red-700 rounded-full hover:bg-red-50 transition-colors"
                          title="Permanently delete log"
                        >
                          <span className="material-symbols-outlined text-[16px]">delete_forever</span>
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </>
      )}

      {/* ── TAB 3: PROJECT ACTIVITY LOGS ── */}
      {currentTab === 'logs' && (
        <div className="p-6 rounded-3xl bg-white border border-surface-container-high/80 shadow-2xs space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm sm:text-base font-extrabold text-primary">
                Activity Audit Trail
              </h3>
              <p className="text-xs text-on-surface-variant mt-0.5">
                Immutable, chronological activity history of every food item added, consumed, discarded, or removed.
              </p>
            </div>
            <span className="text-xs text-outline font-semibold">
              Showing {filteredLogs.length} events
            </span>
          </div>

          {filteredLogs.length === 0 ? (
            <div className="py-12 text-center text-xs text-on-surface-variant">
              No activity logs match the selected filter.
            </div>
          ) : (
            <div className="divide-y divide-surface-container-low">
              {filteredLogs.map((log) => {
                const act = (log.actionType || 'added').toLowerCase();
                const icon =
                  act === 'consumed'
                    ? 'restaurant'
                    : act === 'wasted'
                    ? 'delete'
                    : act === 'added'
                    ? 'add_circle'
                    : act === 'restored'
                    ? 'settings_backup_restore'
                    : 'inventory_2';

                const badgeColor =
                  act === 'consumed'
                    ? 'bg-emerald-100 text-emerald-800'
                    : act === 'wasted'
                    ? 'bg-red-100 text-red-800'
                    : act === 'added'
                    ? 'bg-blue-100 text-blue-800'
                    : act === 'restored'
                    ? 'bg-purple-100 text-purple-800'
                    : 'bg-slate-100 text-slate-800';

                return (
                  <div key={log.activityId} className="py-3.5 flex items-center justify-between gap-3 text-xs">
                    <div className="flex items-center gap-3 min-w-0">
                      <span className={`w-9 h-9 rounded-2xl flex items-center justify-center shrink-0 ${badgeColor}`}>
                        <span className="material-symbols-outlined text-[18px]">{icon}</span>
                      </span>

                      <div className="truncate">
                        <div className="flex items-center gap-2">
                          <span className="font-extrabold text-primary text-sm">{log.foodName}</span>
                          <span className={`px-2 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider ${badgeColor}`}>
                            {act}
                          </span>
                        </div>
                        <p className="text-[11px] text-on-surface-variant truncate mt-0.5">
                          {log.details || log.cultivar}
                        </p>
                      </div>
                    </div>

                    <div className="shrink-0 text-right">
                      <span className="text-[11px] font-semibold text-primary block">
                        {formatIsoDate(log.createdAt)}
                      </span>
                      {log.qualityScore && (
                        <span className="text-[10px] text-on-surface-variant block">
                          Quality: {log.qualityScore}%
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* ── OUTCOME MODAL (Record Consumed, Wasted, or Removed) ── */}
      {outcomeModalItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div
            onClick={() => setOutcomeModalItem(null)}
            className="fixed inset-0 bg-primary/30 backdrop-blur-xs transition-opacity"
          />
          <div className="relative w-full max-w-md bg-white rounded-3xl shadow-2xl p-6 z-10 border border-surface-container-high space-y-4 animate-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between pb-3 border-b border-surface-container-low">
              <div className="flex items-center gap-2">
                <span className="text-xl">📊</span>
                <h3 className="font-extrabold text-primary text-base">
                  Record Outcome: {outcomeModalItem.foodName}
                </h3>
              </div>
              <button
                type="button"
                onClick={() => setOutcomeModalItem(null)}
                className="p-1 rounded-full text-on-surface-variant hover:bg-surface-container"
              >
                <span className="material-symbols-outlined text-[18px]">close</span>
              </button>
            </div>

            <p className="text-xs text-on-surface-variant leading-relaxed">
              Choose the outcome for this pantry item. This updates your Food-Waste Impact Analytics and preserves the item in your Removed Products History logs.
            </p>

            {/* Action Selection Pills */}
            <div className="space-y-2">
              <label
                className={`flex items-center gap-3 p-3 rounded-2xl border cursor-pointer transition-all ${
                  outcomeAction === 'consumed'
                    ? 'border-emerald-500 bg-emerald-50/70'
                    : 'border-surface-container-high hover:bg-surface-container-lowest'
                }`}
              >
                <input
                  type="radio"
                  name="outcomeAction"
                  checked={outcomeAction === 'consumed'}
                  onChange={() => setOutcomeAction('consumed')}
                  className="accent-emerald-600"
                />
                <div>
                  <span className="font-bold text-xs text-emerald-900 block">🎉 Consumed / Saved</span>
                  <span className="text-[11px] text-emerald-800 block">
                    Enjoyed before expiration. Contributes to food waste reduction and pantry savings!
                  </span>
                </div>
              </label>

              <label
                className={`flex items-center gap-3 p-3 rounded-2xl border cursor-pointer transition-all ${
                  outcomeAction === 'wasted'
                    ? 'border-red-500 bg-red-50/70'
                    : 'border-surface-container-high hover:bg-surface-container-lowest'
                }`}
              >
                <input
                  type="radio"
                  name="outcomeAction"
                  checked={outcomeAction === 'wasted'}
                  onChange={() => setOutcomeAction('wasted')}
                  className="accent-red-600"
                />
                <div>
                  <span className="font-bold text-xs text-red-900 block">🗑️ Discarded / Wasted</span>
                  <span className="text-[11px] text-red-800 block">
                    Spoiled or thrown away. Logs waste metrics and helps generate future shopping insights.
                  </span>
                </div>
              </label>

              <label
                className={`flex items-center gap-3 p-3 rounded-2xl border cursor-pointer transition-all ${
                  outcomeAction === 'removed'
                    ? 'border-slate-500 bg-slate-50'
                    : 'border-surface-container-high hover:bg-surface-container-lowest'
                }`}
              >
                <input
                  type="radio"
                  name="outcomeAction"
                  checked={outcomeAction === 'removed'}
                  onChange={() => setOutcomeAction('removed')}
                  className="accent-slate-600"
                />
                <div>
                  <span className="font-bold text-xs text-slate-900 block">📦 Remove & Archive</span>
                  <span className="text-[11px] text-slate-700 block">
                    Remove from active pantry inventory without recording as spoiled.
                  </span>
                </div>
              </label>
            </div>

            {/* Optional Reason Input */}
            <div>
              <label className="text-[11px] font-bold text-primary block mb-1">
                Optional note / reason:
              </label>
              <input
                type="text"
                value={outcomeReason}
                onChange={(e) => setOutcomeReason(e.target.value)}
                placeholder="e.g., Used in dinner, shared with neighbor, or overripe"
                className="w-full px-3 py-2 text-xs bg-surface-container-low border border-surface-container-high rounded-xl focus:outline-none focus:ring-2 focus:ring-secondary/40"
              />
            </div>

            <div className="flex items-center justify-end gap-2 pt-3 border-t border-surface-container-low">
              <button
                type="button"
                onClick={() => setOutcomeModalItem(null)}
                className="px-4 py-2 rounded-full text-xs font-bold text-on-surface-variant hover:bg-surface-container transition-colors"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={isSubmittingOutcome}
                onClick={handleConfirmOutcome}
                className={`px-5 py-2 rounded-full text-xs font-bold text-white shadow-sm transition-all flex items-center gap-1.5 ${
                  outcomeAction === 'consumed'
                    ? 'bg-emerald-600 hover:bg-emerald-700'
                    : outcomeAction === 'wasted'
                    ? 'bg-red-600 hover:bg-red-700'
                    : 'bg-primary hover:bg-primary-container'
                }`}
              >
                {isSubmittingOutcome ? 'Saving...' : 'Record Outcome'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── SLIDE-OUT INSPECTION DETAIL DRAWER (Active & Removed) ── */}
      {selectedItem && (
        <div className="fixed inset-0 z-50 flex justify-end">
          <div
            onClick={() => setSelectedItem(null)}
            className="fixed inset-0 bg-primary/25 backdrop-blur-xs transition-opacity"
          />
          <div className="relative w-full max-w-md bg-white h-full shadow-2xl p-6 sm:p-8 flex flex-col justify-between overflow-y-auto z-10 border-l border-surface-container-high animate-in slide-in-from-right duration-300">
            <div>
              {/* Drawer Top Bar */}
              <div className="flex items-center justify-between pb-4 border-b border-surface-container-low mb-6">
                <span className="text-xs font-bold text-secondary uppercase tracking-wider">
                  {selectedItem.isArchived ? 'Historical Inspection Record' : 'Active Produce Record'}
                </span>
                <button
                  type="button"
                  onClick={() => setSelectedItem(null)}
                  className="p-1.5 text-on-surface-variant hover:text-on-surface rounded-full hover:bg-surface-container"
                >
                  <span className="material-symbols-outlined text-[20px]">close</span>
                </button>
              </div>

              {/* Item Photo */}
              <div className="w-full aspect-video rounded-2xl overflow-hidden mb-5 border border-surface-container-high">
                <img src={selectedItem.imageSrc} alt={selectedItem.foodName} className="w-full h-full object-cover" />
              </div>

              {/* Titles */}
              <div className="mb-4">
                <h2 className="text-xl font-extrabold text-primary">{selectedItem.foodName}</h2>
                <p className="text-xs text-on-surface-variant font-medium">{selectedItem.cultivar}</p>
              </div>

              {/* Status Banner for Removed Produce */}
              {selectedItem.isArchived && (
                <div className="p-3.5 rounded-2xl bg-surface-container-low border border-surface-container-high mb-4 text-xs space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-on-surface-variant">Archived Status:</span>
                    <span className="font-extrabold uppercase text-secondary">
                      {selectedItem.removalAction || 'Removed'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="text-on-surface-variant">Archived At:</span>
                    <span className="font-semibold text-primary">
                      {formatIsoDate(selectedItem.archivedAt)}
                    </span>
                  </div>
                  {selectedItem.removalReason && (
                    <div className="text-[11px] text-on-surface-variant pt-1 border-t border-surface-container-high">
                      <span className="font-bold text-primary">Reason:</span> {selectedItem.removalReason}
                    </div>
                  )}
                </div>
              )}

              {/* Data Strip */}
              <div className="grid grid-cols-2 gap-2.5 text-xs mb-5">
                <div className="p-3 rounded-2xl bg-surface-container-low">
                  <span className="text-on-surface-variant block">Freshness Score</span>
                  <span className="font-extrabold text-secondary text-sm">{selectedItem.qualityScore}%</span>
                </div>
                <div className="p-3 rounded-2xl bg-surface-container-low">
                  <span className="text-on-surface-variant block">Quality Window</span>
                  <span className="font-extrabold text-primary text-sm">{selectedItem.qualityPeriod}</span>
                </div>
              </div>

              {/* Packaged details if applicable */}
              {selectedItem.itemType === 'packaged' && (
                <div className="p-3.5 rounded-2xl bg-blue-50/70 border border-blue-200/60 space-y-1.5 text-xs mb-4">
                  <div className="flex items-center gap-1.5 font-bold text-blue-900">
                    <span className="material-symbols-outlined text-[16px]">barcode_scanner</span>
                    <span>Packaged Product Details</span>
                  </div>
                  {selectedItem.barcode && (
                    <div className="text-[11px] text-blue-800">
                      <span className="font-semibold">Barcode:</span> {selectedItem.barcode}
                    </div>
                  )}
                  {selectedItem.expiryDate && (
                    <div className="text-[11px] text-blue-800">
                      <span className="font-semibold">Expiry / Best Before:</span> {selectedItem.expiryDate}
                    </div>
                  )}
                  {selectedItem.ingredients && (
                    <div className="text-[11px] text-blue-800 line-clamp-3">
                      <span className="font-semibold">Ingredients:</span> {selectedItem.ingredients}
                    </div>
                  )}
                </div>
              )}

              {/* Advice */}
              <div className="space-y-3 text-xs">
                <div className="p-3.5 rounded-2xl bg-surface-container-low/80">
                  <span className="font-bold text-primary block mb-1">Storage Condition</span>
                  <p className="text-on-surface">{selectedItem.storageEnvironment}</p>
                </div>
                <div className="p-3.5 rounded-2xl bg-surface-container-low/80">
                  <span className="font-bold text-primary block mb-1">Culinary Handling</span>
                  <p className="text-on-surface">{selectedItem.guidance}</p>
                </div>
              </div>

              {/* Track Outcome for Active Produce */}
              {!selectedItem.isArchived && (
                <div className="mt-5 p-4 rounded-2xl bg-surface-container-low border border-surface-container-high/60">
                  <div className="flex items-center gap-1.5 text-xs font-bold text-primary mb-2">
                    <span className="material-symbols-outlined text-[16px] text-secondary">insights</span>
                    <span>Track Food Outcome</span>
                  </div>
                  <p className="text-[11px] text-on-surface-variant mb-3">
                    Log whether this item was enjoyed or had to be discarded to update your Food-Waste Impact Analytics.
                  </p>
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      type="button"
                      onClick={() => handleOpenOutcomeModal(selectedItem)}
                      className="py-2 px-3 rounded-xl bg-secondary text-white hover:bg-secondary/90 font-bold text-xs flex items-center justify-center gap-1.5 shadow-2xs transition-all cursor-pointer"
                    >
                      <span className="material-symbols-outlined text-[16px]">check_circle</span>
                      <span>Mark Consumed</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setOutcomeModalItem(selectedItem);
                        setOutcomeAction('wasted');
                      }}
                      className="py-2 px-3 rounded-xl bg-surface-container-highest hover:bg-red-50 text-red-700 font-bold text-xs flex items-center justify-center gap-1.5 border border-red-200 transition-all cursor-pointer"
                    >
                      <span className="material-symbols-outlined text-[16px]">delete_sweep</span>
                      <span>Mark Wasted</span>
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Bottom Actions */}
            <div className="pt-6 border-t border-surface-container-low flex items-center justify-between gap-2">
              {selectedItem.isArchived ? (
                <button
                  type="button"
                  onClick={() => handleRestore(selectedItem)}
                  className="px-4 py-2 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 hover:bg-emerald-200 transition-colors flex items-center gap-1 cursor-pointer"
                >
                  <span className="material-symbols-outlined text-[15px]">settings_backup_restore</span>
                  <span>Restore to Pantry</span>
                </button>
              ) : (
                <button
                  type="button"
                  onClick={() => handleDirectDelete(selectedItem)}
                  className="px-3.5 py-2 rounded-full text-xs font-bold text-error hover:bg-red-50 transition-colors cursor-pointer"
                >
                  Archive / Remove
                </button>
              )}

              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => {
                    freshoBuddyService.setFoodContext({
                      foodName: selectedItem.foodName,
                      cultivar: selectedItem.cultivar,
                      status: selectedItem.status,
                      qualityScore: selectedItem.qualityScore,
                      qualityPeriod: selectedItem.qualityPeriod,
                      storageEnvironment: selectedItem.storageEnvironment,
                      guidance: selectedItem.guidance,
                      imageSrc: selectedItem.imageSrc,
                      analyzedAt: selectedItem.analyzedTime,
                    });
                    setSelectedItem(null);
                    navigate('/fresho-buddy');
                  }}
                  className="px-3.5 py-2 rounded-full bg-surface-container hover:bg-secondary-container hover:text-on-secondary-container text-primary text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer"
                >
                  <img src={MASCOT_ASSETS.freshoBuddyUrl} alt="Buddy" className="w-4 h-4 object-contain" />
                  <span>Ask FreshoBuddy</span>
                </button>

                <button
                  type="button"
                  onClick={() => setSelectedItem(null)}
                  className="px-4 py-2 rounded-full bg-primary text-white text-xs font-bold hover:bg-primary-container transition-colors cursor-pointer"
                >
                  Done
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AnalysisHistoryPage;
