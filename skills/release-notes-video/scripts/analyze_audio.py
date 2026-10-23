"""Measure a constant-tempo beat grid or vocal onsets; requires librosa, NumPy and SoundFile."""
import argparse
import json
from pathlib import Path


def analyze(source, mode, beats_per_bar=4):
    import librosa
    import numpy as np

    y, sr = librosa.load(source, sr=22050, mono=True)
    if len(y) < sr or not np.isfinite(y).all() or np.max(np.abs(y)) < 1e-6:
        raise ValueError('audio must contain at least one second of finite, audible samples')
    duration = len(y) / sr
    if mode == 'vocals':
        hop = 220
        rms = librosa.feature.rms(y=y, hop_length=hop)[0]
        onsets = librosa.onset.onset_detect(y=y, sr=sr, hop_length=hop, units='time', backtrack=True)
        return {'duration': duration, 'rate': sr / hop,
                'db': np.maximum(-120, 20 * np.log10(np.maximum(rms, 1e-6))).tolist(),
                'onsets': sorted(set(float(t) for t in onsets))}

    _, frames = librosa.beat.beat_track(y=y, sr=sr)
    times = librosa.frames_to_time(frames, sr=sr)
    if len(times) < max(8, beats_per_bar * 2):
        raise ValueError('too few detected beats; use a longer musical span or place the grid manually')
    period, offset = np.polyfit(np.arange(len(times)), times, 1)
    if not np.isfinite(period) or period <= 0:
        raise ValueError('could not fit a positive beat period')
    residual = float(np.sqrt(np.mean((times - (period * np.arange(len(times)) + offset)) ** 2)))
    low = librosa.effects.preemphasis(y, coef=-0.97)
    strength = librosa.onset.onset_strength(y=low, sr=sr, hop_length=128, fmax=150)
    ot = librosa.frames_to_time(np.arange(len(strength)), sr=sr, hop_length=128)
    scores = []
    shifts = np.linspace(-period / 2, period / 2, 81)
    for shift in shifts:
        grid = np.arange(offset + shift, duration, period)
        scores.append(float(np.interp(grid[grid >= 0], ot, strength).sum()))
    offset = float((offset + shifts[int(np.argmax(scores))]) % period)
    beats = np.arange(offset, duration, period)
    chroma = librosa.feature.chroma_stft(y=y, sr=sr, hop_length=512)
    rms = librosa.feature.rms(y=y, hop_length=512)[0]
    ft = librosa.frames_to_time(np.arange(chroma.shape[1]), sr=sr, hop_length=512)
    colors, energy = [], []
    for a, b in zip(beats[:-1], beats[1:]):
        mask = (ft >= a) & (ft < b)
        colors.append(chroma[:, mask].mean(axis=1) if mask.any() else np.zeros(12))
        energy.append(float(rms[mask].mean()) if mask.any() else 0)
    changes = np.r_[0, np.linalg.norm(np.diff(colors, axis=0), axis=1)]
    jumps = np.r_[0, np.diff(20 * np.log10(np.array(energy) + 1e-9))]
    harmony = [float(changes[p::beats_per_bar].mean()) for p in range(beats_per_bar)]
    strongest = np.argsort(jumps)[-min(12, len(jumps)):]
    accents = [int(sum(i % beats_per_bar == p for i in strongest)) for p in range(beats_per_bar)]
    votes = [h / max(max(harmony), 1e-9) + e / max(max(accents), 1) for h, e in zip(harmony, accents)]
    phase = int(np.argmax(votes))
    return {'bpm': float(60 / period), 'period': float(period), 'offset': offset,
            'downbeat': float(offset + phase * period), 'beats_per_bar': beats_per_bar,
            'beats': beats.tolist(), 'duration': duration,
            'votes': {'harmony': harmony, 'energy': accents, 'selected_phase': phase,
                      'disagree': int(np.argmax(harmony)) != int(np.argmax(accents))},
            'fit_rms_seconds': residual}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['beats', 'vocals'])
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--beats-per-bar', type=int, default=4)
    args = parser.parse_args()
    if args.beats_per_bar < 2 or args.beats_per_bar > 12:
        parser.error('beats per bar must be between 2 and 12')
    if args.source.resolve() == args.output.resolve():
        parser.error('output must not replace the input audio')
    try:
        result = analyze(args.source, args.mode, args.beats_per_bar)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    except (ValueError, OSError) as error:
        parser.error(str(error))
    print(json.dumps({k: v for k, v in result.items() if k not in ('db', 'onsets', 'beats')}))


if __name__ == '__main__':
    main()
