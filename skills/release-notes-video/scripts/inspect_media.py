"""Inspect an export with ffprobe; validate expected properties without changing it."""
import argparse
import json
from pathlib import Path
import subprocess


def inspect(path):
    data = json.loads(subprocess.check_output(
        ['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)], text=True, encoding='utf-8'))
    streams = data.get('streams', [])
    # Embedded cover art is reported as a video stream; it is not part of the picture.
    videos = [s for s in streams if s.get('codec_type') == 'video'
              and not s.get('disposition', {}).get('attached_pic')]
    audio = [s for s in streams if s.get('codec_type') == 'audio']
    if len(videos) != 1:
        raise ValueError('expected exactly one video stream')
    v = videos[0]
    raw_duration = data.get('format', {}).get('duration') or v.get('duration')
    if raw_duration is None:
        raise ValueError('media has no measurable duration')
    num, _, den = (v.get('avg_frame_rate') or '0/0').partition('/')
    fps = float(num) / float(den) if den and float(den) else None
    return {'path': str(path), 'duration_seconds': float(raw_duration), 'width': v['width'], 'height': v['height'],
            'codec': v['codec_name'], 'pixel_format': v.get('pix_fmt'), 'frame_rate': v.get('avg_frame_rate'),
            'fps': round(fps, 3) if fps else None,
            'frame_count': int(v['nb_frames']) if v.get('nb_frames', '').isdigit() else None,
            'audio_streams': len(audio), 'video_streams': len(videos)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file', type=Path)
    parser.add_argument('--silent', action='store_true')
    parser.add_argument('--duration', type=float)
    parser.add_argument('--width', type=int)
    parser.add_argument('--height', type=int)
    parser.add_argument('--codec')
    parser.add_argument('--fps', type=float)
    parser.add_argument('--pix-fmt', dest='pixel_format')
    args = parser.parse_args()
    try:
        result = inspect(args.file)
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f'Cannot inspect media: {exc}\n')
    errors = []
    if args.silent and result['audio_streams']:
        errors.append('silent clips must have zero audio streams')
    if args.duration is not None and abs(result['duration_seconds'] - args.duration) > .1:
        errors.append('duration differs from the expected value by more than 0.1 seconds')
    if args.fps is not None and (result['fps'] is None or abs(result['fps'] - args.fps) > .01):
        errors.append('frame rate does not match the expected value')
    for key in ['width', 'height', 'codec', 'pixel_format']:
        expected = getattr(args, key)
        if expected is not None and result[key] != expected:
            errors.append(f'{key} does not match the expected value')
    print(json.dumps({**result, 'errors': errors}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
