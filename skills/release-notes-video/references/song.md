# Song and lyrics

## Write for the actual length

Choose a target duration before drafting. A short episode usually needs one or two compact verses, a repeatable hook and a decisive ending. Leave room for the opening context and a readable recap. Do not write a four-minute lyric sheet and assume the song can be invisibly cut into a minute: splices are audible and section replacements break the surrounding audio.

The sheet controls length far more than any duration control. As a rough observation with one generation service, a service-ready sheet (section cues included) sang at about 11–12 characters per second: about 1,000–1,300 characters for a 90–115 second song, about 650–700 for a minute, and about 2,900 for four minutes. Tempo and delivery move this, so measure your first take and adjust. End within a bar or two of the last line.

For a 90–115 second song, useful timing targets are the first vocal by about 6 seconds, the first update line by about 15 seconds and the hook by about 35 seconds. Compress them for shorter episodes. The picture carries the first seconds, not the song; do not write a cold-open gimmick such as a record scratch into the lyrics.

A shape that worked for a short episode: an intro that names the frame, a verse of updates, a stop where the beat cuts out and one question is asked, a chorus that answers it with crowd shouts, a second verse with the sincere turn, a final chorus with a key change, and a one-line deadpan outro that ends on a button word.

## Line rules

- **Topic and narrator.** The topic is obvious from the first two lines and every reference lands on one listen. Use one narrator in one world, talking to "you", with a specific attitude and a catchphrase.
- **Every line is an update, the hook, or a joke that carries an update.** Jokes ride inside the update lines, never instead of them. Do not spend the verses on a story that never announces anything.
- **Verses.** Spoken or deadpan couplets of about 10–13 syllables, one specific detail per line, rhyming. Check syllables with a CMU-dictionary counter such as the `pronouncing` package, then read the lines aloud for syllable piles and forced stresses.
- **The hook.** About 4–8 syllables, open vowels, a crowd shout back, syncopated where the beat stops. The stop or pre-chorus asks a question and the chorus answers it. A strong ending reuses a familiar product or workplace sentence with a new meaning (for example "You're all caught up" or "Mark all as read").
- **One sincere turn.** A single plain, earnest line about what the product now does for people gives the jokes something to land against.
- **Name the frame once.** The intro and outro say these are the release notes. Do not tag lines with "New:". Avoid naming a period that dates or undersells the update; "this month's" can sound slow where no period at all works.
- **No overpromising and no bragging.** The narrator states what the product does.
- **Sensitive topics reassure.** If the update touches privacy or permissions, make the boundary the punchline rather than a line that makes people imagine a leak.
- **Topical references are tied to an update and as broad as possible.** When a reviewer finds some jokes niche, the answer is density: enough jokes that everyone gets some (see picture.md).
- **Competitors.** At most one jab, unnamed or easy to cut.
- **Don't reuse earlier episodes' structural devices.** Callbacks are welcome as easter eggs.

Draft with a source note for every line (line, update, source, syllables), and show the user the complete sheet with a table of where each update lands. Expect several rounds. After the user locks lyrics, preserve them exactly except for approved pronunciation spellings. Save each version and the locked sheet in the private episode folder.

## Writing for Suno

Verify the current editor's behavior; these held for Suno in late 2026 and may apply to similar services:

- Section cues go in brackets with delivery notes, for example `[Verse 1 - spoken, deadpan, over the filtered loop]` or `[Stop - beat cuts out]`. Text in parentheses is sung, which makes parentheses the place for crowd shouts.
- Spell words the way they should be sung ("A-I", "three A-M", a hyphen in a compound the model mispronounces) and caption the actual spelling. Check generated pronunciation rather than trusting the prompt.
- Avoid shouts that can be misheard as profanity. A caption can steer the listener, but safer words are better.
- Screen every take for product names.
- A short hook may grow into a full chorus. Write the chorus out in full if that is what you want.

## Generate varied candidates

Use Suno Custom mode in the user's signed-in account: paste the locked lyrics, enter the style and exclude prompts, and keep instrumental mode off. See [Tools and setup](tools.md) for the production stack. Use another music service when the user chooses it. Confirm the allowed spend and number of candidates when they have not already been authorized. Check the service's terms on automated use; if they restrict it, the user drives the interface. Verify the current controls, export options and usage terms rather than promising that a particular plan or download grants a particular right. Budget downloads separately from generation when the service limits exports. Check commercial-use eligibility under the applicable plan and terms rather than treating download or subscription status as a universal licensing rule.

Make roughly four to six takes across two or three meaningfully different seeds when that fits the budget, for example two takes per seed. Vary arrangement, energy, production or vocal delivery within the approved direction. Small tempo, key or wording changes that produce essentially the same performance do not count as diversity. Apply feedback about arrangement, vocal delivery and emotional energy while keeping the locked lyrics.

Write the style seed as one paragraph covering:

- Genre, era production details and tempo.
- The verse key moving to a chorus key, and any key change for the final chorus.
- The arrangement and the vocal delivery for each section, including how the words stay clear.
- Stop-time gaps and transitions.
- Three or four mood words.

Leave artist and song names out when the service rejects them; describe the sound instead. Keep an exclude list of styles that would pull the take off course, and adapt it to the genre (a country episode cannot exclude country). An example seed and exclude list for a French-touch filter-house episode:

