<img src="assets/icon.svg" width="64" height="64" alt="">

# vice-city-radio

Vice City Radio is an unofficial, fan-made player for the GTA VI radio stations. Pick a Leonida station with L1/R1 and tune in to its real in-game tracklist.

- 22 music stations and 794 songs, taken from the [GTA Wiki station list](https://gta.fandom.com/wiki/Radio_Stations_in_GTA_VI).
- Songs play through YouTube's embedded player, so no audio is hosted.
- Every station runs on a shared clock. Tuning in drops you mid-song, the same for everyone, like the in-game radio.
- Works on phones: swipe the station tiles, and a mini player stays docked at the bottom.

## Hosting

The published site is only these files, about 480 KB on disk. A visitor downloads about 400 KB at most, because browsers fetch only the font files they need:

```
index.html    page and styles
app.js        player code
legal.html    disclaimer, privacy notice, takedown contact, credits
stations.js   station data
logos/        20 station logos as small WebP files
bg/           3 pre-blurred background photos
fonts/        self-hosted Barlow Condensed and its license
```

On short landscape screens, such as car head units, everything fits on one screen. The player's play button tunes in there.

The page must be served over `http://` or `https://`. Opening `index.html` straight from disk breaks YouTube playback. For a local test, run:

```
python -m http.server 8000
```

### GitHub Pages (free tier)

The site is live at **https://quarterwire.github.io/vice-city-radio/**. GitHub Pages is free for public repositories.

Pages serves the `gh-pages` branch, which holds only the files above. `tools/`, the README and the rest of the repo are never served. To publish a change:

1. Commit it to `master`.
2. Push `master`.
3. Run `bash tools/deploy.sh`.

The script copies the committed site files onto `gh-pages`, pushes them, and refuses to publish any unexpected file type. The live site updates about a minute later.

### Security checklist for the GitHub account

The site has no server, accounts or user data, so the realistic risk is someone taking over the GitHub account or repo and changing the page. These settings prevent that:

- **Turn on two-factor authentication** on the GitHub account, preferably with a passkey or an authenticator app. This matters more than anything else on this list.
- Branch protection rules block force pushes to, and deletion of, `master` and `gh-pages`.
- **Private vulnerability reporting** and **secret scanning** are turned on under **Settings → Security**.
- Never commit API keys or passwords. The site doesn't need any, and `.gitignore` blocks the usual secret files.

### What the site does to protect visitors

- **Content Security Policy.** A meta tag only allows scripts from the site itself and YouTube's player API, and frames only from YouTube. All code lives in `app.js`, so the policy can block every inline script. GitHub Pages can't send custom headers, so the policy is set in the page.
- **Nothing third-party loads until play.** The font is self-hosted. YouTube's player only loads when the listener presses play, and it uses the privacy-enhanced `youtube-nocookie.com` domain.
- **Escaped data.** Station and song text is HTML-escaped before it reaches the page.
- **Checked storage.** Saved settings are type-checked when read back, because every repo under `<user>.github.io` shares the same local storage.

## Legal

`legal.html` is linked from the footer, and from the top-right corner in the car layout. It covers:

- The not-affiliated disclaimer and the trademark notice.
- The privacy notice, covering local storage, GitHub Pages logging and YouTube.
- How to request a takedown, through GitHub issues or GitHub's DMCA process.
- The YouTube Terms of Service link that YouTube's API rules require.
- The CC BY-SA 3.0 credit for the GTA Wiki data.
- The font license.

To keep the fan-project risk low:

- **Never make money from it.** That means no ads, donations, merch or paid features. Commercial use is what turns a tolerated fan site into a target.
- **Act on takedown requests straight away.** Remove the item first and discuss later.
- **Only use images you have the right to use.** Credit their owners in `legal.html`.

`LICENSE` puts the project's own code under MIT. It does not cover the Rockstar material, wiki data, font or background images.

## Controls

| Action | Keyboard | Gamepad | Touch |
| --- | --- | --- | --- |
| Previous / next station | `Q` / `E`, arrow keys | L1 / R1 | Swipe the tiles |
| Tune in / radio off | `Space` | A | Tune In button |

- **Vehicle** shows the station blurb and a grid of every station.
- **On Demand** lists the station's tracklist, and tapping a song plays it.

## Known limits

- Phones stop YouTube audio when the screen locks or the browser goes to the background.
- iPhones sometimes block the first play. If nothing starts, tap the small video in the player.
- The talk stations The Wipe and WKTT are left out because their shows aren't on YouTube.
- 44 tracks had no good YouTube match and are skipped. These include fictional in-game songs such as Liquid Wilson's.
- The Vault Radio and The Sniper of La Perle have no logo on the wiki, so their tiles are drawn in CSS.

## Rebuilding the data

The `tools/` folder holds the scripts that produced `stations.js`. It is not needed for hosting.

1. Download the wiki text from `https://gta.fandom.com/api.php?action=parse&page=Radio_Stations_in_GTA_VI&prop=wikitext&format=json`.
2. Save the `wikitext` field to `wiki.txt`.
3. Run the scripts:

```
python tools/logos.py logos_raw logos
python tools/gen.py wiki.txt stations_raw.js
python tools/yt.py stations_raw.js stations.js tools/ytcache.json
```

To change the backgrounds, run `python tools/bg.py bg street=photo1.png hotel=photo2.png gas=photo3.png`. It crops, shrinks and blurs each photo ahead of time, so the browser never blurs live.

`logos.py` downloads the station logos from the wiki and shrinks them into `logos/`. `gen.py` holds each station's tagline, hosts and logo colors. `yt.py` matches songs to YouTube videos and caches the results in `tools/ytcache.json`. To fix a bad match, edit or null its entry in the cache and run `yt.py` again.

Unofficial fan project, not affiliated with or endorsed by Rockstar Games or Take-Two Interactive. Grand Theft Auto and GTA are their trademarks. Tracklists come from the GTA Wiki under CC BY-SA 3.0. Station logos belong to Rockstar Games.
