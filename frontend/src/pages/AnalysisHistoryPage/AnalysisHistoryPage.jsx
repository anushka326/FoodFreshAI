import React, { useState } from 'react';
import { useFoodFresh } from '../../hooks/useFoodFresh.js';
import { MASCOT_ASSETS } from '../../assets/mascot/index.js';
import { freshoBuddyService } from '../../services/freshoBuddyService.js';
import { Toast } from '../../components/common/Toast.jsx';

export function AnalysisHistoryPage({ navigate }) {
  const { history, deleteHistoryItem } = useFoodFresh();
  const [searchTerm, setSearchTerm] = useState('');
  const [activeFilter, setActiveFilter] = useState('all'); // 'all' | 'fresh' | 'semi' | 'attention'
  const [selectedItem, setSelectedItem] = useState(null);
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

  const filteredItems = history.filter((item) => {
    const matchesSearch = item.foodName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.cultivar?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = activeFilter === 'all' || item.statusCategory === activeFilter;
    return matchesSearch && matchesFilter;
  });

  const handleDelete = async (id, name) => {
    await deleteHistoryItem(id);
    if (selectedItem?.id === id) {
      setSelectedItem(null);
    }
    triggerToast(`Removed ${name} from your pantry history.`);
  };

  return (
    <div className="space-y-6 pb-12 font-sans relative">
      <Toast message={toastMessage} visible={showToast} />

      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-primary tracking-tight">
            Pantry Produce Log
          </h1>
          <p className="text-xs sm:text-sm text-on-surface-variant mt-0.5">
            Review past quality evaluations, storage advice, and cellular degradation trends.
          </p>
        </div>

        <button
          type="button"
          onClick={() => navigate('/analyze')}
          className="px-5 py-2.5 rounded-full bg-primary hover:bg-primary-container text-white text-xs font-bold shadow-sm transition-all flex items-center gap-1.5 self-start sm:self-auto cursor-pointer"
        >
          <span className="material-symbols-outlined text-[16px]">add</span>
          <span>New Analysis</span>
        </button>
      </div>

      {/* Metric Overview Strip */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="p-4 rounded-2xl bg-white border border-surface-container-high/80 shadow-2xs">
          <span className="text-xs font-semibold text-on-surface-variant block">Total Logged Items</span>
          <span className="text-2xl font-extrabold text-primary block mt-1">{history.length} produce</span>
        </div>
        <div className="p-4 rounded-2xl bg-white border border-surface-container-high/80 shadow-2xs">
          <span className="text-xs font-semibold text-on-surface-variant block">Needing Cooking Soon</span>
          <span className="text-2xl font-extrabold text-error block mt-1">{needingCookingSoon} items</span>
        </div>
        <div className="p-4 rounded-2xl bg-white border border-surface-container-high/80 shadow-2xs">
          <span className="text-xs font-semibold text-on-surface-variant block">Pantry Longevity Index</span>
          <span className="text-2xl font-extrabold text-secondary block mt-1">{pantryLongevityIndex}%</span>
        </div>
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
            placeholder="Filter pantry produce by name..."
            className="w-full pl-10 pr-4 py-2 bg-surface-container-low/60 border border-surface-container-high rounded-full text-xs text-on-surface placeholder:text-outline focus:outline-none focus:ring-2 focus:ring-secondary/40"
          />
        </div>

        {/* Filter Chips */}
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
            Needs Attention
          </button>
        </div>
      </div>

      {/* Produce Items Grid / List */}
      {filteredItems.length === 0 ? (
        <div className="p-12 rounded-3xl bg-surface-container-low text-center border border-dashed border-surface-container-high">
          <span className="text-3xl block mb-2">🔍</span>
          <h3 className="text-base font-bold text-primary">No matching produce found</h3>
          <p className="text-xs text-on-surface-variant mt-1">
            Try adjusting your search query or filter tags above.
          </p>
          <button
            type="button"
            onClick={() => {
              setSearchTerm('');
              setActiveFilter('all');
            }}
            className="mt-4 px-4 py-2 rounded-full bg-primary text-white text-xs font-bold"
          >
            Clear Filters
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredItems.map((item) => (
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
                    {item.analyzedTime}
                  </div>
                </div>

                {/* Title & Status */}
                <div className="flex items-center justify-between mb-1">
                  <h3 className="font-bold text-sm text-primary">{item.foodName}</h3>
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

                <p className="text-[11px] text-on-surface-variant font-medium mb-3">
                  {item.cultivar}
                </p>

                <p className="text-xs text-on-surface-variant line-clamp-2 leading-relaxed mb-4">
                  {item.guidance}
                </p>
              </div>

              {/* Card Footer Actions */}
              <div className="pt-3 border-t border-surface-container-low flex items-center justify-between">
                <span className="text-xs font-bold text-primary">
                  ⏳ {item.qualityPeriod}
                </span>

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
                    onClick={() => handleDelete(item.id, item.foodName)}
                    className="p-1.5 text-on-surface-variant hover:text-error rounded-full hover:bg-red-50 transition-colors"
                    title="Remove record"
                  >
                    <span className="material-symbols-outlined text-[16px]">delete</span>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* SLIDE-OUT INSPECTION DETAIL DRAWER */}
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
                  Full Inspection Record
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

              {/* Data Strip */}
              <div className="grid grid-cols-2 gap-2.5 text-xs mb-5">
                <div className="p-3 rounded-2xl bg-surface-container-low">
                  <span className="text-on-surface-variant block">Freshness Score</span>
                  <span className="font-extrabold text-secondary text-sm">{selectedItem.qualityScore}%</span>
                </div>
                <div className="p-3 rounded-2xl bg-surface-container-low">
                  <span className="text-on-surface-variant block">Remaining Quality</span>
                  <span className="font-extrabold text-primary text-sm">{selectedItem.qualityPeriod}</span>
                </div>
              </div>

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
            </div>

            {/* Bottom Actions */}
            <div className="pt-6 border-t border-surface-container-low flex items-center justify-between gap-2">
              <button
                type="button"
                onClick={() => handleDelete(selectedItem.id, selectedItem.foodName)}
                className="px-3.5 py-2 rounded-full text-xs font-bold text-error hover:bg-red-50 transition-colors"
              >
                Delete
              </button>

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