```
French touch filter house, 124 BPM, F minor verses lifting to A-flat major choruses, a warm late-90s Paris club sound with a crisp modern mix. Verses ride a filtered disco loop with a pumping sidechained bass, four-on-the-floor kick, open hats and a slowly opening low-pass filter; choruses burst wide open with funky chopped guitar stabs, bright vocoder harmonies doubling the lead and a sweeping string pad. Verses: deadpan, dry, close female spoken voice, a little smug, every word crisp. Choruses: euphoric sung female lead with open vowels, a crowd of coworkers shouting the questions back. Stop-time gaps where the beat drops out, filter builds into each chorus, a key change up for the final chorus. Sleek, futuristic, playful, a little unhinged.
```

```
rap, trap, rock guitar, lo-fi, male lead vocal, mumbled vocals, big room EDM, dubstep, country, acoustic
```

If a browser agent fills the lyric editor and it is a rich-text field, typed input is unreliable. Put the sheet on the clipboard, click the editor, select all and paste, then read the field back and compare its length with the sheet. Log every take with its identifier, seed, settings, length and verdict.

## Compare the recordings together

When authorized audio access is available, use the latest suitable audio-capable Gemini model to compare the complete candidates in one request. Without Gemini access, use another model that can hear several full recordings in one request. Verify the current model through the provider's official documentation and the account's available models. Do not hard-code a speculative model identifier.

Send stable take labels, the actual recordings, locked lyrics, target length, creative brief, reference qualities and the user's latest corrections. Use the recordings themselves, not titles, style prompts or transcripts. Ask for a ranking, one concrete strength and weakness per take, two finalists and a recommended winner. Evaluate opening impact, vocal character, energy, chorus memorability, joke delivery, pronunciation, lyric fidelity and the usable ending. Distinguish a removable instrumental tail from a cut that loses sung words.

Keep the review's prompt, model version and response in the private episode project. Attribute subjective listening judgments to that reviewer. Never present a model's timestamps as final caption sync. Do not infer audible quality from a file name, prompt or generated description. If comparative audio access is unavailable or not authorized, explain that and use human listening plus measurements.

Screen the shortlist locally as separate evidence:

1. Check the service's own word timings when it provides them: the key words and where the last line ends.
2. Split each shortlisted take's vocal and transcribe the stem with word timestamps:

   ```bash
   uv run --with demucs --with soundfile python -m demucs -n htdemucs --two-stems vocals -o stems take-a.wav
   uv run --with openai-whisper whisper stems/htdemucs/take-a/vocals.wav --model large-v3-turbo \
     --word_timestamps True --condition_on_previous_text False --language en \
     --initial_prompt "<the product names and unusual words>" --output_format json --output_dir stems/take-a
   ```

   Any equivalent stem separator or Whisper implementation works.
3. Compare the transcript with the sheet: the share of sheet words heard, the missed words with context (to tell a transcription slip from a real change) and where the singing ends.
4. For the final two, compare intelligibility on the stem and on the full mix (the full mix stands in for listeners), key-term confidence, chorus lift, and when the first update line lands and the last line ends.
5. Transcribe risky shouts on their own with no initial prompt, to hear what a stranger hears.

Send the user the top two alongside the audio-review ranking: a table of the numbers, the specific words to listen for, and your pick in one line. The user picks the take by ear. Do not overrule that choice because a model or a score ranked a different song first; a human's pick can differ from both.

## Editing and provenance

Use the service's supported export path, obtain the selected take at production quality (WAV where available), retain the original and record its take identifier, source, duration, trim point and any licensed-use information the user provides. Do not copy cookies or session values into shared notes or package them with the skill.

In Suno, use the song's Download menu and wait for the file to finish before navigating away. A browser's multiple-download prompt can stall the remaining candidates. Use the exported file rather than a player-stream URL. Copy required upload inputs into the browser tool's allowed workspace when its file picker cannot read the original location.

Prefer a clean trim and musical fade after the final sung line. Trim on a bar line about one bar after the last sung word and fade over that last bar, then update the timing data's duration to match:

```bash
ffmpeg -i song_full.wav -t <end-bar-seconds> -af "afade=t=out:st=<end-bar-seconds minus one bar>:d=<one bar>" song.wav
```

Do not splice syllables, make abrupt mid-song cuts or silently EQ/compress/limit an approved mix. If an alternative vocal balance or mastering treatment would help, offer an explicit comparison before changing it.

If a take is far too long or needs restructuring, these failed in practice: replacing a section (it regenerates the wrong span and changes the audio around it), cutting instrumental passages on matched bars (listeners hear the joins immediately) and re-covering a spliced guide (it reproduces the seams). What worked was a cover or remix of the original take with a new, tighter lyric sheet, the original style pre-filled and low audio influence, around 25%; at 50% the take followed the new lyrics worse. Covers may ignore the duration control and add a long instrumental tail, which you then trim as above. Get approval before spending on this, and inspect the result rather than assuming the service preserved the original.

If one word comes out wrong, prefer, in order: live with it and caption it correctly; turn it into an on-screen gag; regenerate the whole take as a cover with the fixed spelling.
