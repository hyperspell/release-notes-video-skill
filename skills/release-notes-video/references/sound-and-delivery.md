# Sound and delivery

## Sound

Use ElevenLabs Sound Effects for new cues and FFmpeg for the mix and final mux. Reuse existing effects where they fit. Tool setup and the composition handoff are in [Tools and setup](tools.md).

Preserve the selected song. Apart from approved trim/fade, plain loudness gain and quiet effects, do not add processing without permission. Avoid silently repairing a mix with EQ, compression or a limiter; listeners notice ("did you do something to the audio?"). Pushing spoken verses up from the vocal stem can help on phone speakers, but offer it only as an A/B the user chooses.

Anchor effects to the action or sung word, the same way graphics are anchored, so sound and picture move together when the take changes. Keep a small reusable effects library and add genre-specific effects to it. Keep effects well below the song: reviewers repeatedly found them too loud, including a gag at −12 dB. A useful starting point is comic effects at −18 dB or lower relative to the song before any overall trim, with UI ticks and pops lower still. A quiet click may carry a product interaction better than another loud comic effect. Review the effect's peak against the same musical span; the gain value alone does not tell you whether it dominates.

For feed video, a useful starting target is about −14 LUFS integrated with true peak at or below −1 dBTP; feeds autoplay clips back to back, and a quieter clip sounds weaker than its neighbours. Use a plain gain capped by the peak ceiling. If the peak limit prevents reaching the loudness target, preserve dynamics and report that rather than adding a hidden limiter. Internal playback may need a different target agreed with the user.

Retain the source, working mix and edit recipe separately. Record trim start/end, fade start/duration, any effect cues and the applied gain.

Use `master_audio.py` for the gain-only delivery pass. It copies the picture, rejects mismatched ending durations and remeasures the encoded AAC. Commands are in [Production helpers](production-helpers.md).

## Export and review

Use native dimensions for the chosen frame, H.264 at about CRF 18, yuv420p and a constant frame rate agreed for the project; 24 fps is a useful default. Copy the rendered picture untouched when muxing the final audio. A high-quality review should be the same file that would be posted, not a low-resolution proxy; reviewers notice low-resolution clips. AAC at 256 kbps and MP4 faststart are reasonable distribution defaults. As a size reference, a two-minute 1080×1350 master came out at about 58 MB.

For social posting:

- A native 4:5 file takes roughly twice the phone screen area of 16:9 in most feeds.
- Upload the video natively rather than posting a link.
- Check the destination's current length limit when publishing is actually requested; some platforms cap non-premium accounts at about 140 seconds.
- A thumbnail with a face or an animal pulls attention.

Inspect the picture, soundtrack and final mux durations independently. A renderer using `-shortest` may trim a newly extended ending to an older working mix. A readable final recap needs matching picture and audio time; a silent tail is a creative choice to approve, not an unnoticed export bug.

Run `python3 <skill>/scripts/inspect_media.py <master.mp4> --duration <expected-seconds> --width <width> --height <height> --fps 24 --pix-fmt yuv420p` to check an export. The helper reports technical properties; it does not certify intelligibility or taste. Loudness is measured with FFmpeg's `ebur128` or equivalent available tools, separately from metadata inspection.

After the user approves a review, copy that exact file to a stable final name and compare hashes. Do not re-encode it merely to remove a review suffix.

## Standalone demos

When requested, make short silent demonstrations, typically six to nine seconds each. These are product explanations, not cropped music-video excerpts. Strip the audio stream entirely. Use ordinary fictional data and remove music-video-only jokes when they distract from the explanation; for example, show the product's real stock settings rather than a joke setting from the music video.

Show the product doing one useful thing, hold the update's plain feature sentence along the bottom, push in on the detail that proves the claim so it reads on a phone, and hold the result. Silent demos are usually 0.2–1.2 MB each. One release may have several capability demos. Do not describe them as distinct launches if they are not.

Render each standalone demo page with the included `render.mjs`; its output has no audio stream. See [Production helpers](production-helpers.md) for full and partial render commands.

## Portable posting kit

Use `python3 <skill>/scripts/build_posting_kit.py <kit.json> --output <delivery-directory>` with the manifest created by `new_episode.py`. Paths to clips are relative to the manifest. All clips must be inside the manifest's episode directory. Output must be outside those inputs.

The manifest has:

```json
{
  "title": "Weekly update",
  "main_post": "Our weekly update, in a song. Sound on.",
  "before_posting": ["Confirm the final audience and availability wording."],
  "items": [
    {
      "title": "A verified capability",
      "description": "What happens and why it matters.",
      "clip": "deliver/demos/example.mp4",
      "filename": "example-demo.mp4"
    }
  ]
}
```

Replace the invented example with approved copy and actual files. The builder checks that each clip is silent H.264 between 4 and about 9 seconds long, and that the embedded clips total at most 25 MiB. It produces:

- A self-contained HTML page with inline players, Copy controls and original MP4 downloads.
- A `demos/` directory containing the same original bytes and plain post copy.
- A ZIP containing that handoff.

The main music video travels separately. The page has no external hosting requirement and no provider-specific artifact API. If a cloud Page is also useful, use its real supported media blocks and uploaded file references. Do not invent playable URLs or put local paths into a cloud document.

Internal posting caveats belong only in a kit for the approved poster. A forwarding kit can expose that text even when viewers cannot see private source material. Test playback, copy payloads, filenames and downloaded bytes in a normal browser, including a narrow viewport. State clearly whether a shared file is local, hosted privately, or public. Leave publishing and sharing permissions unchanged unless the user asks.

## Archive

Keep code, generic templates and reusable instructions separate from episode media and organizational evidence. Store source recordings, alternatives worth keeping, generated originals, timing data, export recipes, final masters and posting kits in the user's chosen private archive.

Use a checksum manifest and preserve relative paths. Verify uploads by readback before moving scratch to the Trash. A restore guide should identify the selected take, active composition, required fonts/tools and commands needed to rebuild without historical review folders. Do not promise that re-encoding will reproduce identical compressed bytes; keep the approved final export too.

Use `asset_manifest.py` to inventory the archive and verify a downloaded/restored copy. For Drive, use the user's connected Drive tools or configured CLI and preserve the existing sharing settings. Skip unchanged files when resuming; retain changed assets as revisions where supported. Split archives to fit the actual upload limit, keeping packs independently extractable and preserving relative paths. Keep useful candidate songs and originals; omit regenerable frame dumps and draft renders. Record the remote file locations with the episode, and promote reusable sets/props only when authorized.

Promote reusable character/set assets only when their reuse is authorized. Keep private reference photos and team feedback out of a public skill export. Archive sharing and repository commits are separate from delivering the video and need the user's authorization.
