# Brief and copy

## Find the update worth singing about

Record the reporting window and where the facts came from. Use the user's authorized sources: release notes, current code/specifications, issue trackers, shipped documentation or a team-approved update. Read current evidence rather than relying on a stale local checkout or a summary that calls every item new.

For each proposed item, record:

| Field | What to establish |
|---|---|
| Change | What a viewer can now do or understand |
| Status | Launched, limited rollout, planned, experiment or internal-only |
| Evidence | A source the producer can inspect |
| Audience | Who can use it or is allowed to hear about it |
| Demonstration | The action and result the video can actually show |
| Caveat | Any limitation that materially changes the claim |

Keep source URLs and internal evidence in the private episode project. They do not belong in the reusable skill or public posting kit.

Set the window explicitly, from the previous episode's cutoff to now, and write it at the top of the brief; a wrong cutoff silently moves whole groups of changes in or out. With a large window, cluster merged changes and completed tickets into stories rather than listing them. Check every "new" claim in a summary or digest against its actual ship date.

For public release notes, verify availability separately from implementation: check feature flags and rollout percentages in every region or environment (a flag can be fully on in one region and off in another), per-account settings, admin-only or opt-in surfaces, account tier, permissions and published documentation where relevant. Record region caveats and whether public documentation exists yet, because posts cannot point people at docs that do not exist. Describe a limited rollout as limited; do not imply general availability when the intended audience cannot use it. For an internal all-hands, distinguish accomplishments from plans and keep any confidential metrics within the approved audience.

One substantial release can carry an entire short episode. Several demonstrations of it are capabilities of that release, not several invented launches. Choose the story because a viewer would care, not because a change has a recent timestamp.

For a public episode, choose stories with meaningful customer impact:

- **Expected capabilities.** Explain the useful change rather than presenting baseline functionality as a breakthrough.
- **Before-and-after claims.** Describe both accurately. Do not exaggerate earlier limitations or make customer difficulties the punchline.
- **Routine fixes, maintenance and renames.** Keep these in the written changelog unless their customer impact makes them a strong story.
- **Internal rebuilds and API restrictions.** Include only when the audience needs to understand a material change in behavior.
- **Security and incidents.** Follow the organization's approved communication process. A playful music video is not a substitute for an accurate advisory or customer notice, and a private incident is not a punchline.
- **Positioning presented as a release.** The company pitch is not something that shipped.
- **Unlaunched work.** Do not present it as available. Name rollout limits when announcing a launched beta or limited release.

The lyrics can still joke about smaller things in passing, but the feature sentences and the recap list only the chosen updates. Internal operational work may be worth celebrating in an all-hands when the audience understands why it matters.

## No counts

Do not say "six things shipped", "03/06" or number the recap. A count reads as "only six". Use a title such as "Sprint highlights" or "Shipped this week", or whatever period the user names.

## Copy the viewer understands immediately

Give each demonstration one short, complete sentence: who does what, and what changes. Examples with invented product names:

- “See the evidence behind each answer.”
- “Choose what goes in your briefing.”
- “Give each team a useful view.”

These are copy examples, not claims about a particular product. Replace them with verified behavior.

The lyric may contain a metaphor; the feature sentence explains the concrete capability. The joke sings and the sentence explains. Avoid a second headline that merely restates the sung words. Put jokes in the fictional data while keeping the demonstrated behavior accurate. Wrap long sentences to two lines.

Avoid the phrasing that makes copy sound machine-written:

- "seamless(ly)", "effortless(ly)", "empower", "unlock", "supercharge", "game-changer"
- "not X but Y" and "it's not just X, it's Y"
- groups of three for rhythm
- em dashes
- colon-headline taglines
- invented compound terms
- hedges
- self-congratulation ("we're proud to…")
- a "New:" label on every item

Where the product has its own words (button labels, status text, feature names), use them.

Product comparisons must not imply access restrictions, automation, real-time behavior or new interfaces that have not been verified. If the screen is an illustrative assembly, make its relationship to the actual product clear.

## Fact-check the exact words

After the lyrics and feature sentences are drafted, run a second check on the exact sentences that will appear on screen and in posts, ideally by a separate reviewer or subagent with only the sentences and the sources. Ask it to flag anything wrong, citing specification or documentation paths. In practice this catches errors in your own copy and in reviewers' suggested rewrites: a "private message" that is actually a reply visible only to the asker, a rule that sounds automatic when every match waits for a person, two separate integrations described as one, or custom-sounding settings that are really stock options.

## Post copy

When the video is posted with replies per update:

- **Main post:** one line plus a sound cue, for example "We put this sprint's release notes in a song. Sound on 🔊".
- **One reply per update:** the plain feature name as a header; two or three sentences covering what it does, who sets it up or can use it, and what stays private; then a short silent demo clip.
- **Before-posting caveats for the poster:** region availability, missing docs, staged rollouts and anything the music video jokes about that a demo should not show.

## Review before production

Present the proposed story, claims, intended audience and demonstration plan for approval. When the evidence is uncertain, identify the exact uncertainty rather than writing around it. Keep a brief feedback log in the private episode project; when updating the shared skill, retain the lesson without the conversation transcript or personal attribution.
