# Picture

## Storyboard the whole timeline

For every span, record the lyric, demonstrated capability, shot, action/result, supporting asset, intended transition and reading hold. Establish what the viewer should understand at the end of each product scene. Plan the actual product story before filling the chorus with characters.

Use three coordinated layers:

1. The real product behavior, with fictional or approved data. Every featured update gets a lyric that carries the joke, the product doing the thing on screen, and a plain feature sentence.
2. The genre's animated or live-action world, only where it earns its place.
3. Timed typography: every sung word designed into the shot (hook slams, stamps, chat messages, labels) or captioned, plus concise feature sentences and a final recap.

One point of attention per shot is usually enough. Do not stack an explanatory headline, subtitle, joke label, dense UI and full lyric paragraph. A character can be funny without becoming an unexplained narrator. Keep recurring characters only when the user approves their use and likeness.

Choose the narrator to fit the approved premise rather than forcing an existing mascot into every story. A recurring fictional company, cast and setting lets repeat viewers catch callbacks. Pace intensity like a dose curve: keep the intro sober, reach genre intensity at the first chorus and save the maximum for the final chorus.

Characters should be properly animated (a generated or animated clip per shot), not cutout sprites bouncing on the beat. Avoid a title card at the start and a title or progress meter on screen the whole time.

## The first seconds

Feeds count a view after about two to three seconds, so the frame must move from frame one. Establish the update's context and a recognizable problem before asking viewers to decode a mascot or an unfamiliar character.

The picture can carry the opening while the song keeps its intro. One opening that worked: a team chat flooding with messages, arriving faster and faster, the unread counter racing past 1,000, every message a small joke, until the product's arrival stops it all and the counter flips to the product's own "all caught up" state.

Most feed video autoplays muted, so add a headline line and a small "sound on" cue in the opening, for example "You weren't going to read our release notes. / So we made them a song." Never put a count in it; "we shipped six things" reads as not shipping much.

## Joke density

Some jokes will be niche to some viewers. The answer is density: enough jokes and easter eggs that everyone gets some, with subtlety allowed.

- **Layer the jokes** across the lyric, the picture, the fake UI copy, a running gag and a post-credits beat.
- **A running gag** pays off over four or five moments, so missing one does not matter. For example, a fictional coworker who promises to do something "by Friday", is quoted on an answer card, appears in a private note, gets a toast when they finally catch up, and returns in a post-credits notification asking what they missed.
- **Easter eggs live in the fake data:** a ticket titled "Make the agent stop saying 'You're absolutely right'", open for 47 days; a meeting called "Launch sync ('sounds good')"; "41 people, 3 of whom read the docs". Keep the demonstrated behavior accurate while the data is ridiculous.
- **Turn a flaw into a gag.** If the singer mangles a word, caption the mangled version with a deadpan footnote rather than hiding it.

## Make the product legible

- Prefer actual captures or source-faithful components. Conceptual imagery can explain the idea, but must not invent a product interface or behavior.
- Show an action and useful result. Keep the changed information in the same position so the viewer can compare it, make the click target visible and hold the result.
- If a claim has sources, show the claim and evidence together. If a tool reads a document, show enough of both to explain the relationship.
- Animate meaningful operations such as reordering. A cut between two nearly identical pages often hides what changed.
- Give the demo a useful scenario: show the work the product reads, what it produces and what changes when the work changes. Repeated visits should advance the example. A lone date or status field is weak filler if it does not change the story.
- Capture the actual product theme that reads best at the delivery size. Light UI often helps on a small social frame, but avoid restyling the application into an imaginary version.
- Keep fictional jokes coherent across views. Different briefings do not imply a permission boundary unless one actually exists.
- Keep application geometry stable across consecutive shots: the same window, size and position, with only the contents changing. Cutting from a lone sidebar to the full window made the sidebar jump in width and left a black band.
- Indicators, menus and text belong inside their real containers, where the real app puts them; a typing indicator goes under the composer, not under the window. Nothing overflows its container; check every list for overflow, wrapping and kerning.
- Draw borders on whole pixels and do not animate scale on hairlines, or window edges flicker.
- Captions sit on dark ground. White captions over a white UI are unreadable, so reframe to leave a dark band.
- Feature sentences never cover UI headers, title bars or labels. Move or retime them.
- The cursor does the action on the sung word: it clicks the button on the line that names the decision, and the button flips to its done state.
- When the product's own empty or success state is the payoff, use it rather than drawing a second copy on top.
- Push in on the detail that proves the claim so it reads on a phone.

To get pixel-faithful product pages with fake data, build them from the product's own component markup, class names and stylesheets, filled with fictional copy, rather than restyling screenshots. If you start from a saved copy of a live page, keep that raw snapshot private and out of version control, strip it to the chrome only (no names, emails, avatars or scripts), and search the result for `@`, real names and `<script` before it goes anywhere. Remove navigation for features that are not available to the video's audience.

Before sending any capture to an external tool, check the complete image, including browser chrome, avatars, sidebars and notifications. Keep raw captures in private local storage. Shared templates and examples must not contain hidden production text, identifiers or scripts.

## Text hierarchy

