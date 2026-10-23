"""Local end-to-end checks using synthetic media; no accounts or external services."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'skills/release-notes-video/scripts'
sys.path.insert(0, str(SCRIPTS))
from build_posting_kit import build
from inspect_media import inspect


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'FFmpeg and ffprobe are required')
class HelpersTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.base = Path(cls.temp.name)
        cls.video = cls.base / 'silent.mp4'
        cls.audio_video = cls.base / 'with-audio.mp4'
        subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'testsrc2=size=160x200:rate=24',
                        '-t', '4', '-an', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', str(cls.video)], check=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-i', str(cls.video), '-f', 'lavfi', '-i', 'sine=frequency=440',
                        '-t', '4', '-c:v', 'copy', '-c:a', 'aac', str(cls.audio_video)], check=True)
        cls.cover_video = cls.base / 'with-cover.mp4'
        cover = cls.base / 'cover.png'
        subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'color=red:size=64x64', '-frames:v', '1',
                        str(cover)], check=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-i', str(cls.video), '-i', str(cover), '-map', '0', '-map', '1',
                        '-c:v:0', 'copy', '-c:v:1', 'png', '-disposition:v:1', 'attached_pic',
                        str(cls.cover_video)], check=True)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def episode(self, name):
        target = self.base / name
        subprocess.run([sys.executable, str(SCRIPTS / 'new_episode.py'), str(target),
                        '--audience', 'internal', '--aspect', '16:9', '--duration', '60'],
                       check=True, capture_output=True)
        return target

    def test_internal_episode_requires_confirmed_aspect(self):
        target = self.base / 'no-aspect'
        result = subprocess.run([sys.executable, str(SCRIPTS / 'new_episode.py'), str(target),
                                 '--audience', 'internal'], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('--aspect', result.stderr)
        self.assertFalse(target.exists())

    def test_scaffold_format_and_existing_directory(self):
        ep = self.episode('scaffold')
        data = json.loads((ep / 'project.json').read_text(encoding='utf-8'))
        self.assertEqual((data['width'], data['height']), (1920, 1080))
        self.assertFalse(data['publishing_authorized'])
        before = (ep / 'project.json').read_bytes()
        result = subprocess.run([sys.executable, str(SCRIPTS / 'new_episode.py'), str(ep),
                                 '--audience', 'public'], capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(before, (ep / 'project.json').read_bytes())

    def test_media_validation_distinguishes_audio(self):
        self.assertEqual(inspect(self.video)['audio_streams'], 0)
        self.assertEqual(inspect(self.audio_video)['audio_streams'], 1)
        for path, expected in [(self.video, 0), (self.audio_video, 1)]:
            result = subprocess.run([sys.executable, str(SCRIPTS / 'inspect_media.py'), str(path),
                                     '--silent', '--duration', '4', '--width', '160'], capture_output=True)
            self.assertEqual(result.returncode, expected)

    def test_media_validation_ignores_cover_art_and_checks_fps(self):
        info = inspect(self.cover_video)
        self.assertEqual((info['video_streams'], info['width'], info['fps']), (1, 160, 24))
        for fps, expected in [('24', 0), ('30', 1)]:
            result = subprocess.run([sys.executable, str(SCRIPTS / 'inspect_media.py'), str(self.cover_video),
                                     '--fps', fps, '--pix-fmt', 'yuv420p'], capture_output=True)
            self.assertEqual(result.returncode, expected)

    def test_posting_kit_names_missing_clip(self):
        ep = self.episode('missing')
        with self.assertRaisesRegex(ValueError, 'not found: deliver/demos/example.mp4'):
            build(ep / 'kit.json', ep / 'deliver/kit')
        self.assertFalse((ep / 'deliver/kit').exists())

    def test_posting_kit_preserves_clips_and_escapes_text(self):
        ep = self.episode('kit')
        source = ep / 'deliver/demos/example.mp4'
        shutil.copyfile(self.video, source)
        data = json.loads((ep / 'kit.json').read_text(encoding='utf-8'))
        data['items'][0]['title'] = '</script><p>Literal café 🎵 text</p>'
        data['producer_notes'] = 'Not part of the handoff'
        data['items'][0]['internal_source'] = 'Not part of the handoff either'
        (ep / 'kit.json').write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
        output = ep / 'deliver/kit'
        result = build(ep / 'kit.json', output)
        self.assertEqual(result['clips'][0]['bytes'], source.stat().st_size)
        html = (output / 'posting-kit.html').read_text(encoding='utf-8')
        payload = html.split('<script id="payload" type="application/json">')[1].split('</script>')[0]
        self.assertEqual(json.loads(payload)['items'][0]['title'], data['items'][0]['title'])
        self.assertNotIn('</script><p>', payload)
        self.assertNotIn('producer_notes', payload)
        self.assertNotIn('internal_source', payload)
        self.assertNotIn('deliver/demos', payload)
        with zipfile.ZipFile(output / 'posting-kit.zip') as archive:
            self.assertIsNone(archive.testzip())
            self.assertEqual(archive.read('demos/example-demo.mp4'), source.read_bytes())
            self.assertEqual(set(archive.namelist()), {'posting-kit.html', 'post-copy.txt', 'manifest.json',
                                                       'README.txt', 'demos/example-demo.mp4'})
        with self.assertRaises(ValueError):
            build(ep / 'kit.json', output)

    def test_invalid_and_external_clips_are_rejected(self):
        ep = self.episode('invalid')
        source = ep / 'deliver/demos/example.mp4'
        shutil.copyfile(self.audio_video, source)
        with self.assertRaises(ValueError):
            build(ep / 'kit.json', ep / 'deliver/invalid')
        data = json.loads((ep / 'kit.json').read_text(encoding='utf-8'))
        data['items'][0]['clip'] = str(self.video)
        (ep / 'kit.json').write_text(json.dumps(data), encoding='utf-8')
        with self.assertRaises(ValueError):
            build(ep / 'kit.json', ep / 'deliver/external')

    @unittest.skipUnless(importlib.util.find_spec('PIL'), 'Pillow is required for contact sheets')
    def test_portrait_contact_sheet_uses_correct_height(self):
        from PIL import Image
        output = self.base / 'contact.jpg'
        subprocess.run([sys.executable, str(SCRIPTS / 'contact_sheet.py'), str(self.video), str(output),
                        '--interval', '2', '--width', '160', '--columns', '2'], check=True, capture_output=True)
        with Image.open(output) as image:
            self.assertEqual(image.size, (320, 224))
        result = subprocess.run([sys.executable, str(SCRIPTS / 'contact_sheet.py'), str(self.video),
                                 str(self.base / 'contact'), '--interval', '2'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('image extension', result.stderr)


if __name__ == '__main__':
    unittest.main()
