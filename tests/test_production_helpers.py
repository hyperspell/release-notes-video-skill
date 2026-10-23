"""Synthetic checks for restored timing, render-quality, mastering and archive helpers."""
import importlib.util
import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / 'skills/release-notes-video/scripts'


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(*arguments, check=True):
    return subprocess.run([str(value) for value in arguments], capture_output=True, text=True, check=check)


class AlignmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load('align_lyrics')

    def test_repeats_crowd_and_independent_evidence(self):
        words = [{'word': word, 'start': i + .1, 'end': i + .7}
                 for i, word in enumerate(['Please', 'stay', 'Please', 'stay'])]
        service = [{**word, 'start': word['start'] + .4, 'end': word['end'] + .4} for word in words]
        timing, report = self.module.align('[Verse]\nPlease stay\n[Chorus]\n(Please stay)', words, service, 5)
        self.assertTrue(report['gate_passed'])
        self.assertEqual(len(report['discrepancies_over_250ms']), 4)
        self.assertTrue(all(word['crowd'] for word in timing['lines'][1]['words']))
        self.assertEqual(timing['lines'][1]['words'][0]['transcript_start'], 2.1)
        self.assertEqual(timing['lines'][1]['words'][0]['start'], 2.5)

    def test_snap_preserves_close_words_and_short_intervals(self):
        evidence = [{'word': 'stay', 'start': .95, 'end': .98},
                    {'word': 'here', 'start': 1.1, 'end': 1.4}]
        envelope = {'rate': 100, 'db': [-10] * 300, 'onsets': [1.0]}
        timing, report = self.module.align('stay here', evidence, evidence, 3, envelope)
        words = timing['lines'][0]['words']
        self.assertEqual(words[0]['start'], .95)
        self.assertGreater(words[1]['start'], words[0]['start'])
        self.assertTrue(report['gate_passed'])
        evidence[0].update(start=1, end=1.05)
        timing, _ = self.module.align('stay here', evidence, evidence, 3, envelope)
        self.assertEqual(timing['lines'][0]['words'][1]['start'], 1.1)

    def test_unmatched_words_are_not_silently_measured(self):
        evidence = [{'word': 'Please', 'start': .1, 'end': .3}, {'word': 'stay', 'start': 1.2, 'end': 1.5}]
        timing, report = self.module.align('Please just stay', evidence, [], 2)
        self.assertFalse(report['gate_passed'])
        self.assertEqual(report['unresolved'], [{'index': 1, 'text': 'just'}])
        self.assertEqual(timing['lines'][0]['words'][1]['source'], 'interpolated')
        timing, report = self.module.align('Please just stay', evidence, [], 2,
            overrides={'words': {'1': {'start': .6, 'end': 1}}})
        self.assertTrue(report['gate_passed'])
        self.assertEqual(timing['lines'][0]['words'][1]['source'], 'manual')

    def test_stale_service_and_bad_override(self):
        heard = [{'word': 'Please', 'start': 1, 'end': 1.5}]
        stale = [{'word': 'Please', 'start': 5, 'end': 5.5}]
        timing, report = self.module.align('Please', heard, stale, 6)
        self.assertEqual(timing['lines'][0]['words'][0]['start'], 1)
        self.assertEqual(len(report['service_rejected_over_3s']), 1)
        with self.assertRaises(ValueError):
            self.module.align('Please', heard, [], 6, overrides={'words': {'0': {'start': 2, 'end': 7}}})

    def test_cli_gate_writes_report_without_lyrics(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'sung.txt').write_text('Please just stay', encoding='utf-8')
            (root / 'words.json').write_text(json.dumps([{'word': 'Please', 'start': .1, 'end': .4}]))
            result = run(sys.executable, SCRIPTS / 'align_lyrics.py', '--sheet', root / 'sung.txt',
                         '--transcript', root / 'words.json', '--duration', 3, '--output', root / 'out', check=False)
            self.assertEqual(result.returncode, 1)
            self.assertTrue((root / 'out/alignment-report.json').exists())
            self.assertFalse((root / 'out/lyrics.json').exists())


