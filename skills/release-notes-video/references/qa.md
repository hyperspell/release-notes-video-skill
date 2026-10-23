# Quality checks

Report the actual evidence: rendered frames, measured metadata, transcription checks, audio-model judgments and human listening are different things. Do not claim to have watched or heard something from a prompt or a contact sheet alone.

## Picture and copy

- Inspect the first seconds at the intended viewing size. The audience should understand the frame and have a reason to stay.
- Inspect the cut list for gaps, overlaps and shots shorter than about 0.6 seconds. Check the render log for page or frame errors; every frame must render.
- Capture both sides of every cut, product action, source reveal, text entrance and final-card animation, and look at each still at the size it will play.
- Make a whole-video contact sheet every 2–2.5 seconds. `uv run --with pillow python3 <skill>/scripts/contact_sheet.py <video> <sheet.jpg>` samples actual exported frames.
- Run a flicker scan on the final video, not just the generated scene source: measure each frame's average brightness and inspect every large frame-to-frame jump. For example, `ffmpeg -i <video> -vf "signalstats,metadata=mode=print:key=lavfi.signalstats.YAVG:file=yavg.txt" -f null -` writes one brightness value per frame. A deliberate strobe on a montage cut is fine; a blip, a dip at a card, a 1–3-frame flash at a montage cut or a row of pulses over text is not.
- Run the included spatial detector too: `uv run --with numpy python3 <skill>/scripts/flicker.py <video> --output <report.json>`. Equal-brightness wrong-frame flashes can escape a brightness-only scan. Inspect the reported timestamps; hits are review candidates, not automatic failures.
- Check no mirror, kaleidoscope, swirl or hue-rotate effect is on footage, no overlay covers a face, cards open fully visible without a dip to black, and no generated badge is visible where it was meant to be cropped.
- Check text contrast, line breaks, containers, cursor targets, UI geometry and reading time. A five-second bubble should be fully readable for five seconds after its entrance.
- Ensure no source clip freezes accidentally, no face/cap is lost to the crop, and no unapproved likeness or real customer data appears.
- Count all sung words and inspect uncertain timings. Captions start with the sung word, not before it; check the lines transcription got early. Check repeated chorus lines are neither missing nor duplicated by two caption layers, no caption spills into the next shot, captions never overlap, and the caption text matches what the take actually sings.
- Confirm every product statement matches the approved brief and audience, and only available navigation is visible. Check fictional jokes do not imply a nonexistent feature. Search composed pages and shot code for real names, emails and customer names.
- Check the copy for counts, machine-sounding phrasing (brief-and-copy.md) and the period named the way the user asked.
- Confirm the final recap remains fully settled long enough to read.

## Sound and export

- Check pronounced product names and material lyric differences against the recordings.
- Measure loudness and true peak, and compare effect peaks with the song's level in the same span.
- Verify the selected take was only changed in the approved ways; if in doubt, compare the mix without effects against the take. Preserve its original and the working-mix hash.
- Check dimensions, frame rate, codec, duration and streams with `inspect_media.py`. A silent demo must have zero audio streams, even an empty one.
- Verify final duration against the planned end card and audio fade. Watch both ends and patch boundaries in the actual exported file.

## Posting kit

- Test every video player and Copy/Download control in the actual HTML page.
- Compare the downloaded MP4 bytes with the source, not only its name.
- Inspect desktop and narrow layouts. Avoid horizontal overflow and unreadably small video previews.
- Check that all source links and caveats are appropriate for the intended recipient.
- If cloud preview is blocked by authentication, distinguish file/readback checks from a visual inspection you could not perform.

## Review note

Send the full-quality review with a short note: what changed, one line per note addressed; what else QA found and fixed; how it was checked (stills at these times, contact sheets, the flicker scan); and what still needs the user's ears or eyes, for example "the drop shouts were placed by hand; please listen at 0:41". Record feedback in the private episode project. Preserve approved choices between rounds. When a note reveals a reusable lesson, add the lesson to the appropriate reference without importing the private discussion.