The lyric supplies the joke. A small feature bubble supplies one plain capability sentence. Start with roughly four to six words and at least five seconds fully readable; adjust after testing the actual layout. Entrance and exit animation do not count as reading time. Prefer fewer, longer-held bubbles to many short repeats; a bubble can carry across a cut if it stays clear of faces and still fits what is shown. Do not use large headings that merely repeat the sung line.

Use a readable caption face and a genre-appropriate display face; simplifying captions does not mean making them plain if the genre font reads well in short phrases. Build caption type into the shot rather than covering the product with an unrelated block. Use short phrases, deliberate line breaks and enough contrast. Inspect at phone size for social and from the back-of-room perspective for an all-hands.

Opening and closing branding should use the user's approved wordmark when available. A closing card can stagger complete feature lines quickly, then hold the fully settled list long enough to read. Title the recap without a number ("Sprint highlights", not "6 things we shipped") and use dots rather than a numbered list. End with a beat after the final button: let the end card hold over the outro groove, with a last small gag a few seconds after the final sung word.

## Visual effects: light, not distortion

- Build intensity with light: a zoom punch and exposure pump on the kick, coloured beams and bloom, a thin RGB fringe, and a strobe only on cuts.
- Never put mirror, kaleidoscope, swirl or hue-rotate effects on live-action or generated footage; they read as broken rather than energetic.
- Never pulse a wash or flash over text pages. A beat-synced colour wash on a recap reads as annoying flashing.
- Cuts into a card start fully visible. Do not dip to near-black.
- Cards pop in rather than fading in like a ghost.
- Draw lyrics, feature sentences and cards after the post-processing pass so text stays crisp.

## Animation and cinematography

Use OpenAI image generation for character references and first frames, Dreamina/Seedance for generated motion, and Blender for controlled 3D shots or clay camera references. The setup, job lifecycle and Blender rendering workflow are in [Tools and setup](tools.md). Capture product demonstrations with Playwright and compose exact text separately from generated footage.

Generate motion where it adds something a still cannot. Use approved source stills and consistent character references. Compose for the final aspect ratio before paying for clips. Match shot length to the source clip; a clip that runs out and freezes on its final frame is a bug.

Ask for the camera, action, framing, lighting and final composition in the prompt. Avoid generating important UI text in a model; render that text deterministically. A style line such as "No text, no captions, no subtitles, no speech, no singing, no lip-sync, no new logos" prevents most unwanted additions; add "no religious or occult symbols" to anything ritual-looking. Check hands, faces, props and logos for unintended changes.

- **Stills.** Edits tend to keep the input's camera angle. For a precise fix, mask one region per call and composite only that region back. If a large requested change (a whole outfit) does nothing, say that the change is required and must be clearly visible.
- **Clips.** Generate each clip from its own first-frame still, in parallel, rather than chaining one clip's last frame into the next. Use the full-quality model for finals; cheaper variants tend to drift faces, garble text and ad-lib dialogue. If a clip cannot be cropped to the final ratio without losing its subject, regenerate it in a portrait ratio rather than cropping. Lip-sync is a hero-shot tool, not a default.
- **Cost.** Inspect the current tool's resolution choices and price before quoting a batch. A lower-cost resolution can be appropriate for brief cutaways, with the higher one kept for hero shots; review the actual result at final size, because low-resolution clips look soft in a 1080-pixel master. Do not assume a historical credit rate or model identifier is still valid. Preserve job IDs and completed originals so an interrupted run can resume without regenerating paid work.

Use camera moves, editing and light to express the genre. Avoid accidental distortions, mirrored faces and melted objects. Intentional absurdity should have a clear gag or visual premise. A directed crowd pullback can be funny; a generic concert inserted everywhere is filler. Choose props and behavior that fit the genre; a logo and robots at a generic concert do not communicate a specific musical world.

Only remove or crop a generated badge when the provider's terms permit it; preserve any required attribution or disclosure. Keep hats, faces and important action within the safe crop.

## Editing

- Cut on meaningful beats, bars, phrases and actions, taking the cut list from the song's beat grid. A renderer should be deterministic in song time when practical.
- Flag shots shorter than about 0.6 seconds and any gaps or overlaps in the cut list.
- In a beat-cut montage, never switch clips within about 0.5 seconds of either end of the shot; a three-frame flash of the next clip right before a cut reads as a glitch. Inspect at least one frame before and after every cut.
- Put product reading ahead of beat decoration. Keep held text stable while the music continues.
- Render the delivery aspect ratio natively. Letterboxing a 16:9 cut into a phone feed filled less than half the screen. In a native 4:5 cut, UI fills the width, product pages are captured at a narrower viewport, captions wrap to two lines, hooks and long shouts shrink or split to fit, the recap is a single column, each clip's crop is placed by hand, and overlays stay off faces.
- Patch only changed spans when the pipeline supports it: render the span, splice its frames into the full render at the exact frame offset (start time × fps), re-encode and re-deliver. Inspect both sides of every patch.
- Music-video metadata can be a genre detail. Keep the visible bottom/right insets balanced, stay clear of captions, and use brief opening/closing appearances when that suits the format. Never invent actual label or artist affiliations.
