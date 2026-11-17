/**
 * FoodFresh AI — Progressive Web App Service Worker
 * Provides offline application shell, asset caching, and safe network boundaries.
 * 
 * Security Guard: NEVER caches user-specific or authenticated /api/* responses
 * to prevent any cross-user data leakage (Requirement 9).
 */

const CACHE_NAME = 'foodfresh-ai-v1';

// Essential assets needed to boot the application shell offline
const PRECACHE_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/icons/fresho-buddy.svg',
  '/icons/logo.svg',
  '/icons/icon-192.png',
  '/icons/icon-512.png',
  '/icons/icon-maskable-192.png',
  '/icons/icon-maskable-512.png',
];

// Install: Precache shell assets and activate immediately
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(PRECACHE_ASSETS).catch((err) => {
        console.warn('[SW] Some precache assets could not be cached immediately:', err);
      });
    }).then(() => self.skipWaiting())
  );
});

// Activate: Clean up obsolete caches and claim existing clients
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME && key.startsWith('foodfresh-ai-')) {
            console.log('[SW] Clearing old cache:', key);
            return caches.delete(key);
          }
          return null;
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch: Strategy dispatcher based on request type
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // 1. Non-GET requests (POST, PUT, DELETE, etc.) cannot be cached
  if (request.method !== 'GET') {
    // If offline, provide a clean JSON fallback
    if (!navigator.onLine) {
      event.respondWith(
        new Response(
          JSON.stringify({
            offline: true,
            status: 'offline',
            message: 'You are currently offline. This action will be queued or must be retried when reconnected.',
          }),
          {
            status: 503,
            statusText: 'Service Unavailable (Offline)',
            headers: { 'Content-Type': 'application/json' },
          }
        )
      );
    }
    return;
  }

  // 2. API Endpoints (/api/*): STRICT Network-Only
  // Requirement 9: Do NOT cache sensitive API responses in Service Worker cache.
  // User data isolation and freshness must be strictly preserved.
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request).catch(() => {
        return new Response(
          JSON.stringify({
            offline: true,
            status: 'offline',
            message: 'You are offline. Live data cannot be retrieved right now.',
          }),
          {
            status: 503,
            statusText: 'Service Unavailable (Offline)',
            headers: { 'Content-Type': 'application/json' },
          }
        );
      })
    );
    return;
  }

  // 3. Navigation requests (HTML documents): Network-first with /index.html offline fallback
  if (request.mode === 'navigate' || request.destination === 'document') {
    event.respondWith(
      fetch(request)
        .then((response) => {
          if (response && response.status === 200) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
          }
          return response;
        })
        .catch(async () => {
          const cached = await caches.match(request);
          if (cached) return cached;
          const fallback = await caches.match('/index.html');
          if (fallback) return fallback;
          return caches.match('/');
        })
    );
    return;
  }

  // 4. Static assets (JS, CSS, fonts, images)
  // Stale-While-Revalidate / Cache-First with runtime caching
  const isStaticAsset =
    url.origin === self.location.origin ||
    url.hostname.includes('fonts.googleapis.com') ||
    url.hostname.includes('fonts.gstatic.com');

  if (isStaticAsset) {
    event.respondWith(
      caches.match(request).then((cachedResponse) => {
        const fetchPromise = fetch(request)
          .then((networkResponse) => {
            if (networkResponse && networkResponse.status === 200) {
              const clone = networkResponse.clone();
              caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
            }
            return networkResponse;
          })
          .catch(() => cachedResponse);

        return cachedResponse || fetchPromise;
      })
    );
  }
});

