# Tools and setup

Use this stack to produce the episode. Keep the user's existing tool choices and accounts; resolve a missing tool before planning shots that depend on it.

| Stage | Tool | Handoff |
|---|---|---|
| Song | Suno Custom mode | Locked lyric sheet, style seeds, labeled candidate recordings and selected WAV |
| Listening comparison | Gemini with audio input | All complete candidates in one request, ranked against the brief |
| Stills | OpenAI image generation | Approved character references and a first frame for each generated shot |
| Animation | Dreamina with Seedance | Directed clips, retained originals and generation job IDs |
| 3D | Blender | Reproducible scenes, rendered shots or clay motion references for Seedance |
| Product capture | Playwright | Real product behavior with fictional data, captured at the intended viewport |
| Composition | Node.js, HTML Canvas and Playwright | Frames computed from song time: product shots, clips, captions, feature bubbles and effects |
| Song analysis | Demucs, Whisper and librosa | Vocal stem, word timing, onset envelope and beat grid |
| Sound effects | ElevenLabs, when needed | Short reusable effects, mixed quietly under the approved song |
| Delivery | FFmpeg, ffprobe and Pillow | Encoded master, silent demos, inspection reports and contact sheets |

## Preflight

Check Node.js, Python 3.10+, FFmpeg/ffprobe and uv. Check Blender if the storyboard uses 3D. Install Playwright in the video project and its Chromium browser; keep the project's package lock so later renders use the same version. Contact sheets need Pillow; audio analysis needs Demucs, Whisper and librosa. On Apple Silicon, `mlx-whisper` is an alternative to the standard Whisper implementation.

Verify the user's Suno session, Dreamina access, image-generation access and Gemini audio access before generating. API credentials belong in the user's local credential store or environment. Record tool/model versions in the episode notes. Resolve paid generation against the authorized budget.

## Suno: song production

