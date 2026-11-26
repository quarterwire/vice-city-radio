import re, json, sys, os
src, out = sys.argv[1], sys.argv[2]
txt = open(src, encoding='utf-8').read()
SOMA = lambda c: 'https://ice2.somafm.com/%s-128-mp3' % c
# id, wiki section, tagline, hosts, genre, place, tile, streams, fallback tag, kind
M = [
 ('afrobank','AfroBank FM','Afrobeats, Amapiano & Highlife','Burna Boy & Palms Trax','African','Vice City',
  dict(s='stack',bg='#eadcbf',fg='#3a2313',ac='#d4381e',l=['Afro','Bank','FM']),
  ['https://streaming.exclusive.radio/er/afrobeats/icecast.audio','https://listen.radioking.com/radio/397789/stream/449770'],'afrobeats','music'),
 ('backcountry','Back Country Radio','Renegade Country','MW & Delta Dawne','Country','Grassrivers',
  dict(s='oval',bg='#d8cdb4',fg='#c3302c',ac='#24417f',l=['Back','Country','Radio']),
  ['https://live.amperwave.net/direct/saga-wzidhd3mp3-ibc2','https://a10.asurahosting.com:8560/radio.mp3','https://listen.181fm.com/181-kickincountry_128k.mp3'],'classic country','music'),
 ('circoloco','CircoLoco Records Radio','House, Techno & After Hours','Seth Troxler & Antonio Carbonaro','Electronic','Vice Beach',
  dict(s='mono',bg='#111111',fg='#ffffff',ac='#ff3b3b',l=['Circo','Loco','Records Radio']),
  ['https://stream.bigfm.de/deeptechhouse/mp3-128/radio-browser',SOMA('beatblender')],'tech house','music'),
 ('cocoteo','Cocoteo FM','El party que nunca se apaga','El Martillo & La Gata','Reggaeton · Dembow','Little Havana',
  dict(s='chunk',bg='#d69ee0',fg='#fff4e6',ac='#5b2f17',l=['Cocoteo','FM']),
  ['https://latinareggaeton.ice.infomaniak.ch/latinareggaeton.mp3','https://radio.dominiserver.com/proxy/topurbano?mp=/stream'],'reggaeton','music'),
 ('dirtysouth','Dirty South Classics','Southern Hospitality','Trick & Trina','Southern Rap','Vice City',
  dict(s='outline',bg='#2b2b2d',fg='#e8e8e8',ac='#9a9a9a',l=['Dirty South','Classics']),
  ['https://listen.181fm.com/181-oldschool_128k.mp3','https://radio.thisisarealdomain.com/THE-CRIB','https://stream.laut.fm/astounded'],'old school hip hop','music'),
 ('emotion','Emotion 98.3','Soft Rock & Power Ballads','Doug Van Dyke','Soft Rock','Vice City',
  dict(s='script',bg='#1c2a55',fg='#ffffff',ac='#f6a6cb',l=['Emotion','98.3']),
  ['https://maggie.torontocast.com:2020/stream/rdmixlovesongs','https://listen.181fm.com/181-lite80s_128k.mp3'],'soft rock','music'),
 ('flash','Flash FM','Pop, Grooves & Good Times','Robyn & Alex','Pop','Vice City',
  dict(s='flash',bg='#f6dcc0',fg='#ff8a1f',ac='#ff3d9a',l=['Flash','FM']),
  ['https://listen.181fm.com/181-power_128k.mp3','https://ice2.somafm.com/poptron-128-mp3'],'pop','music'),
 ('gloriana','Gloriana Blues Radio','The Blues, Old & New','Keith Richards & Buddy Guy','Blues','Gloriana',
  dict(s='serif',bg='#0f2747',fg='#e8c46a',ac='#e8c46a',l=['Gloriana','Blues Radio']),
  ['https://listen.181fm.com/181-blues_128k.mp3'],'blues','music'),
 ('honey','Honey FM','90s R&B & Slow Jams','Chilli & T-Boz','R&B · Soul','Vice City',
  dict(s='round',bg='#f2b22a',fg='#4d2300',ac='#fff1c2',l=['honey','fm']),
  ['https://listen.181fm.com/181-90srnb_128k.mp3','https://listen.181fm.com/181-rnb_128k.mp3'],'rnb','music'),
 ('kaleidoscope','Kaleidoscope FM','The World, Off the Beaten Track','Jeremy Irons','Eclectic · World','Vice City',
  dict(s='kaleido',bg='#2a1240',fg='#ffffff',ac='#ffd23f',l=['Kaleido','scope FM']),
  ['https://stream.radioparadise.com/world-etc-128','https://stream.radioparadise.com/eclectic-128'],'eclectic','music'),
 ('ljr','Leonida Jazz Radio','Jazz Fusion & Funk','DJ Randy & DJ Stanley','Jazz Fusion','Vice City',
  dict(s='serif',bg='#121212',fg='#f2e6c9',ac='#d4a13a',l=['LJR','Leonida Jazz Radio']),
  ['https://streaming.klcbsofficial.com/listen/fusion/klcbs-fusion','https://smoothjazz.cdnstream1.com/2585_128.mp3','https://stream.srg-ssr.ch/m/rsj/mp3_128'],'jazz','music'),
 ('laola','Radio La Ola','Salsa, Son & Merengue','Gloria & Emilio Estefan','Classic Latin','Little Havana',
  dict(s='wave',bg='#0b6fa4',fg='#ffffff',ac='#ffd23f',l=['La Ola','Radio']),
  ['https://liveaudio.lamusica.com/MIA_WCMQ_icy','https://radio.dominiserver.com/proxy/topsalsaradio?mp=/stream'],'salsa','music'),
 ('onu','Radio On-U','Dub, Roots & Lovers Rock','Adrian Sherwood','Dub · Reggae','Vice City',
  dict(s='dot',bg='#f2eee4',fg='#111111',ac='#d8261c',l=['On-U','Radio']),
  [SOMA('reggae'),'https://listen.radioking.com/radio/50473/stream/87415'],'reggae','music'),
 ('stockyard','Stockyard FM','Indie Dance & Electronic','Victoria & Harrison','Indie · Electronic','Vice City',
  dict(s='block',bg='#c6ff3a',fg='#111111',ac='#111111',l=['Stockyard','FM']),
  [SOMA('poptron'),SOMA('indiepop')],'indie','music'),
 ('symphony','Symphony FM','The Great Orchestral Works','Yuja Wang','Classical','Vice City',
  dict(s='script',bg='#f5efe3',fg='#1b1b1b',ac='#9b7b3c',l=['Symphony','FM']),
  ['https://stream.srg-ssr.ch/m/rsc_de/mp3_128','https://live.streams.klassikradio.de/klassikradio-deutschland/stream/mp3'],'classical','music'),
 ('chamber','The Chamber 106.6','Crushing Metal','DJ Kerry & DJ Tom','Metal','Port Gellhorn',
  dict(s='metal',bg='#0b0b0b',fg='#e6e6e6',ac='#b3121b',l=['The Chamber','106.6']),
  [SOMA('metal'),'https://cast1.torontocast.com:4660/stream'],'heavy metal','music'),
 ('sniper','The Sniper of La Perle','Kompa & Haitian Heat','Kodak Black & Michaël Brun','Haitian · Caribbean','Little Haiti',
  dict(s='mono',bg='#0d1d52',fg='#ffffff',ac='#d21034',l=['Sniper','of La Perle','Unlockable']),
  ['https://antillesmedia.pro-fhi.net/antillesmediakompa','https://stream.flavorjamz.com/stream.mp3'],'kompa','music'),
 ('vault','The Vault Radio','After Dark at The Vault','DJ Pretzel','Club · Rave','Vice City',
  dict(s='block',bg='#ff4fa3',fg='#140014',ac='#140014',l=['The Vault','Radio']),
  [SOMA('thetrip'),SOMA('beatblender')],'house','music'),
 ('wipe','The Wipe','Leonida, Unfiltered','El Enigma, Dr. Nita & Ava','Talk · Satire','Vice City',
  dict(s='swipe',bg='#ffffff',fg='#111111',ac='#00b2ff',l=['the wipe']),
  ['https://ais-sa5.cdnstream1.com/b42761_64mp3','https://streaming04.liveboxstream.uk/proxy/roksta14/stream'],'comedy','talk'),
 ('vrock','V-Rock','Classic & Hard Rock','The Buck & Skipper McD','Rock','Vice City',
  dict(s='italic',bg='#17110e',fg='#ff7a1a',ac='#ffd33d',l=['V-Rock']),
  ['https://listen.181fm.com/181-eagle_128k.mp3','https://cast1.torontocast.com:4610/stream'],'classic rock','music'),
 ('vcrr','VCRR','Rap Right Now','JT & DJ Stevie J','Hip-Hop · Rap','Vice City',
  dict(s='mono',bg='#0d0d0d',fg='#ffcc00',ac='#ffffff',l=['VCRR','Vice City Rap Radio']),
  ['https://ilm.stream27.radiohost.de/ilm_iloveusonlyrapradio_mp3-192','https://listen.181fm.com/181-beat_128k.mp3','https://listen.reyfm.de/raproyal_192kbps.mp3'],'hip hop','music'),
 ('vicecityfm','Vice City FM','The 80s Never Ended','DJ Al & Madame Brigitte','80s Pop','Vice City',
  dict(s='neon',bg='#16002f',fg='#ff4fd8',ac='#36e2ff',l=['Vice City','FM']),
  ['https://listen.181fm.com/181-awesome80s_128k.mp3','https://media-ssl.musicradio.com/Heart80sMP3',SOMA('u80s')],'80s','music'),
 ('wktt','WKTT','We Know The Truth','Richard Bastion & The Brick','Talk Radio','Vice City',
  dict(s='stars',bg='#0e2a5c',fg='#ffffff',ac='#c8102e',l=['WKTT','We Know The Truth']),
  ['https://streaming04.liveboxstream.uk/proxy/roksta18/stream','https://icecast.walmradio.com:8443/otr'],'old time radio','talk'),
 ('worldwide','Worldwide FM','Jazz, Soul & Global Sounds','Gilles Peterson','Jazz · Soul · World','Vice City',
  dict(s='globe',bg='#f3f3f3',fg='#111111',ac='#ff5a00',l=['Worldwide','FM']),
  [SOMA('sonicuniverse'),'https://s-14.wefunkradio.com:8443/wefunk64.mp3'],'soul','music'),
]

