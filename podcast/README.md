# Wandering Aerun — production pipeline

An in-universe radio show for the Aerun campaign, hosted by the Compiler of
*A Wanderer's Journal of Aerun*, broadcast on a lost Relay far-speaker from
somewhere beyond the Rim Wall.

## One-time setup

1. **API key** — get it from elevenlabs.io → profile → API Keys, then in
   PowerShell (run this yourself; the key never needs to be in the repo or chat):

   ```powershell
   [Environment]::SetEnvironmentVariable('ELEVENLABS_API_KEY', 'sk_your_key_here', 'User')
   ```

   Open a **new** terminal afterward. Verify with `echo $env:ELEVENLABS_API_KEY`.

2. **ffmpeg** — `winget install Gyan.FFmpeg` (already done on this machine).

3. **Voices** — run `python generate.py --list-voices` and edit `voices.json`
   to taste. Placeholder premade voices are prefilled. For the Wanderer,
   consider designing a custom voice in the ElevenLabs Voice Library and
   pasting its ID.

## Producing an episode

```powershell
python generate.py episodes/ep001-the-long-reach.md   # calls ElevenLabs, caches clips
python master.py ep001-the-long-reach                 # stitch + radio filter -> build/ep001-the-long-reach/ep001-the-long-reach.mp3
```

- Clips are cached by content hash in `build/<slug>/clips/` — rewriting one
  line only regenerates that chunk. `--scene <name>` limits generation to one scene.
- `[radio]` scenes get the far-speaker bandpass; `[dry]` scenes are the
  Wanderer close on the mic. Script format is documented at the top of
  `episodes/ep001-the-long-reach.md`.
- **SFX that can actually be heard.** The sound-generation API puts transients (a
  switch clunk) at full scale and ambience (hum, static, room tone) 40+ dB down, and
  prompts containing "soft" / "faint" / "quiet" come back near-silent. So: write SFX
  prompts LOUD and close-miked, and let `master.py` level them - it measures every SFX
  clip, lifts the quiet tail, and sets it a few dB under the voice. SFX in `[radio]`
  scenes skip the 280 Hz high-pass, which used to delete hum outright. An optional
  third field sets prompt adherence: `SFX: description | seconds | 0.6`.
- **`BED: description | seconds | 0.6`** (anywhere in the script, once) generates a
  seamless looping ambience and mixes it under the whole episode at -36 dB.
  `python master.py <slug> --bed-db -32` makes it louder; `--no-bed` writes
  `<slug>-nobed.mp3` without it.
- Final loudness is a measured constant gain to -16 LUFS plus a limiter, not
  single-pass `loudnorm` (which rides the gain up on whatever opens the file).
- Dialogue uses **Eleven v3 text-to-dialogue** (multi-speaker, audio tags like
  `[whispers]`); SFX lines use the sound-generation endpoint.

## Publishing (archive.org + RSS)

One archive.org item hosts everything; the feed URL never changes.

1. Create the item once at archive.org → Upload: identifier `wandering-aerun`
   (must match `archive_item` in `show.json`), mediatype **audio**. Upload
   `cover.jpg` (3000x3000 square art) with it.
2. Per episode: upload `build/<slug>/<slug>.mp3` to the item, append an entry
   to `feed_episodes.json` (bytes = file size, duration from the mp3), run
   `python make_feed.py`, and upload the regenerated `feed.xml` to the same item.
3. The players subscribe **by URL** in any podcast app
   (Pocket Casts / Apple Podcasts "Follow a show by URL" / AntennaPod / Overcast):

   `https://archive.org/download/wandering-aerun/feed.xml`

   No directory submission, no review process, effectively private-by-obscurity —
   right for a campaign audience. If you ever want it in the public Apple/Spotify
   directories, submit that same feed URL to each; the feed already carries the
   required itunes tags.

## Notes

- `build/` is generated output — gitignored.
- Commercial usage rights for generated audio require a paid ElevenLabs plan;
  for a private campaign feed the free/starter tiers are fine.
