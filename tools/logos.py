"""Download station logos from the GTA Wiki into a raw folder, then shrink them into logos/.
Usage: python tools/logos.py logos_raw logos"""
import json, sys, os, urllib.request, urllib.parse
out = sys.argv[1]
os.makedirs(out, exist_ok=True)
FILES = {
    'afrobank': 'Afrobank-logo.0r-.t v9b~9l.png',
    'backcountry': 'Radio-stations-from-the-gta-6-music-preview-site-v0-8rhl1vbxf9uh1.webp',
    'circoloco': 'Emoji-1572766318393036952-128.png',
    'cocoteo': 'Zqa8yubxf9uh1.png',
    'dirtysouth': 'Gta6-radio-station-dirty-south-classics-logo-transparent.webp',
    'emotion': 'Ab67706c0000da8480491c902d5810d5a0382f6d-Photoroom.png',
    'flash': 'Flash-logo.04o~oki.8dgm0.png',
    'gloriana': 'Emoji-1572764885589164122-128.png',
    'honey': 'Emoji-1572764263343194122-128.png',
    'kaleidoscope': 'KaleidoscopeFM.png',
    'laola': 'LaOla.png',
    'ljr': 'LJR.png',
    'onu': 'Ab67706c0000da84b3112ea9f90c7c01f4ce00b8.png',
    'stockyard': 'Ab67706c0000da84a05493483b7f2f892ef6196e.png',
    'symphony': 'Emoji-1566122355946950746-128.png',
    'chamber': 'Gsu92bbxf9uh1.png',
    'vcrr': 'VCRR.png',
    'vrock': 'VROCKGTAVI.png',
    'vicecityfm': 'ViceCityFMGTAVI.png',
    'worldwide': 'Emoji-1572765874627280937-128.png',
}
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36', 'Referer': 'https://gta.fandom.com/'}
titles = '|'.join('File:' + f for f in FILES.values())
q = urllib.parse.urlencode({'action': 'query', 'titles': titles, 'prop': 'imageinfo', 'iiprop': 'url|size|mime', 'format': 'json'})
d = json.load(urllib.request.urlopen(urllib.request.Request('https://gta.fandom.com/api.php?' + q, headers=UA), timeout=30))
info = {}
for p in d['query']['pages'].values():
    if 'imageinfo' in p:
        info[p['title'][5:].replace('_', ' ')] = p['imageinfo'][0]
norm = d['query'].get('normalized', [])
alias = {n['to'][5:]: n['from'][5:] for n in norm}
for sid, fn in FILES.items():
    ii = info.get(fn) or next((v for k, v in info.items() if alias.get(k) == fn), None)
    if not ii:
        print(sid, 'MISSING', fn); continue
    ext = ii['url'].split('?')[0].rsplit('.', 1)[-1].split('/')[0]
    data = urllib.request.urlopen(urllib.request.Request(ii['url'], headers=UA), timeout=30).read()
    open(os.path.join(out, sid + '.' + ext.lower()), 'wb').write(data)
    print(sid, ii['width'], 'x', ii['height'], ii.get('mime'), len(data))

# Shrink into the site's logos/ folder: trim transparent edges, 256px max, smallest of lossy/lossless WebP.
if len(sys.argv) > 2:
    import io
    from PIL import Image
    dst = sys.argv[2]
    os.makedirs(dst, exist_ok=True)
    for f in sorted(os.listdir(out)):
        im = Image.open(os.path.join(out, f)).convert('RGBA')
        bb = im.getchannel('A').point(lambda v: 255 if v > 12 else 0).getbbox()
        if bb:
            im = im.crop(bb)
        im.thumbnail((256, 256), Image.LANCZOS)
        best = None
        for kw in (dict(quality=68, alpha_quality=70, method=6), dict(lossless=True, quality=100, method=6)):
            b = io.BytesIO(); im.save(b, 'WEBP', **kw)
            if best is None or b.tell() < best.tell():
                best = b
        open(os.path.join(dst, f.rsplit('.', 1)[0] + '.webp'), 'wb').write(best.getvalue())
