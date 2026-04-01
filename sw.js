// TapToons Service Worker v3.0 Arcade Edition — Offline Support + Smart Cache
const CACHE_NAME = 'taptoons-v6';
const ASSETS = [
    './',
    './index.html',
    './manifest.json',
    './sounds.json',
    './icons/icon-72.png',
    './icons/icon-96.png',
    './icons/icon-128.png',
    './icons/icon-192.png',
    './icons/icon-512.png'
];

self.addEventListener('install', (e) => {
    e.waitUntil(
        caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS))
    );
    self.skipWaiting();
});

self.addEventListener('activate', (e) => {
    e.waitUntil(
        caches.keys().then(keys =>
            Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
        )
    );
    self.clients.claim();
});

// Network-first for HTML (always fresh), cache-first for assets
self.addEventListener('fetch', (e) => {
    const url = new URL(e.request.url);
    if (url.pathname.endsWith('.html') || url.pathname === '/' || url.pathname.endsWith('/')) {
        // Network-first for HTML — always get fresh version
        e.respondWith(
            fetch(e.request).then(response => {
                if (response.ok) {
                    const clone = response.clone();
                    caches.open(CACHE_NAME).then(cache => cache.put(e.request, clone));
                }
                return response;
            }).catch(() => caches.match(e.request))
        );
    } else {
        // Cache-first for static assets
        e.respondWith(
            caches.match(e.request).then(cached => cached || fetch(e.request).then(response => {
                if (response.ok) {
                    const clone = response.clone();
                    caches.open(CACHE_NAME).then(cache => cache.put(e.request, clone));
                }
                return response;
            }))
        );
    }
});
