# Sync

Use song time as the common clock for captions, product actions, animation, sound effects and cuts. A caption timeline is data; it should not be a second, manually drifting edit.

Use the included `analyze_audio.py` and `align_lyrics.py` to produce inspectable timing data and a report that distinguishes measured words from interpolation. Commands, evidence schemas and overrides are in [Production helpers](production-helpers.md). The alignment gate fails until unresolved words are addressed; a complete-looking JSON file is not proof of accurate sync.

## Establish the timing data

1. Retain the selected original and make the approved working trim/fade.
2. Separate a vocal stem if the available tools support it. Transcribe that stem, never the full mix, with word timestamps (commands in song.md). Full-mix transcription hangs a line's first word on the tail of the previous phrase; in one episode it put line starts up to 2.4 seconds early. Turn off conditioning on previous text and give an initial prompt containing the product names and unusual words.
3. Obtain the music service's word timings when it offers them. Some services show per-word timings for a take in their interface or account data; use only the access the service and its terms allow, and do not depend on copying a browser session token. These timings are usually accurate for a normal sung take, but crowd and shout runs can collapse to about 10 ms a word, and timings for a replaced section may still be aligned to the old sheet.
4. Write the text the take actually sings, including repeats and altered words, in the sheet's spelling. Keep the section headers and mark crowd words (for example in parentheses) so they render as shout pills or chat bubbles rather than captions. Compare it with the locked sheet and flag material changes.
5. Build a beat grid from the music: a constant-tempo fit phased on low-frequency onsets, so beats land on the kick rather than the hats. Estimate the bar phase two ways (for example from harmonic change and from energy). If they disagree, take the phase where the sections start on bar lines. A plausible tempo is insufficient if the downbeat is on beat 2.
6. Measure vocal onsets and a loudness envelope on the stem.
7. Reconcile alignment, transcription and vocal onsets, then run a lyric gate: report how many sheet words have a time and list every interpolated word. Check each interpolated word against the envelope, and list the lines where transcription and the service's timings disagree by more than about 0.25 seconds.

Tools such as Demucs, Whisper, librosa or an available forced aligner can help. Choose the current supported implementation for the host. Alignment exports and transcription are evidence to inspect, not automatically correct caption timing.

## Timing rules that worked

- **Snap word starts to the stem's onsets.** Take the service's or aligner's start and snap it to a vocal onset within about −0.2 to +0.05 seconds. Aligners tend to mark the vowel; the eye wants the consonant.
- **End a word when the stem drops away,** for example below about −42 dB for 0.15 seconds.
- **Place collapsed shout runs by hand.** Read the stem's loudness envelope over the span, find each shout's burst and record the times as explicit overrides. Tell the reviewer which spots were hand-placed so they check them by ear.
- **Transcription QA is per clip.** Never transcribe a whole video to check it; Whisper hallucinates loops and closing phrases such as "thank you for watching".

## Portable timing structure

Store a simple inspectable representation in the episode project, for example:

```json
{
  "fps": 24,
  "duration": 60,
  "beats": {"bpm": 120, "offset": 0.1},
  "lines": [
    {
      "id": "verse-1-line-1",
      "text": "Here is the weekly update.",
      "words": [
        {"text": "Here", "start": 1.0, "end": 1.2},
        {"text": "is", "start": 1.2, "end": 1.3},
        {"text": "the", "start": 1.3, "end": 1.4},
        {"text": "weekly", "start": 1.4, "end": 1.7},
        {"text": "update.", "start": 1.7, "end": 2.1}
      ]
    }
  ]
}
```

This is an illustrative composition structure. The alignment helper's actual output contract is documented in [Production helpers](production-helpers.md); adapt that data explicitly to the episode's composition. Keep overrides explicit and preserve their reasons. Count the sung words and account for every one; do not fill missing alignment with an invisible guess.

## Caption behavior

- Start near the audible consonant. Check uncertain words with a waveform or onset envelope and listening.
- End after the phrase lands, before the next phrase collides with it. Compute the desired end as `max(last word end + 0.3 s, line end + hold)`, then cap the entire result at `next line start − 0.28 s`. The next-line limit must be outside the `max`; otherwise the last word's minimum hold can override it. Count any exit fade inside that capped interval. With no following line, cap at the final video duration. If the cap would fall before the current line starts, flag overlapping or invalid timing instead of creating a negative-length caption; use a deliberate separate treatment for overlapping voices.
- Break long lines into short readable phrases; a 4:5 frame usually needs two-line captions.
- Declare which shot owns a lyric so it is not drawn twice by both a custom title and a global caption layer. Apply the ownership to every shot the line starts in, or a typeset line can spill into the next shot as a caption.
- Hang graphics off sung words, never fixed offsets: look lines up by their first words and words by their text, and anchor clicks, reveals and sound effects to them. Replacing the selected song should then move everything with it instead of requiring every time to be guessed again.
- Show crowd questions word by word as they are sung.
- Validate nonnegative, ordered word intervals within the final duration, and inspect both sides of shot boundaries.

If the outro is extended for reading time, update the final picture duration and matching audio mix deliberately. An old timing-file duration must not silently shorten the final mux.