Open [Suno Create](https://suno.com/create) in the user's signed-in browser. Use Custom mode, paste the locked lyrics, supply the style and exclude prompts, and turn instrumental mode off. Set the vocal direction and quality controls available in the current editor; inspect the UI rather than assuming a historical model or switch still exists. Follow the service's current rules for browser automation.

Generate two or three meaningfully different style seeds, usually two takes each. Log labels, take IDs, prompts and settings. Export the full candidates for listening, then obtain the selected take at production quality, preferably WAV. Keep the original. See [Song](song.md) for pronunciation, comparison and editing.

## Gemini: compare the actual performances

Use the latest suitable audio-capable Gemini model available to the account. Discover the model instead of hard-coding a version. Send all full recordings together with take labels, locked lyrics, target duration, reference qualities and the user's latest feedback. Ask for a ranking, concrete strengths and weaknesses, two finalists and a winner. Preserve the request and response; the user chooses the song.

Use the provider's supported audio/file input and current limits, as described in the [audio guide](https://ai.google.dev/gemini-api/docs/audio). A transcript is useful for lyric checks but cannot stand in for listening to the performance.

## OpenAI image generation: first frames and references

Use the host's image-generation tool or the [OpenAI image-generation API](https://developers.openai.com/api/docs/guides/image-generation). Make the character/set references first, then compose a first-frame still for each Seedance shot. Include the approved references when editing to keep faces, costumes and props consistent. Inspect the still before spending on animation. Add exact typography and product UI in the composition rather than asking the image model to render them.

## Dreamina / Seedance: directed animation

Use [Dreamina](https://dreamina.capcut.com/ai-video/image-to-video) for the generated moving shots. Prefer the full-quality Seedance model for finals; Seedance 2.5 was the production choice for this workflow. Discover the current models, supported ratios, durations, resolutions and prices in the account before quoting a batch.

For each shot, specify the first-frame still, action, camera move, lighting, duration and safe crop. Use a portrait source when it protects the final 4:5 composition. Start with 720p for brief cutaways when it holds up at final size; use a higher resolution when detail warrants it. Review a sample before committing to a large batch. Each shot gets its own first frame rather than inheriting the previous clip's last frame.

### With the Dreamina Canvas CLI

When `dreamina-canvas` is installed, use it to keep jobs inspectable and recoverable. Its current schema is the authority for commands and model parameters. The CLI and its own skill are separate installations; use Dreamina's browser interface when the CLI is unavailable.

Select the user's intended profile. The example uses a profile named `video`; replace it with theirs:

```bash
DREAMINA_PROFILE=video
dreamina-canvas version
dreamina-canvas schema
dreamina-canvas --profile "$DREAMINA_PROFILE" auth status
dreamina-canvas --profile "$DREAMINA_PROFILE" model list --type video
dreamina-canvas --profile "$DREAMINA_PROFILE" model find Seedance --type video
```

1. Select or create the episode canvas. Upload approved source media using the current `resource upload` contract.
2. Create one video node per shot with `node create`, using a canonical model and supported reference mode from discovery. Keep the prompt and selected parameters in the episode project.
3. Run `node quote` for the prepared nodes. Present the total cost and resolution choices, obtain any missing budget approval, then use the CLI's credit-confirmation flow. A technical confirmation token does not replace the user's spending decision.
4. Run each node with its own stable submission ID. Keep canvas, node, submission and operation identities in the local episode record. Run independent shots concurrently within the account's limits; wait for prerequisite stills or references first.
5. Use `operation status` or `operation wait` to follow the same jobs to completion. After a timeout or interrupted connection, inspect and resume those jobs before submitting anything new. Avoid paying twice for an uncertain result.
6. Export the selected completed originals through the supported download/export route. Inspect the actual files for duration, crop, likeness, unexpected speech and frozen tails. Acceptance of a job is not a completed clip.

Do not copy a private account profile, project wrapper or canvas ID into the shared skill. Store the episode's durable job IDs with the episode; credentials and short-lived access material stay in the account's credential store.

## Blender: sets, props and deliberate camera moves

Use Blender when the shot needs exact geometry, a controlled camera move, reusable 3D props, or a stylized scene that generation would make inconsistent. It can produce a final shot directly or a clay reference to guide Seedance. Choose this while storyboarding; do not add 3D just to use the tool.

Write a Python scene-building script in the episode project. Set the frame size, frame rate and range explicitly; keyframe cameras, lights and objects from the shot's song-time boundaries. Save a `.blend` file as well as the script. Render a few key frames before the full sequence to check framing, silhouettes and the final crop.

For example, write `shots/build_scene.py` to save `scene.blend` in the episode directory, then run from that directory:

```bash
blender --background --python shots/build_scene.py
blender --background scene.blend --render-output //frames/shot_ --render-format PNG --render-anim
```

Set output options before `--render-anim`: Blender executes arguments in order. `//` is relative to the loaded blend file. See the [command-line rendering guide](https://docs.blender.org/manual/en/latest/advanced/command_line/render.html).

For a motion reference, render a simple clay version showing the intended camera and blocking. Supply it to Seedance only through a model mode that accepts video references, alongside the approved appearance references. Include any billable reference duration in the quote. For a final Blender shot, bring the rendered frames directly into the composition. Keep both routes at the episode's frame rate and preserve their source scenes.

## Product capture and the main composition

Use Playwright to capture the real product or source-faithful HTML with fictional data. Keep the viewport and application geometry stable across shots. Capture at enough resolution for the detail to remain readable in the final crop.

Build the main composition in the video project with JavaScript and HTML Canvas. Use a single song-time clock: seeking to time `t` must reproduce the same frame, including clips, camera moves, captions and UI state. Load fonts and media before capture; explicitly seek video clips and seed any procedural randomness. Use Playwright to capture the frames, then FFmpeg to encode them and mux the soundtrack. Keep audio processing separate from picture rendering.

Blender renders and Seedance originals are inputs to this timeline. Draw exact product text, feature sentences and lyrics after visual effects so they stay crisp. Preserve the composition code, timing data, assets and dependency lock. An existing editor can replace this rendering route when the user chooses one, while keeping the same timing and delivery checks.

## Sync, effects and delivery

Separate vocals with Demucs; transcribe the vocal stem with Whisper or MLX Whisper; use librosa for onset and beat analysis. Reconcile those results with Suno's word timings where available. Follow [Sync](sync.md) rather than treating a transcript's timestamps as final captions.

Generate extra effects with [ElevenLabs Sound Effects](https://elevenlabs.io/docs/overview/capabilities/sound-effects) only when a cue needs them. Reuse suitable existing effects, anchor cues to the action or sung word, and keep them below the music.

Use FFmpeg for trims/fades, frame extraction, picture encoding and soundtrack muxing, and ffprobe for technical inspection. The included scripts make contact sheets, check exports and package silent demos. Follow [Sound and delivery](sound-and-delivery.md) for the final settings and handoff.
