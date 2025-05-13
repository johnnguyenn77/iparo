// public/reconstructive-serviceworker.js

// Debug: indicate script load
console.log('SW: reconstructive-serviceworker.js load start');

// Global error listener
self.addEventListener('error', (event) => {
  console.error('SW global error:', event);
});

// Attempt importScripts with debug
try {
  importScripts('/reconstructive.js', '/reconstructive-banner.js');
  console.log('SW: importScripts succeeded');
} catch (e) {
  console.error('SW: importScripts failed:', e);
}

// Check that Reconstructive is available
if (typeof Reconstructive !== 'function') {
  console.error('SW: Reconstructive is not defined or not a function:', typeof Reconstructive);
} else {
  console.log('SW: Reconstructive found, version:', Reconstructive.prototype.VERSION);
}

// Instantiate Reconstructive with debug
let rc;
try {
  rc = new Reconstructive({ showBanner: true, debug: true });
  console.log('SW: rc instance created:', rc);
} catch (e) {
  console.error('SW: rc instantiation error:', e);
}

// Existing event listeners...
self.addEventListener('install',  e => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(self.clients.claim()));
// Bypass Reconstructive for API calls to avoid blocking backend endpoints
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (url.pathname.startsWith('/api/')) {
    // Let the browser handle API requests normally
    return;
  }
  rc && rc.reroute(e);
});