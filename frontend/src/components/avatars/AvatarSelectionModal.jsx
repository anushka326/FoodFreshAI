import React, { useState, useEffect, useRef } from 'react';
import {
  AVATAR_CATEGORIES,
  THEMED_AVATARS,
  getAvatarById,
  getAvatarsByCategory,
} from '../../assets/avatars/avatarCatalog.jsx';

/**
 * Themed Avatar Selection Modal
 * Allows user to browse 6 curated categories of FoodFresh AI friendly avatars,
 * preview selection with bio/personality, and save directly to their authenticated account.
 */
export function AvatarSelectionModal({
  isOpen,
  onClose,
  currentAvatarId = null,
  onSaveAvatar,
  isSaving = false,
}) {
  const [activeCategory, setActiveCategory] = useState('fruit_buddies');
  const [selectedAvatarId, setSelectedAvatarId] = useState(currentAvatarId || 'fruit_apple');
  const [errorMsg, setErrorMsg] = useState(null);
  const modalRef = useRef(null);

  // Sync initial selection when modal opens
  useEffect(() => {
    if (isOpen) {
      const initial = currentAvatarId || 'fruit_apple';
      setSelectedAvatarId(initial);
      const found = getAvatarById(initial);
      if (found) {
        setActiveCategory(found.category);
      }
      setErrorMsg(null);
    }
  }, [isOpen, currentAvatarId]);

  // Handle ESC key to close modal
  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && !isSaving) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, isSaving, onClose]);

  if (!isOpen) return null;

  const currentCategoryAvatars = getAvatarsByCategory(activeCategory);
  const selectedAvatar = getAvatarById(selectedAvatarId);
  const isUnchanged = selectedAvatarId === currentAvatarId;

  const handleSave = async () => {
    if (!selectedAvatarId) {
      setErrorMsg('Please select an avatar before saving.');
      return;
    }
    setErrorMsg(null);
    try {
      await onSaveAvatar(selectedAvatarId);
    } catch (err) {
      setErrorMsg(err.message || 'Failed to save avatar. Please try again.');
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-black/60 backdrop-blur-xs animate-fade-in"
      role="dialog"
      aria-modal="true"
      aria-labelledby="avatar-modal-title"
      onClick={(e) => {
        if (e.target === e.currentTarget && !isSaving) onClose();
      }}
    >
      <div
        ref={modalRef}
        className="w-full max-w-4xl bg-surface rounded-3xl shadow-2xl border border-surface-container-high flex flex-col max-h-[92vh] overflow-hidden animate-scale-up"
      >
        {/* Header */}
        <div className="px-5 sm:px-8 py-5 border-b border-surface-container-high flex items-center justify-between bg-surface-container-low/60">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-secondary-container/80 flex items-center justify-center text-xl shadow-2xs">
              🌱
            </div>
            <div>
              <h2 id="avatar-modal-title" className="text-xl sm:text-2xl font-black text-on-surface tracking-tight">
                Choose Your Kitchen Avatar
              </h2>
              <p className="text-xs sm:text-sm text-on-surface-variant">
                Pick a friendly companion to represent your FoodFresh AI kitchen journey.
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            disabled={isSaving}
            className="w-9 h-9 rounded-full flex items-center justify-center text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high transition-colors disabled:opacity-50"
            aria-label="Close dialog"
          >
            <span className="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>

        {/* Category Tabs */}
        <div className="px-5 sm:px-8 pt-4 pb-2 border-b border-surface-container bg-surface flex items-center gap-2 overflow-x-auto no-scrollbar">
          {AVATAR_CATEGORIES.map((cat) => {
            const isActive = activeCategory === cat.id;
            return (
              <button
                key={cat.id}
                type="button"
                onClick={() => setActiveCategory(cat.id)}
                className={`px-3.5 py-2 rounded-xl text-xs sm:text-sm font-bold flex items-center gap-2 whitespace-nowrap transition-all duration-150 shrink-0 select-none ${
                  isActive
                    ? 'bg-primary text-on-primary shadow-sm ring-2 ring-primary/20'
                    : 'bg-surface-container-low text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface'
                }`}
              >
                <span>{cat.icon}</span>
                <span>{cat.label}</span>
              </button>
            );
          })}
        </div>

        {/* Modal Body: Left Grid + Right Preview */}
        <div className="p-5 sm:p-8 flex-1 overflow-y-auto grid grid-cols-1 md:grid-cols-12 gap-6 bg-surface-container-lowest/30">
          {/* Avatar Grid (8 cols on desktop) */}
          <div className="md:col-span-7 flex flex-col gap-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-on-surface-variant uppercase tracking-wider">
                {AVATAR_CATEGORIES.find((c) => c.id === activeCategory)?.label || 'Avatars'} ({currentCategoryAvatars.length})
              </span>
              <span className="text-xs text-on-surface-variant">
                Click an avatar to select
              </span>
            </div>

            <div className="grid grid-cols-3 sm:grid-cols-3 gap-3.5 sm:gap-4">
              {currentCategoryAvatars.map((avatar) => {
                const isSelected = selectedAvatarId === avatar.id;
                const isCurrent = currentAvatarId === avatar.id;

                return (
                  <button
                    key={avatar.id}
                    type="button"
                    onClick={() => {
                      setSelectedAvatarId(avatar.id);
                      setErrorMsg(null);
                    }}
                    className={`relative group flex flex-col items-center p-3 rounded-2xl border transition-all duration-200 text-center select-none ${
                      isSelected
                        ? 'border-primary bg-primary-container/20 ring-3 ring-primary/30 shadow-md scale-[1.02]'
                        : 'border-surface-container-high bg-surface hover:border-primary/50 hover:bg-surface-container-low hover:shadow-2xs'
                    }`}
                  >
                    {/* Active Checkmark Badge */}
                    {isSelected && (
                      <div className="absolute top-2 right-2 w-5 h-5 rounded-full bg-primary text-on-primary flex items-center justify-center shadow-xs text-xs animate-scale-up">
                        <span className="material-symbols-outlined text-[13px] font-black">check</span>
                      </div>
                    )}

                    {/* Current User Badge */}
                    {isCurrent && !isSelected && (
                      <span className="absolute top-2 left-2 px-1.5 py-0.5 rounded-full bg-surface-container text-on-surface-variant text-[9px] font-bold">
                        Current
                      </span>
                    )}

                    {/* Avatar Vector Graphic */}
                    <div
                      className="w-16 h-16 sm:w-20 sm:h-20 rounded-2xl flex items-center justify-center p-1 overflow-hidden transition-transform group-hover:scale-105"
                      style={{ backgroundColor: avatar.bg || '#f1f5f9' }}
                    >
                      <div className="w-full h-full flex items-center justify-center">
                        {avatar.svg}
                      </div>
                    </div>

                    {/* Avatar Label */}
                    <div className="mt-2.5 w-full">
                      <p className="text-xs sm:text-sm font-bold text-on-surface truncate">
                        {avatar.name}
                      </p>
                      <p className="text-[10px] sm:text-xs text-on-surface-variant truncate">
                        {avatar.subtitle}
                      </p>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Avatar Preview Card (5 cols on desktop) */}
          <div className="md:col-span-5 flex flex-col">
            <div className="bg-surface rounded-2xl border border-surface-container-high p-5 sm:p-6 flex flex-col items-center text-center h-full justify-between shadow-xs">
              <div className="flex flex-col items-center w-full">
                <span className="text-[11px] font-extrabold text-primary uppercase tracking-widest bg-primary-container/40 px-3 py-1 rounded-full mb-4">
                  Selected Preview
                </span>

                {selectedAvatar ? (
                  <>
                    <div
                      className="w-32 h-32 sm:w-36 sm:h-36 rounded-3xl p-3 flex items-center justify-center shadow-lg border-2 border-primary/20 animate-fade-in"
                      style={{ backgroundColor: selectedAvatar.bg || '#f0fdf4' }}
                    >
                      <div className="w-full h-full flex items-center justify-center">
                        {selectedAvatar.svg}
                      </div>
                    </div>

                    <h3 className="text-xl font-black text-on-surface mt-4 tracking-tight">
                      {selectedAvatar.name}
                    </h3>
                    <p className="text-xs font-semibold text-primary mt-0.5">
                      {selectedAvatar.subtitle}
                    </p>

                    <div className="mt-3.5 p-3 rounded-xl bg-surface-container-low text-left w-full border border-surface-container">
                      <p className="text-xs text-on-surface-variant leading-relaxed">
                        {selectedAvatar.bio}
                      </p>
                    </div>

                    <div className="mt-3 w-full flex items-center justify-between text-[11px] text-on-surface-variant px-1">
                      <span>Category:</span>
                      <span className="font-bold text-on-surface">
                        {AVATAR_CATEGORIES.find((c) => c.id === selectedAvatar.category)?.label}
                      </span>
                    </div>

                    {selectedAvatarId === currentAvatarId && (
                      <div className="mt-2 text-xs font-bold text-primary flex items-center gap-1">
                        <span className="material-symbols-outlined text-[16px]">verified</span>
                        <span>Currently active on your profile</span>
                      </div>
                    )}
                  </>
                ) : (
                  <div className="py-12 text-on-surface-variant text-sm">
                    Select an avatar to see details
                  </div>
                )}
              </div>

              {/* Status / Error Alert */}
              {errorMsg && (
                <div className="mt-4 w-full p-2.5 rounded-xl bg-error/10 border border-error/20 text-error text-xs font-semibold flex items-center gap-2 text-left">
                  <span className="material-symbols-outlined text-[16px]">error</span>
                  <span>{errorMsg}</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="px-5 sm:px-8 py-4 border-t border-surface-container-high bg-surface-container-low/80 flex flex-col-reverse sm:flex-row items-center justify-between gap-3">
          <div className="text-xs text-on-surface-variant text-center sm:text-left">
            <span>Avatars are synced across your dashboard, sidebar, and recipes.</span>
          </div>

          <div className="flex items-center gap-3 w-full sm:w-auto justify-end">
            <button
              type="button"
              onClick={onClose}
              disabled={isSaving}
              className="flex-1 sm:flex-initial px-5 py-2.5 rounded-xl font-bold text-xs sm:text-sm text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleSave}
              disabled={isSaving || !selectedAvatarId || isUnchanged}
              className={`flex-1 sm:flex-initial px-6 py-2.5 rounded-xl font-bold text-xs sm:text-sm flex items-center justify-center gap-2 transition-all shadow-sm ${
                isSaving || !selectedAvatarId || isUnchanged
                  ? 'bg-surface-container text-on-surface-variant opacity-60 cursor-not-allowed'
                  : 'bg-primary text-on-primary hover:bg-primary/90 hover:shadow-md active:scale-95'
              }`}
            >
              {isSaving ? (
                <>
                  <div className="w-4 h-4 border-2 border-on-primary border-t-transparent rounded-full animate-spin" />
                  <span>Saving...</span>
                </>
              ) : (
                <>
                  <span className="material-symbols-outlined text-[18px]">check_circle</span>
                  <span>Save Avatar</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

