self.addEventListener('install', function(event) {
    console.log('Service Worker: Installed');
    event.waitUntil(
        caches.open('static-cache').then(function(cache) {
            return cache.addAll([
                '/', 
                '/static/icon.png',
                '/static/manifest.json',
                // Здесь перечислите все статические файлы вашего приложения, которые должны кешироваться
            ]);
        })
    );
});

self.addEventListener('activate', function(event) {
    console.log('Service Worker: Activated');
});

self.addEventListener('fetch', function(event) {
    event.respondWith(
        caches.match(event.request).then(function(response) {
            return response || fetch(event.request);
        })
    );
});
