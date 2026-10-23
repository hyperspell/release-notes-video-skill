# Production helpers

Run these from your video project. `SKILL` is the path to the installed `release-notes-video` skill directory. The scripts take explicit paths; they do not depend on the original production repository, account wrappers or episode files.

## Beat grid and vocal evidence

First separate the selected working song with Demucs and transcribe its vocal stem as shown in [Song](song.md). Keep the original recording, working mix and transcript separate. Analyze the instrumental and vocals:

```bash
uv run --with librosa --with soundfile python3 "$SKILL/scripts/analyze_audio.py" beats episodes/sample-week/audio/stems/no_vocals.wav episodes/sample-week/timing/beats.json
uv run --with librosa --with soundfile python3 "$SKILL/scripts/analyze_audio.py" vocals episodes/sample-week/audio/stems/vocals.wav episodes/sample-week/timing/vocal-env.json
```

The beat output contains `bpm`, `period`, `offset`, `downbeat`, `beats_per_bar`, individual `beats`, `duration`, harmony/energy `votes`, and `fit_rms_seconds`. It fits a constant tempo and moves the grid onto low-frequency onsets. Compare both bar-phase votes with the actual section starts. A disagreement or a large fit residual needs inspection; a rubato song needs a manually established or variable-tempo grid. Use `--beats-per-bar 3` for triple meter instead of assuming four beats.

The vocal output contains `duration`, envelope sample `rate`, `db` samples and `onsets`. Inspect the envelope near uncertain shouts; a model's transcript alone cannot place them reliably.

## Lyric alignment and the gate

Write `sung.txt` with the words the selected take actually sings, section headers in brackets and crowd words in parentheses. Keep the locked lyric sheet separately so material changes can be reviewed. The transcript can be a Whisper JSON object with `segments[].words[]`, or a flat array of one-word entries:

```json
[{"word": "Please", "start": 1.0, "end": 1.3}, {"word": "update", "start": 1.4, "end": 1.8}]
```

Optional service timing uses the same flat schema, obtained through a supported export. Do not extract session credentials. Manual overrides are JSON, keyed by zero-based word index in the sung sheet:

```json
{"words": {"0": {"start": 1.02, "end": 1.31}}}
```

```bash
python3 "$SKILL/scripts/align_lyrics.py" --sheet episodes/sample-week/audio/sung.txt --transcript episodes/sample-week/audio/words.json --service-words episodes/sample-week/timing/service-words.json --envelope episodes/sample-week/timing/vocal-env.json --overrides episodes/sample-week/timing/overrides.json --duration 60 --output episodes/sample-week/timing/alignment-v1
```

Omit the optional `--service-words`, `--envelope` or `--overrides` arguments when that evidence is unavailable. Match `--duration` to the approved working song. Choose a new output directory for each revision.

The output is `lyrics.json` with `duration` and `lines[]`: each line has an `id`, section, text, start/end and timed words. Each word retains its source (`transcript`, `service`, `service+onset`, `manual` or `interpolated`) and the original transcript/service starts where available. The report lists unresolved words and independent timing disagreements over 250 ms. Service timings more than three seconds away from the matching transcript are rejected in favor of transcript evidence and reported for inspection; this catches stale replaced-section alignment.

The command writes the report and exits unsuccessfully if any word lacks evidence. Add manual overrides after listening, then rerun. `--allow-interpolation` writes explicitly labeled draft timings for review; it does not make the gate pass. Do not ship a draft merely because a timestamp exists. Follow [Sync](sync.md) for caption holds and ownership; the helper does not decide the visual treatment or resolve overlapping voices for you.

## Frame capture, stills and silent demos

Install Playwright and Chromium in the video project:

```bash
npm install playwright
npx playwright install chromium
```

Author the composition HTML/JavaScript for the episode. The included renderer captures that page; the product components, artwork and shot designs belong to the episode. Expose:

