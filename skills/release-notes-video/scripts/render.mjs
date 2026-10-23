// Capture an episode-authored page exposing async window.render(songTime).
// Resolve Playwright from the video project, not the installed skill directory.
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';
import { execFileSync } from 'node:child_process';

const options = {};
const allowed = new Set(['page', 'output', 'mode', 'width', 'height', 'fps', 'duration', 'from', 'to', 'workers', 'times', 'timeout-ms']);
for (let i = 2; i < process.argv.length; i += 2) {
  const key = process.argv[i].replace(/^--/, '');
  if (!allowed.has(key) || process.argv[i + 1] == null) throw new Error(`Unknown or incomplete option: ${process.argv[i]}`);
  options[key] = process.argv[i + 1];
}
if (!options.page || !options.output || !options.duration) throw new Error('Pass --page composition.html --output NEW_DIRECTORY --duration SECONDS; optional --mode video|stills|shots, --times 0,1,2, --from, --to, --width, --height, --fps, --workers');
const pagePath = path.resolve(options.page), output = path.resolve(options.output);
const mode = options.mode || 'video';
const width = Number(options.width || 1080), height = Number(options.height || 1350);
const fps = Number(options.fps || 24), duration = Number(options.duration);
const from = Number(options.from || 0), to = Number(options.to || duration), workers = Number(options.workers || 2);
const timeout = Number(options['timeout-ms'] || 30000);
if (!['video', 'stills', 'shots'].includes(mode) || ![width, height, fps, duration, from, to, workers].every(Number.isFinite)
    || width <= 0 || height <= 0 || width % 2 || height % 2 || fps <= 0 || duration <= 0
    || from < 0 || to <= from || to > duration || !Number.isInteger(workers) || workers < 1 || workers > 16
    || !Number.isFinite(timeout) || timeout < 100) throw new Error('Invalid mode, dimensions, timing, timeout or worker count');
if (![from, to].every(t => Math.abs(t * fps - Math.round(t * fps)) < 1e-6)) throw new Error('Range endpoints must land on frame boundaries');
if (fs.existsSync(output)) throw new Error('Choose a new output directory to prevent stale-frame reuse');
const requireProject = createRequire(path.join(path.dirname(pagePath), 'package.json'));
const { chromium } = requireProject('playwright');
fs.mkdirSync(output, { recursive: true });
const browser = await chromium.launch({ args: ['--allow-file-access-from-files'] });
const pageErrors = [];
async function deadline(operation, label) {
  let timer;
  try {
    return await Promise.race([operation, new Promise((_, reject) => {
      timer = setTimeout(() => reject(new Error(`${label} exceeded ${timeout}ms`)), timeout);
    })]);
  } finally { clearTimeout(timer); }
}
async function openPage() {
  const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 });
  page.setDefaultTimeout(timeout);
  page.on('pageerror', error => pageErrors.push(error.message));
  await page.goto(pathToFileURL(pagePath).href);
  await page.waitForFunction(() => typeof window.render === 'function');
  await deadline(page.evaluate(async () => { if (window.ready) await window.ready; await document.fonts.ready; }), 'Page readiness');
  return page;
}
async function capture(page, time, destination) {
  await deadline(page.evaluate(async t => {
    await window.render(t);
    await document.fonts.ready;
    await Promise.all([...document.images].map(image => image.decode()));
    // Draw again after delayed assets settle; render must be a pure function of t.
    await window.render(t);
  }, time), `Frame at ${time}s`);
  if (pageErrors.length) throw new Error(`Page failed: ${pageErrors.join('; ')}`);
  await page.screenshot({ path: destination, type: 'png', clip: { x: 0, y: 0, width, height } });
}
try {
  const page = await openPage();
  const shots = await page.evaluate(() => (window.SHOTS || []).map(shot => ({ start: shot.start ?? shot.t0, end: shot.end ?? shot.t1 })));
  if (!shots.length) throw new Error('Expose a nonempty window.SHOTS cut list covering the declared duration');
  const issues = [];
  shots.forEach((shot, i) => {
    if (![shot.start, shot.end].every(Number.isFinite) || shot.end <= shot.start) issues.push(`Invalid shot ${i}`);
    if (shot.end - shot.start < .6) console.warn(`Short shot ${i}: ${(shot.end - shot.start).toFixed(3)}s`);
    if (i && Math.abs(shot.start - shots[i - 1].end) > 1e-6) issues.push(`Gap/overlap before shot ${i}`);
  });
  if (shots.length && (Math.abs(shots[0].start) > 1e-6 || Math.abs(shots.at(-1).end - duration) > 1e-6)) issues.push('Shot list does not cover the declared duration');
  if (issues.length) throw new Error(issues.join('; '));
  fs.writeFileSync(path.join(output, 'shots.json'), JSON.stringify(shots, null, 2));
  if (mode === 'shots') {
    if (pageErrors.length) throw new Error(pageErrors.join('; '));
    console.log(JSON.stringify(shots));
  } else if (mode === 'stills') {
    const times = (options.times || `${from},${Math.max(from, to - 1 / fps)}`).split(',').map(Number);
    if (!times.every(t => Number.isFinite(t) && t >= from && t < to)) throw new Error('Still times must lie in the selected range');
    for (let i = 0; i < times.length; i++) await capture(page, times[i], path.join(output, `still-${i}-${times[i].toFixed(4)}.png`));
  } else {
    const frames = path.join(output, 'frames'); fs.mkdirSync(frames);
    const start = Math.round(from * fps), end = Math.round(to * fps), count = end - start;
    const pages = [page, ...await Promise.all(Array.from({ length: workers - 1 }, openPage))];
    await Promise.all(pages.map(async (worker, offset) => {
      for (let frame = start + offset; frame < end; frame += workers) {
        await capture(worker, frame / fps, path.join(frames, `${String(frame - start).padStart(6, '0')}.png`));
      }
    }));
    if (pageErrors.length || fs.readdirSync(frames).length !== count) throw new Error('Render failed or frames are missing');
    execFileSync('ffmpeg', ['-n', '-v', 'error', '-framerate', String(fps), '-i', path.join(frames, '%06d.png'),
      '-frames:v', String(count), '-an', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p',
      '-movflags', '+faststart', path.join(output, 'picture.mp4')], { stdio: 'inherit' });
    fs.writeFileSync(path.join(output, 'render.json'), JSON.stringify({ width, height, fps, from, to, frames: count, silent: true }, null, 2));
    console.log(path.join(output, 'picture.mp4'));
  }
} finally {
  await browser.close();
}
