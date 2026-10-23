---
name: release-notes-video
description: Make release-notes or weekly-update music videos using Suno, Gemini audio review, Dreamina/Seedance animation, Blender and a timed video composition. Use to plan an episode, write lyrics, compare takes, sync captions, build product demos, edit the video or prepare silent clips and a posting kit.
---

# Release notes music video

Make a video people want to watch that also makes the update unmistakable. The genre defines the music, visual world, typography and editing. Real demonstrations carry the explanation; the song and visual jokes make it memorable.

Use Suno for music, Gemini to compare recordings, OpenAI image generation for stills, Dreamina/Seedance for animation, Blender for 3D and camera control, Playwright with HTML Canvas for product capture and composition, Demucs/Whisper/librosa for sync, and FFmpeg for mixing and delivery. Add ElevenLabs effects when needed. Read [Tools and setup](references/tools.md) before production; it explains the handoffs and the Dreamina CLI workflow. If a tool is unavailable, explain the missing capability and agree on a substitute rather than silently dropping it.

## Establish the brief

Resolve the audience, deadline, target duration, intended display format, source notes, available tools and approver. Ask only about missing information that materially changes the work. Use existing choices and authorizations from the conversation.

- **Public release notes:** feature claims must be launched, available and verified for the intended audience. An implementation or merged change alone does not prove availability.
- **Internal all-hands:** planned work, experiments and metrics may be included if the user approves them for that audience and their status is explicit. Do not quietly turn plans into launches.
- **Format:** default to native 1080×1350, 4:5 for social. Confirm the display for an all-hands; 16:9 may be appropriate. The scaffold requires `--aspect` for internal episodes for this reason. Deliver one format unless more are requested.
- **Duration:** agree on a target. Around 60–90 seconds is a useful initial proposal for a public episode; internal updates may need a different length. Write for the chosen duration from the start.

Work in the user's own project directory, never inside this skill's directory. In commands, `<skill>` means the absolute path of this skill's directory. Create an episode folder with `python3 <skill>/scripts/new_episode.py <project>/episodes/<date>-<slug> --audience public --duration 60`, or use an existing project layout.

## Keep these invariants

- Use real product behavior with fictional or explicitly approved data. A production screenshot is not automatically suitable for an external service or public video.
- Keep credentials, session values, unpublished business details and personal reference media out of the distributed skill. Use the user's chosen accounts and authorized tools.
- Treat paid generation and publishing as distinct actions. Obtain any missing budget or publishing authorization, and reuse authorization already granted for the same scope. Approval of a song or video is not permission to publish it.
- Preserve locked lyrics and the selected song. Change them only when the user authorizes it. Artist references describe creative qualities; write original lyrics and melodies.
- Compare actual audio before judging a performance. Measurements, transcription and listening judgments are separate evidence.
- Every sung word appears in sync. One readable capability sentence explains each demonstrated feature; it does not repeat the lyric.
- Put the hook in the opening seconds. Use a recognizable problem or striking image, with enough context to know what the video is announcing.
- Characters and effects earn their screen time. Product shots show an action, useful result and evidence where relevant.
- Keep the distribution skill separate from episode data. Do not archive or publish the working directory wholesale.

## Run the production

Use the following sequence, adapting to the tools and approvals already available:

1. **Choose the story.** Verify the source window and status of each candidate. Favor one meaningful headline with supporting capabilities, or a small set of substantive updates. Present the proposed story for approval before locking it. Read [Brief and copy](references/brief-and-copy.md).
2. **Choose a musical world.** Pitch three distinct directions with a recognizable reference, precise sound, opening image, narrator and format joke. Let the user choose. Read [Genre and story](references/genre-and-story.md).
3. **Lock the lyrics.** Draft a short complete song with specific details, a memorable hook and jokes that serve the update. Show where each claim comes from. Resolve edits before generating a batch in Suno. Lyrics and take selection: [Song](references/song.md).
4. **Generate and compare takes.** With the authorized budget, use Suno to make meaningfully different arrangements and vocal approaches. Have the latest available audio-capable Gemini model compare the complete recordings together when access and permission allow it; without Gemini access, use another model that can hear several full recordings in one request. Verify availability rather than inventing a model name. The user's selection overrides the recommendation.
5. **Build timing data.** Retain the chosen original, record any trim/fade, align sung words and establish the beat grid. Read [Sync](references/sync.md).
6. **Plan and build the picture.** Storyboard the entire timeline before filling it with animation. Capture product demonstrations with Playwright, generate first-frame stills, and animate selected shots with Dreamina/Seedance. Use Blender for shots that need controlled 3D geometry or camera motion, either as final renders or motion references. Build the product explanation first, then add the genre world, approved characters and intentional visual absurdity. Read [Picture](references/picture.md).
7. **Mix, render and inspect.** Use quiet, purposeful sound effects. Check every cut, caption, reading hold and clip boundary, then export a full-quality review. Read [Sound and delivery](references/sound-and-delivery.md) and [QA](references/qa.md).
8. **Revise and deliver.** Address feedback without altering the locked song unnecessarily. After approval, promote the approved bytes to a stable final filename. Make standalone silent product demos and a posting kit if requested. Record the source inventory and verify the archive before cleanup.

Do not proceed past an unresolved story, genre, lyric or song decision that requires the user's choice. Once a decision is made, continue within the approved scope without asking again. Internal distribution and public posting remain separate choices.

## Optional utilities

All included scripts operate locally and require no service credentials:

| Script | Purpose |
|---|---|
| `scripts/new_episode.py` | Create an episode folder, brief and kit manifest |
| `scripts/inspect_media.py` | Report streams/dimensions/duration and validate a silent clip or expected export |
| `scripts/contact_sheet.py` | Make a timestamped contact sheet using FFmpeg and Pillow |
| `scripts/build_posting_kit.py` | Build an offline HTML kit and ZIP with original silent demo clips |

The helpers do not create the music or render the main video. Build the episode's composition with HTML Canvas and Playwright, then encode and mux with FFmpeg; use another editor when the user chooses it. Preserve the timing model and source assets so another agent can rebuild the episode.
