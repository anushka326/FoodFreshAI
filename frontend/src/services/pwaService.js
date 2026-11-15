/**
 * FoodFresh AI — PWA Service Worker & Install Manager
 * Manages service worker lifecycle, installation prompts, and standalone display mode detection.
 */

class PwaService {
  constructor() {
    this.deferredPrompt = null;
    this.isInstallable = false;
    this.isInstalled = false;
    this.listeners = new Set();

    if (typeof window !== 'undefined') {
      this.init();
    }
  }

  init() {
    // Check if app is already running in standalone display mode
    const isStandalone =
      window.matchMedia('(display-mode: standalone)').matches ||
      window.navigator.standalone === true ||
      document.referrer.includes('android-app://');

    this.isInstalled = isStandalone;

    // Listen for beforeinstallprompt
    window.addEventListener('beforeinstallprompt', (e) => {
      // Prevent automatic browser mini-infobar
      e.preventDefault();
      this.deferredPrompt = e;
      this.isInstallable = true;
      this.notify();
    });

    // Listen for appinstalled
    window.addEventListener('appinstalled', () => {
      this.deferredPrompt = null;
      this.isInstallable = false;
      this.isInstalled = true;
      this.notify();
      console.log('[PWA] FoodFresh AI was successfully installed!');
    });

    // Register Service Worker
    this.registerServiceWorker();
  }

  async registerServiceWorker() {
    if ('serviceWorker' in navigator) {
      try {
        const registration = await navigator.serviceWorker.register('/sw.js', {
          scope: '/',
        });
        console.log('[PWA] Service Worker registered with scope:', registration.scope);

        // Check for updates
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing;
          if (newWorker) {
            newWorker.addEventListener('statechange', () => {
              if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                console.log('[PWA] New content is available; please refresh.');
              }
            });
          }
        });
      } catch (error) {
        console.warn('[PWA] Service Worker registration failed:', error);
      }
    }
  }

  /**
   * Trigger the native browser PWA installation dialog
   */
  async promptInstall() {
    if (!this.deferredPrompt) {
      return { outcome: 'dismissed', reason: 'no-prompt' };
    }

    try {
      this.deferredPrompt.prompt();
      const choiceResult = await this.deferredPrompt.userChoice;
      console.log('[PWA] User choice:', choiceResult.outcome);
      if (choiceResult.outcome === 'accepted') {
        this.isInstalled = true;
      }
      this.deferredPrompt = null;
      this.isInstallable = false;
      this.notify();
      return choiceResult;
    } catch (err) {
      console.warn('[PWA] Install prompt error:', err);
      return { outcome: 'error', error: err };
    }
  }

  /**
   * Subscribe to installability changes
   */
  subscribe(callback) {
    this.listeners.add(callback);
    // Initial emit
    callback({
      isInstallable: this.isInstallable,
      isInstalled: this.isInstalled,
    });
    return () => this.listeners.delete(callback);
  }

  notify() {
    for (const cb of this.listeners) {
      try {
        cb({
          isInstallable: this.isInstallable,
          isInstalled: this.isInstalled,
        });
      } catch (err) {
        console.error('[PWA] Listener error:', err);
      }
    }
  }
}

export const pwaService = new PwaService();
export default pwaService;

