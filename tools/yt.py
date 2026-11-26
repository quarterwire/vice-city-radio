"""Match every station track to a YouTube video id + duration. Resumable via cache."""
import json, re, sys, os, unicodedata, urllib.request, urllib.parse, threading, time
from concurrent.futures import ThreadPoolExecutor

raw, out, cache_path = sys.argv[1], sys.argv[2], sys.argv[3]
src = open(raw, encoding='utf-8').read()
stations = json.loads(src[src.index('=') + 1:].rstrip().rstrip(';'))
cache = json.load(open(cache_path, encoding='utf-8')) if os.path.exists(cache_path) else {}
lock = threading.Lock()
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'
HDR = {'User-Agent': UA, 'Accept-Language': 'en-US,en;q=0.9', 'Cookie': 'SOCS=CAI; CONSENT=YES+'}

def norm(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    s = re.sub(r'\(.*?\)|\[.*?\]', ' ', s)
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()

def get(url, tries=3):
    for i in range(tries):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=HDR), timeout=20)
            return r.status, r.read().decode('utf-8', 'replace')
        except urllib.error.HTTPError as e:
            if e.code in (401, 403, 404):
                return e.code, ''
            time.sleep(2 + i * 3)
        except Exception:
            time.sleep(2 + i * 3)
    return 0, ''

def walk(o, acc):
    if isinstance(o, dict):
        if 'videoRenderer' in o:
            acc.append(o['videoRenderer'])
        for v in o.values():
            walk(v, acc)
    elif isinstance(o, list):
        for v in o:
            walk(v, acc)

def secs(t):
    p = [int(x) for x in t.split(':')]
    s = 0
    for x in p:
        s = s * 60 + x
    return s

def search(q):
    st, html = get('https://www.youtube.com/results?' + urllib.parse.urlencode({'search_query': q, 'sp': 'EgIQAQ=='}))
    m = re.search(r'var ytInitialData = (\{.*?\});</script>', html, re.S)
    if not m:
        return None
    acc = []
    walk(json.loads(m.group(1)), acc)
    res = []
    for v in acc[:10]:
        try:
            res.append(dict(id=v['videoId'],
                            title=''.join(r['text'] for r in v['title']['runs']),
                            owner=''.join(r['text'] for r in v.get('ownerText', v.get('longBylineText', {})).get('runs', [])),
                            len=secs(v['lengthText']['simpleText']) if 'lengthText' in v else 0))
        except Exception:
            pass
    return res

BAD = ['cover', 'karaoke', 'slowed', 'sped up', 'speed up', 'nightcore', '8d', 'reverb', 'instrumental', 'tutorial', 'reaction', 'piano version', 'bass boosted']

def score(c, artist, title, rank):
    t, o = norm(c['title']), norm(c['owner'])
    nt = norm(title)
    a_tokens = [w for w in norm(re.split(r',| & | feat\.| ft\.| and | with ', artist)[0]).split() if len(w) > 1]
    s = 0.0
    title_hit = nt and (nt in t or all(w in t.split() for w in nt.split()))
    if not title_hit:
        return None
    s += 3
    if c['owner'].endswith(' - Topic'):
        s += 3
    if a_tokens and all(w in (t + ' ' + o) for w in a_tokens):
        s += 2.5
    elif a_tokens and any(w in (t + ' ' + o) for w in a_tokens):
        s += 1
    else:
        s -= 2
    if 'official' in t:
        s += 0.8
    for b in BAD:
        if b in t and b not in nt:
            s -= 4
    if 'live' in t.split() and 'live' not in nt.split():
        s -= 2
    if 'remix' in t and 'remix' not in nt and 'mix' not in nt:
        s -= 2.5
    if 'gta' in t or 'grand theft' in t:
        s -= 1.5
    L = c['len']
    if L == 0 or L < 50 or L > 1500:
        s -= 5
    elif L > 720 and 'symphony' not in nt and 'concerto' not in nt:
        s -= 1.5
    s += 0.35 * (10 - rank)
    return s

def embeddable(vid):
    st, _ = get('https://www.youtube.com/oembed?' + urllib.parse.urlencode({'url': 'https://www.youtube.com/watch?v=' + vid, 'format': 'json'}))
    return st == 200

def resolve(artist, title):
    key = artist + ' – ' + title
    with lock:
        if key in cache:
            return cache[key]
    res = None
    for i in range(4):
        res = search(artist + ' ' + title)
        if res:
            break
        time.sleep(5 + i * 6)
    res = res or []
    cands = []
    for i, c in enumerate(res):
        sc = score(c, artist, title, i)
        if sc is not None and sc > 1:
            cands.append((sc, c))
    cands.sort(key=lambda x: -x[0])
    pick = None
    for sc, c in cands[:5]:
        if embeddable(c['id']):
            pick = [c['id'], c['len'], round(sc, 1), c['title'], c['owner']]
            break
    with lock:
        cache[key] = pick
    return pick

jobs = []
for st in stations:
    if st['kind'] != 'music':
        continue
    for tr in st['tracks']:
        if tr[0].startswith('Liquid Wilson'):
            continue
        jobs.append((tr[0], tr[1]))
print(len(jobs), 'tracks to resolve,', sum(1 for a, t in jobs if (a + ' – ' + t) in cache), 'cached', flush=True)
done = [0]
def work(j):
    r = resolve(*j)
    with lock:
        done[0] += 1
        if done[0] % 50 == 0:
            json.dump(cache, open(cache_path, 'w', encoding='utf-8'), ensure_ascii=False)
            print(done[0], 'done', flush=True)
    return r
with ThreadPoolExecutor(3) as ex:
    list(ex.map(work, jobs))
json.dump(cache, open(cache_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)

# assemble output
final, miss = [], []
for st in stations:
    if st['kind'] != 'music':
        continue
    tracks = []
    for tr in st['tracks']:
        key = tr[0] + ' – ' + tr[1]
        p = cache.get(key)
        if not p:
            miss.append(st['id'] + ': ' + key)
            continue
        tracks.append([tr[0], tr[1], tr[2] if len(tr) > 2 else 0, p[0], p[1]])
    st = {k: v for k, v in st.items() if k not in ('streams', 'ftag', 'kind', 'shows')}
    st['tracks'] = tracks
    final.append(st)
js = ('/* GTA VI radio stations. Names, hosts and tracklists from the GTA Wiki (CC BY-SA 3.0).\n'
      '   tracks: [artist, title, year, youtubeVideoId, seconds]. Audio streams from YouTube embeds. */\n'
      'window.STATIONS=' + json.dumps(final, ensure_ascii=False, separators=(',', ':')) + ';\n')
open(out, 'w', encoding='utf-8', newline='\n').write(js)
print('stations', len(final), 'tracks', sum(len(s['tracks']) for s in final), 'missing', len(miss), 'bytes', len(js.encode()))
open(out + '.missing.txt', 'w', encoding='utf-8').write('\n'.join(miss))