secs, cur = {}, None
for line in txt.split('\n'):
    m = re.match(r'^===([^=].*?)===\s*$', line)
    if m:
        cur = m.group(1).strip(); secs[cur] = []; continue
    if re.match(r'^==[^=]', line):
        cur = None; continue
    if cur is not None:
        secs[cur].append(line)

def clean(s):
    s = re.sub(r'<ref[^>]*/>|<ref.*?</ref>', '', s)
    s = s.replace('{{nd}}', ' – ')
    for _ in range(3):
        s = re.sub(r'\{\{WP\|[^{}|]*\|([^{}]*)\}\}', r'\1', s)
        s = re.sub(r'\{\{WP\|([^{}]*)\}\}', r'\1', s)
    s = re.sub(r'\[\[(?:[^\]|]*\|)?([^\]]*)\]\]', r'\1', s)
    s = re.sub(r'\[https?://\S+ ([^\]]*)\]', r'\1', s)
    s = s.replace("'''", '').replace("''", '')
    return re.sub(r'\s+', ' ', s).strip()

def desc_of(lines):
    for l in lines:
        l2 = l.strip()
        if not l2 or l2.startswith(('{{', '[[File', '*', 'The following', '=')):
            continue
        return clean(l2)
    return ''

LOGO_BG = {'gloriana': '#efe6cf', 'honey': '#4a2408', 'laola': '#0d5d8c', 'vrock': '#ff8a1f', 'circoloco': '#f62d18'}
stations, total = [], 0
for (sid, sec, tag, hosts, genre, place, tile, streams, ftag, kind) in M:
    lines = secs[sec]
    tracks, shows = [], []
    for l in lines:
        if not l.startswith('*'):
            continue
        c = clean(l.lstrip('* '))
        m = re.match(r'^(.*?) – "?(.*?)"?(?: \((\d{4})\)?)?$', c)
        if m and kind == 'music':
            a, t, y = m.group(1), m.group(2).strip('"'), m.group(3) or ''
            tracks.append([a, t, int(y)] if y else [a, t])
        else:
            shows.append(c)
    total += len(tracks)
    st = dict(id=sid, name=sec, tag=tag, hosts=hosts, genre=genre, place=place, kind=kind,
              desc=desc_of(lines), tile=tile, streams=streams, ftag=ftag, tracks=tracks)
    if shows:
        st['shows'] = shows
    if sid in ('sniper', 'vault'):
        st['secret'] = 1
    # wiki logo (downloaded to logos/<id>.webp by tools/logos.py); 2 = full-bleed square
    if sid in LOGO_BG:
        tile['bg'] = LOGO_BG[sid]
    if os.path.exists(os.path.join(os.path.dirname(out) or '.', 'logos', sid + '.webp')):
        tile['img'] = 2 if sid == 'circoloco' else 1
    stations.append(st)

js = ('/* Station names, hosts and tracklists: GTA Wiki (CC BY-SA). '
      'Audio: third-party live radio streams picked by genre. Edit "streams" to change them. */\n'
      'window.STATIONS=' + json.dumps(stations, ensure_ascii=False, separators=(',', ':')) + ';\n')
open(out, 'w', encoding='utf-8', newline='\n').write(js)
print(len(stations), 'stations', total, 'tracks', len(js.encode()), 'bytes')
for s in stations:
    print(s['id'], len(s['tracks']), len(s.get('shows', [])), s['desc'][:80].encode('ascii', 'replace').decode())