class SignalTests(unittest.TestCase):
    def test_equal_brightness_wrong_image_flash(self):
        import numpy as np
        module = load('flicker')
        base = np.array([[.2, .8], [.8, .2]], dtype=np.float32)
        frames = np.repeat(base[None, :, :], 48, axis=0)
        frames[24] = 1 - base
        hits = module.detect(frames, 24)
        self.assertTrue(any(hit['kind'] == 'blip' and hit['frame'] == 24 for hit in hits))
        self.assertFalse(any(hit['kind'] in ('dip', 'pulse') for hit in hits))
        self.assertEqual(module.detect(np.repeat(base[None, :, :], 48, axis=0), 24), [])

    def test_click_track_and_silence(self):
        import numpy as np
        import soundfile as sf
        module = load('analyze_audio')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sr = 22050
            y = np.zeros(sr * 16)
            for index in range(32):
                start = int((index * .5 + .1) * sr)
                time = np.arange(1100) / sr
                y[start:start + 1100] += np.sin(2 * np.pi * 100 * time) * np.exp(-time * 90) * .7
            sf.write(root / 'click.wav', y, sr)
            beats = module.analyze(root / 'click.wav', 'beats')
            self.assertLess(abs(beats['bpm'] - 120), 4)
            self.assertLess(beats['fit_rms_seconds'], .06)
            vocals = module.analyze(root / 'click.wav', 'vocals')
            self.assertGreater(len(vocals['onsets']), 20)
            self.assertTrue(all(math.isfinite(value) for value in vocals['db']))
            sf.write(root / 'silent.wav', np.zeros(sr * 2), sr)
            with self.assertRaises(ValueError):
                module.analyze(root / 'silent.wav', 'beats')


class MediaAndArchiveTests(unittest.TestCase):
    def test_master_copies_picture_and_rejects_short_audio(self):
        module = load('master_audio')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            video, audio, output = (root / name for name in ('picture.mp4', 'song.wav', 'master.mp4'))
            run('ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'color=c=blue:s=64x80:r=24:d=3',
                '-an', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', video)
            run('ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'sine=frequency=440:duration=3', audio)
            result = module.master(video, audio, output)
            self.assertLessEqual(result['final_true_peak'], -1)
            def picture_hash(path):
                return run('ffmpeg', '-v', 'error', '-i', path, '-map', '0:v:0', '-c', 'copy', '-f', 'hash', '-').stdout
            self.assertEqual(picture_hash(video), picture_hash(output))
            self.assertLess(abs(module.duration(output) - 3), .05)
            self.assertTrue(load('flicker').scan(output)['frames'] >= 72)
            short = root / 'short.wav'
            run('ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'sine=duration=2', short)
            with self.assertRaises(ValueError):
                module.master(video, short, root / 'bad.mp4')
            self.assertFalse((root / 'bad.mp4').exists())

    def test_archive_readback_and_tampering(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'original.wav').write_bytes(b'original recording')
            (root / 'build').mkdir()
            (root / 'build/frame.png').write_bytes(b'regenerable')
            manifest = root / 'archive.json'
            run(sys.executable, SCRIPTS / 'asset_manifest.py', 'create', root, manifest, '--exclude', 'build')
            self.assertEqual(len(json.loads(manifest.read_text())['files']), 1)
            run(sys.executable, SCRIPTS / 'asset_manifest.py', 'verify', root, manifest)
            (root / 'original.wav').write_bytes(b'tampered')
            failed = run(sys.executable, SCRIPTS / 'asset_manifest.py', 'verify', root, manifest, check=False)
            self.assertNotEqual(failed.returncode, 0)


if __name__ == '__main__':
    unittest.main()
