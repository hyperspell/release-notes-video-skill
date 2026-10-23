# Release notes, but make them a music video

An agent skill for turning release notes or a weekly all-hands update into a music video. Created by **Hyperspell**.

Pick a story and a musical direction, write the song, then build the video around it. The skill guides your agent through that process, including product demos and a posting kit with downloadable clips and copy.

## Start here

Give your agent [the skill](skills/release-notes-video/SKILL.md), your update notes and your intended audience. For example:

> Use the release-notes-video skill to make a 60-second music video for our weekly all-hands. Our notes are attached. Start by choosing the stories and pitching three musical directions. Ask before spending money on generation.

You can point your agent directly at the skill file, or install it by copying the whole `skills/release-notes-video/` directory into your agent's skills folder. Keep the references and scripts with it.

## What you need

- An agent with file access and tools for making and editing media.
- Your update notes, product visuals and any brand assets you want to use.
- A music-generation service or an original recording.
- A video editor or renderer. This repo provides instructions and helper scripts; you'll need your own editing tools.

The optional scripts need Python 3.10+ and FFmpeg/ffprobe. Contact sheets also need Pillow; the examples below use [uv](https://docs.astral.sh/uv/) to supply it. If you've installed Pillow yourself, omit `uv run --with pillow`.

## Included utilities

Run these from your video project directory to keep episode files separate from the skill. Set `SKILL` to the path of your installed or cloned skill directory:

```bash
SKILL=path/to/release-notes-video
python3 "$SKILL/scripts/new_episode.py" episodes/sample-week --audience internal --aspect 16:9 --duration 60
python3 "$SKILL/scripts/inspect_media.py" episodes/sample-week/deliver/master.mp4 --duration 60
uv run --with pillow python3 "$SKILL/scripts/contact_sheet.py" episodes/sample-week/deliver/master.mp4 episodes/sample-week/qa/contact.jpg
python3 "$SKILL/scripts/build_posting_kit.py" episodes/sample-week/kit.json --output episodes/sample-week/deliver/posting-kit
```

`new_episode.py` sets up the episode folders and planning files. Fill in `kit.json` with your clips and copy, then use `build_posting_kit.py` to package them as an offline HTML page and a ZIP. The page includes Copy and Download buttons.

To check the helper scripts, run `uv run --with pillow python3 -m unittest discover -s tests` from the repository root.

## For public feeds and internal all-hands

Social videos default to 1080×1350 (4:5). For an all-hands presentation, use the format that fits your screen, usually 1920×1080 (16:9).

Public release notes cover features people can use now. Internal updates can include plans and experiments, clearly labeled.

## Attribution

Please credit Hyperspell when publishing work made with this skill.

Released under the [MIT License](LICENSE).
