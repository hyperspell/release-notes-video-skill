"""Flag short visual blips, dark dips and brightness pulses in a constant-frame-rate video."""
import argparse
import json
import math
import subprocess
from pathlib import Path


def detect(frames, fps):
    import numpy as np

    if not math.isfinite(fps) or fps <= 0:
        raise ValueError('fps must be finite and positive')
    values = np.asarray(frames, dtype=np.float32)
    if len(values) < 3 or not np.isfinite(values).all():
        raise ValueError('at least three finite frames are required')
    values = values.reshape(len(values), -1)
    brightness = values.mean(axis=1)
    distance = lambda a, b: float(np.abs(values[a] - values[b]).mean())
    hits = []
    for i in range(1, len(values) - 1):
        for count in (1, 2, 3):
            j = i + count
            if j >= len(values):
                break
            if distance(i - 1, j) < .03 and distance(i - 1, i) > .08 and distance(j - 1, j) > .08:
                hits.append({'frame': i, 'time': i / fps, 'kind': 'blip', 'frames': count})
                break
    context = np.array([np.median(brightness[max(0, i - 12):i + 13]) for i in range(len(values))])
    for kind, mask, max_length in [('dip', (brightness < context / 3) & (context > .08), 6),
                                    ('pulse', brightness - context > .07, 4)]:
        indices = np.flatnonzero(mask)
        for run in np.split(indices, np.where(np.diff(indices) > 1)[0] + 1):
            if 0 < len(run) <= max_length:
                i = int(run[0])
                hits.append({'frame': i, 'time': i / fps, 'kind': kind, 'frames': len(run)})
    return sorted(hits, key=lambda hit: (hit['frame'], hit['kind']))


def scan(source, fps=None):
    import numpy as np

    if fps is None:
        result = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                                 '-show_entries', 'stream=avg_frame_rate', '-of', 'json', str(source)],
                                capture_output=True, text=True, check=True)
        numerator, denominator = json.loads(result.stdout)['streams'][0]['avg_frame_rate'].split('/')
        fps = float(numerator) / float(denominator)
    if not math.isfinite(fps) or fps <= 0:
        raise ValueError('invalid frame rate')
    result = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(source), '-vf',
                             f'fps={fps},scale=64:80,format=gray', '-f', 'rawvideo', '-'],
                            capture_output=True, check=True)
    frames = np.frombuffer(result.stdout, dtype=np.uint8).reshape(-1, 80, 64).astype(np.float32) / 255
    return {'fps': fps, 'frames': len(frames), 'hits': detect(frames, fps),
            'note': 'Inspect every hit; real cuts and intentional flashes may trigger this check.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('video', type=Path)
    parser.add_argument('--fps', type=float)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        result = scan(args.video, args.fps)
        text = json.dumps(result, indent=2) + '\n'
        if args.output:
            if args.output.resolve() == args.video.resolve():
                raise ValueError('report must not replace the source video')
            args.output.write_text(text, encoding='utf-8')
        print(text, end='')
    except (OSError, ValueError, KeyError, IndexError, ZeroDivisionError, subprocess.CalledProcessError) as error:
        parser.error(str(error))


if __name__ == '__main__':
    main()
