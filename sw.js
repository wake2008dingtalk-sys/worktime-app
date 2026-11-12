// v1.1: 缓存名带版本号；移除跨域百度地图脚本（旧 AK 已轮换，且跨域 addAll 会让 install 失败）
const CACHE_NAME = 'worktime-v11';
const ASSETS = [
  '/',
  '/index.html'
];

self.addEventListener('install', e => {
  // 逐个资源 add 并吞掉单个失败：任一资源 404 / 跨域失败都不阻塞 Service Worker 安装
  e.waitUntil(
    caches.open(CACHE_NAME).then(cache =>
      Promise.all(ASSETS.map(url =>
        cache.add(url).catch(err => {
          console.warn('[SW] skip precache: ' + url, err);
        })
      ))
    )
  );
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  // 清理旧版本缓存（只清理 worktime- 前缀，避免误删同源其他缓存）
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys
          .filter(key => key.indexOf('worktime-') === 0 && key !== CACHE_NAME)
          .map(key => caches.delete(key))
      ))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  e.respondWith(
    caches.match(e.request).then(response => {
      return response || fetch(e.request).catch(() => {
        // 离线时返回缓存的 index.html
        if (e.request.mode === 'navigate') {
          return caches.match('/index.html');
        }
      });
    })
  );
});
