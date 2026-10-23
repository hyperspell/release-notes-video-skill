import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync, spawnSync } from 'node:child_process';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const renderer = path.join(root, 'skills/release-notes-video/scripts/render.mjs');
function fixture(body, ready = '') {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'video-render-test-'));
  fs.symlinkSync(path.join(root, 'node_modules'), path.join(directory, 'node_modules'), 'dir');
  const page = path.join(directory, 'composition.html');
  fs.writeFileSync(page, `<!doctype html><style>body{margin:0}canvas{display:block}</style><canvas width="64" height="80"></canvas><script>
    const canvas=document.querySelector('canvas'), ctx=canvas.getContext('2d');
    window.SHOTS=[{start:0,end:1}]; ${ready}
    window.render=async t=>{${body}};
  </script>`);
  return { directory, page };
}
function render(f, name, extra = []) {
  return spawnSync(process.execPath, [renderer, '--page', f.page, '--output', path.join(f.directory, name),
    '--duration', '1', '--width', '64', '--height', '80', '--fps', '24', ...extra],
    { encoding: 'utf8', timeout: 20000 });
}
test('captures deterministic out-of-order frames and silent video', () => {
  const f = fixture("await new Promise(resolve=>setTimeout(resolve,5));ctx.fillStyle=t<.5?'#f00':'#00f';ctx.fillRect(0,0,64,80)");
  try {
    const stills = render(f, 'stills', ['--mode', 'stills', '--times', '0.75,0.25,0.75']);
    assert.equal(stills.status, 0, stills.stderr);
    const files = fs.readdirSync(path.join(f.directory, 'stills')).filter(name => name.endsWith('.png')).sort();
    const bytes = name => fs.readFileSync(path.join(f.directory, 'stills', name));
    assert.deepEqual(bytes(files[0]), bytes(files[2]));
    assert.notDeepEqual(bytes(files[0]), bytes(files[1]));
    const video = render(f, 'video', ['--workers', '2']);
    assert.equal(video.status, 0, video.stderr);
    const probe = JSON.parse(execFileSync('ffprobe', ['-v', 'error', '-show_streams', '-show_format', '-of', 'json', path.join(f.directory, 'video/picture.mp4')], { encoding: 'utf8' }));
    assert.equal(probe.streams.length, 1);
    assert.equal(probe.streams[0].nb_frames, '24');
    assert.equal(Number(probe.format.duration), 1);
    const repeated = render(f, 'video');
    assert.notEqual(repeated.status, 0);
  } finally { fs.rmSync(f.directory, { recursive: true, force: true }); }
});
test('page errors and unresolved render promises fail without an export', () => {
  for (const [body, name] of [["throw new Error('missing media')", 'error'], ["await new Promise(()=>{})", 'timeout']]) {
    const f = fixture(body);
    try {
      const result = render(f, name, ['--workers', '1', '--timeout-ms', '500']);
      assert.notEqual(result.status, 0);
      assert.equal(fs.existsSync(path.join(f.directory, name, 'picture.mp4')), false);
      assert.match(result.stderr, name === 'error' ? /missing media/ : /exceeded 500ms/);
    } finally { fs.rmSync(f.directory, { recursive: true, force: true }); }
  }
});
test('cut list ending one frame early is rejected', () => {
  const f = fixture("ctx.fillRect(0,0,64,80)", 'window.SHOTS=[{start:0,end:23/24}];');
  try {
    const result = render(f, 'undercovered');
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /does not cover the declared duration/);
    assert.equal(fs.existsSync(path.join(f.directory, 'undercovered/picture.mp4')), false);
  } finally { fs.rmSync(f.directory, { recursive: true, force: true }); }
});
