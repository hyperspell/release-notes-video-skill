"""Copy a video's picture and mux a duration-matched WAV using measured plain gain only."""
import argparse
import json
import math
import re
import subprocess
import tempfile
from pathlib import Path


def run(arguments):
    return subprocess.run([str(value) for value in arguments], capture_output=True, text=True, check=True)


def duration(path):
    return float(run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path]).stdout)


def loudness(path, seconds):
    result = run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-t', seconds,
                  '-vn', '-af', 'ebur128=peak=true', '-f', 'null', '-'])
    summary = result.stderr[result.stderr.rfind('Summary:'):]
    integrated = re.search(r'I:\s+(-?[\d.]+) LUFS', summary)
    peak = re.search(r'Peak:\s+(-?[\d.]+) dBFS', summary)
    if not integrated or not peak:
        raise ValueError('could not measure finite audio loudness/true peak; check for silence or missing audio')
    return float(integrated[1]), float(peak[1])


def master(video, audio, output, target=-14, ceiling=-1, tolerance=.05):
    if not all(math.isfinite(n) for n in (target, ceiling, tolerance)) or tolerance <= 0:
        raise ValueError('targets and tolerance must be finite, with positive tolerance')
    if output.exists() or output.resolve() in (video.resolve(), audio.resolve()):
        raise ValueError('choose a new output file; inputs and existing masters are never overwritten')
    picture_duration, audio_duration = duration(video), duration(audio)
    if not math.isfinite(picture_duration + audio_duration) or picture_duration <= 0:
        raise ValueError('invalid input duration')
    if abs(picture_duration - audio_duration) > tolerance:
        raise ValueError(f'picture is {picture_duration:.3f}s but soundtrack is {audio_duration:.3f}s; match the intended ending first')
    integrated, peak = loudness(audio, picture_duration)
    gain = min(target - integrated, ceiling - peak)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent, prefix='master-') as temp:
        candidate = Path(temp) / 'candidate.mp4'
        for _ in range(4):
            run(['ffmpeg', '-y', '-v', 'error', '-i', video, '-i', audio,
                 '-map', '0:v:0', '-map', '1:a:0', '-t', picture_duration,
                 '-c:v', 'copy', '-af', f'volume={gain:.4f}dB', '-c:a', 'aac', '-b:a', '256k',
                 '-movflags', '+faststart', candidate])
            final_i, final_peak = loudness(candidate, picture_duration)
            if final_peak <= ceiling and final_i <= target + .1:
                break
            # AAC can raise true peak. Reduce plain gain and encode from the original WAV again.
            gain -= max(final_peak - ceiling, final_i - target, 0) + .1
        else:
            raise ValueError('could not meet the peak ceiling with plain gain; no final master written')
        if abs(duration(candidate) - picture_duration) > tolerance:
            raise ValueError('mux duration differs from the picture; no final master written')
        if output.exists():
            raise ValueError('output appeared during processing; choose a new filename')
        candidate.rename(output)
    return {'duration': picture_duration, 'source_lufs': integrated, 'source_true_peak': peak,
            'gain_db': gain, 'final_lufs': final_i, 'final_true_peak': final_peak,
            'target_lufs': target, 'peak_ceiling': ceiling,
            'target_limited_by_peak': final_i < target - .5, 'picture_stream_copied': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('video', type=Path)
    parser.add_argument('audio', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--target', type=float, default=-14)
    parser.add_argument('--ceiling', type=float, default=-1)
    parser.add_argument('--duration-tolerance', type=float, default=.05)
    args = parser.parse_args()
    try:
        print(json.dumps(master(args.video, args.audio, args.output, args.target, args.ceiling, args.duration_tolerance)))
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.error(str(error))


if __name__ == '__main__':
    main()
