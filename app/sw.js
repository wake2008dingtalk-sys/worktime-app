// 网页版 Service Worker（子路径 /app/ 部署；APK 内不注册 SW）
// v1.1.10：升级缓存名，强制清掉 v1.1.5/v1.1.7 老缓存，避免旧版 PWA 卡在老版本
const CACHE_NAME = 'worktime-web-v6';
const ASSETS = ['./', './index.html'];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE_NAME).then(cache =>
      Promise.all(ASSETS.map(url =>
        cache.add(url).catch(err => console.warn('[SW] skip precache: ' + url, err))
      ))
    )
  );
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys.filter(k => k.indexOf('worktime-') === 0 && k !== CACHE_NAME).map(k => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const req = e.request;
  // 导航请求走 network-first，保证网页版更新能及时生效
  if (req.mode === 'navigate') {
    e.respondWith(
      fetch(req).then(res => {
        const copy = res.clone();
        caches.open(CACHE_NAME).then(c => c.put('./index.html', copy)).catch(() => {});
        return res;
      }).catch(() => caches.match('./index.html').then(r => r || caches.match(req)))
    );
    return;
  }
  e.respondWith(caches.match(req).then(r => r || fetch(req).catch(() => {})));
});