- `window.render(t)`: an async function that draws the complete frame at song time `t`. Wait for required fonts, images and clip seeks before resolving. Repeated or out-of-order seeks must reproduce the same frame.
- `window.SHOTS`: an ordered cut list of `{start, end}` objects covering the full declared duration. The original `{t0, t1}` names also work.
- `window.ready`: an optional promise for initial setup.

Use song time for every animation; avoid wall-clock timers, unseeded randomness or CSS animations that continue while frames are captured. Draw scene effects first and readable text afterward. Load approved fonts/assets locally for reproducible captures.

```bash
node "$SKILL/scripts/render.mjs" --page episodes/sample-week/composition.html --output episodes/sample-week/build/render-v1 --duration 60 --width 1080 --height 1350 --fps 24 --workers 4
node "$SKILL/scripts/render.mjs" --page episodes/sample-week/composition.html --output episodes/sample-week/qa/stills-v1 --duration 60 --mode stills --times 0,1,12.5,59
node "$SKILL/scripts/render.mjs" --page episodes/sample-week/composition.html --output episodes/sample-week/qa/cuts-v1 --duration 60 --mode shots
```

The render produces numbered PNGs, `shots.json`, `render.json` and a silent H.264 `picture.mp4`. It rejects cut-list gaps/overlaps, page errors, failed frames and reused output directories. Shots shorter than 0.6 seconds are flagged for review. Readiness and each frame have a 30-second deadline; `--timeout-ms` changes it. It resolves Playwright from the video project's dependencies.

Use `--from` and `--to` for a patch or standalone demo; both must land on frame boundaries. A partial render's frame zero corresponds to `--from` in song time. For a six-second silent demo, author a dedicated product-demo page with its own `{start: 0, end: 6}` shot list, render it with `--duration 6`, and copy its `picture.mp4` to the filename used in the kit. A demo page should explain the feature without relying on the music video's lyrics or jokes.

For a patch, replace the matching complete-render frames starting at `round(from × fps)`, then re-encode the complete picture. Inspect both boundaries and retain the original render until the revision is approved. See [Picture](picture.md).

## Gain-only mastering

Make the soundtrack's duration match the complete picture, including the final reading hold and fade. Then mux it:

```bash
python3 "$SKILL/scripts/master_audio.py" episodes/sample-week/build/render-v1/picture.mp4 episodes/sample-week/audio/song-sfx.wav episodes/sample-week/deliver/review-v1.mp4
```

The script rejects duration mismatches instead of silently truncating the outro. It measures the WAV, calculates plain gain toward −14 LUFS while respecting −1 dBTP, copies the video stream and encodes AAC. It remeasures the actual output; if AAC raises the peak, it reduces gain and encodes again from the original WAV. There is no limiter or compression. Its report says when the peak ceiling prevents reaching the loudness target. `--target`, `--ceiling` and `--duration-tolerance` can accommodate the agreed delivery settings. Existing masters are never overwritten.

## Flicker and archive checks

```bash
uv run --with numpy python3 "$SKILL/scripts/flicker.py" episodes/sample-week/deliver/review-v1.mp4 --output episodes/sample-week/qa/flicker-v1.json
python3 "$SKILL/scripts/asset_manifest.py" create episodes/sample-week episodes/sample-week/archive-manifest.json --exclude build --exclude qa
python3 "$SKILL/scripts/asset_manifest.py" verify restored/sample-week restored/sample-week/archive-manifest.json
```

The flicker detector compares spatial frame differences as well as brightness. It can flag a one-frame wrong image even when its average brightness is unchanged. Every hit needs visual inspection; a real cut or deliberate flash can trigger it.

The archive manifest records relative paths, byte sizes and SHA-256 hashes. Exclude only regenerable material; retain selected audio, useful candidates, approved stills, original clips, code, timing, final masters and the posting kit. Upload through the user's chosen Drive tools or other archive, download/read back the archive, and verify the restored files against the manifest before cleanup. The helper itself does not upload or change sharing permissions.
