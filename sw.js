/* Offline cache for the site's own files. Repeat visits open instantly, even with weak or no signal.
   Only same-origin files are cached. YouTube is never touched. tools/deploy.sh stamps VERSION on every deploy. */
const VERSION = "dev";
const CACHE = "vcr-" + VERSION;
const LOGOS = ["afrobank","backcountry","chamber","circoloco","cocoteo","dirtysouth","emotion","flash","gloriana","honey",
  "kaleidoscope","laola","ljr","onu","stockyard","symphony","vcrr","vicecityfm","vrock","worldwide"];
const FILES = ["./", "app.js", "stations.js", "legal.html", "bg/street.webp", "bg/hotel.webp", "bg/gas.webp",
  ...["500", "600", "700", "800", "800i"].map((w) => `fonts/barlow-condensed-${w}-latin.woff2`),
  ...LOGOS.map((l) => `logos/${l}.webp`)];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(FILES)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys().then((keys) => Promise.all(keys.filter((k) => k.startsWith("vcr-") && k !== CACHE).map((k) => caches.delete(k))))
    .then(() => self.clients.claim()));
});

// Install reuses what the browser already downloaded (no second download over a weak signal).
// Serve from the cache straight away, and refresh the cached copy in the background when there is signal.
self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET" || new URL(req.url).origin !== location.origin) return;
  e.respondWith(caches.open(CACHE).then(async (cache) => {
    const key = req.mode === "navigate" && new URL(req.url).pathname.endsWith("/") ? "./" : req;
    const hit = await cache.match(key, { ignoreSearch: true });
    const fresh = fetch(req).then((res) => { if (res.ok && res.type === "basic") cache.put(key, res.clone()); return res; });
    if (hit) { e.waitUntil(fresh.catch(() => {})); return hit; }
    return fresh.catch(() => Response.error());
  }));
});
