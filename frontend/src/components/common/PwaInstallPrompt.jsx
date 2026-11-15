import React, { useState, useEffect } from 'react';
import { pwaService } from '../../services/pwaService.js';
import { MASCOT_ASSETS } from '../../assets/mascot/index.js';

export function PwaInstallPrompt({ variant = 'banner' }) {
  const [installState, setInstallState] = useState({
    isInstallable: false,
    isInstalled: false,
  });
  const [isDismissed, setIsDismissed] = useState(false);

  useEffect(() => {
    // Check if dismissed in this session
    const dismissed = sessionStorage.getItem('foodfresh_pwa_install_dismissed') === 'true';
    setIsDismissed(dismissed);

    const unsubscribe = pwaService.subscribe((state) => {
      setInstallState(state);
    });
    return unsubscribe;
  }, []);

  const handleInstall = async () => {
    await pwaService.promptInstall();
  };

  const handleDismiss = () => {
    setIsDismissed(true);
    sessionStorage.setItem('foodfresh_pwa_install_dismissed', 'true');
  };

  // If already running standalone or not installable, don't show
  if (installState.isInstalled || !installState.isInstallable) {
    return null;
  }

  // Variant: 'navbar-pill' (compact button for top navigation)
  if (variant === 'navbar-pill') {
    return (
      <button
        type="button"
        onClick={handleInstall}
        className="hidden md:flex items-center gap-1.5 px-3 py-1 rounded-full bg-secondary text-white hover:bg-secondary/90 text-xs font-bold shadow-2xs transition-all hover:scale-102 cursor-pointer"
        title="Install FoodFresh AI as desktop or mobile app"
      >
        <span className="material-symbols-outlined text-[16px]">download</span>
        <span>Install App</span>
      </button>
    );
  }

  // Variant: 'sidebar-card' (micro card inside sidebar drawer)
  if (variant === 'sidebar-card') {
    return (
      <div className="p-3 rounded-2xl bg-primary/5 border border-primary/10 flex flex-col gap-2">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
            <span className="material-symbols-outlined text-[16px]">install_mobile</span>
          </div>
          <span className="text-xs font-bold text-primary">Install FoodFresh</span>
        </div>
        <p className="text-[11px] text-on-surface-variant leading-tight">
          Add to home screen for 1-tap offline kitchen access.
        </p>
        <button
          type="button"
          onClick={handleInstall}
          className="w-full py-1.5 rounded-full bg-primary text-white hover:bg-primary-container text-xs font-bold transition-colors text-center cursor-pointer"
        >
          Install App
        </button>
      </div>
    );
  }

  // Variant: 'banner' (floating dismissible prompt)
  if (isDismissed) {
    return null;
  }

  return (
    <div className="fixed bottom-20 left-4 right-4 sm:left-auto sm:right-6 sm:max-w-sm z-40 animate-in fade-in slide-in-from-bottom duration-300">
      <div className="p-4 rounded-3xl bg-surface-container-lowest/95 backdrop-blur-md border border-surface-container-high/80 shadow-2xl flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-surface-container-low flex items-center justify-center p-1.5 shrink-0 border border-surface-container-high/60">
            <img
              src={MASCOT_ASSETS.freshoBuddyUrl}
              alt="FoodFresh AI"
              className="w-full h-full object-contain"
            />
          </div>
          <div>
            <span className="font-extrabold text-sm text-primary block leading-tight">
              Install FoodFresh AI
            </span>
            <p className="text-[11px] text-on-surface-variant leading-snug mt-0.5">
              Launch directly from your home screen or dock with offline access.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-1.5 shrink-0">
          <button
            type="button"
            onClick={handleInstall}
            className="px-3 py-1.5 rounded-full bg-secondary hover:bg-secondary/90 text-white font-bold text-xs shadow-2xs transition-all cursor-pointer"
          >
            Install
          </button>
          <button
            type="button"
            onClick={handleDismiss}
            className="p-1.5 rounded-full text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-colors cursor-pointer"
            aria-label="Dismiss install banner"
          >
            <span className="material-symbols-outlined text-[16px]">close</span>
          </button>
        </div>
      </div>
    </div>
  );
}

export default PwaInstallPrompt;

