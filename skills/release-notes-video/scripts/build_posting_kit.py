"""Package approved copy and silent clips in an offline HTML page and a ZIP."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import zipfile

from inspect_media import inspect

HTML = r'''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Video posting kit</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#f5f3ef;color:#19191c;font:17px/1.5 system-ui,sans-serif}
main{max-width:950px;margin:auto;padding:36px 20px}h1{font-size:clamp(30px,5vw,48px);line-height:1.1}h2{line-height:1.2}
section,article{background:white;padding:24px;margin:22px 0;border-radius:16px;border:1px solid #dedbd5}
article{display:grid;grid-template-columns:minmax(150px,260px) minmax(0,1fr);gap:24px}
video{width:100%;max-height:480px;background:#17171b;border-radius:8px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:inherit}
button,a.download{display:inline-block;margin:8px 8px 0 0;padding:10px 15px;border:1px solid #444;border-radius:8px;background:white;color:#19191c;font:inherit;cursor:pointer;text-decoration:none}
button:focus-visible,a:focus-visible{outline:3px solid #2570db;outline-offset:3px}li{margin:8px 0}article p{white-space:pre-line;overflow-wrap:anywhere}
.status{position:fixed;left:50%;bottom:20px;transform:translateX(-50%);max-width:calc(100% - 32px);margin:0;padding:10px 16px;border-radius:8px;background:#19191c;color:white}.status:empty{display:none}
@media(max-width:600px){article{grid-template-columns:1fr}video{max-width:340px;justify-self:center}section,article{padding:18px}}
</style>
<main><h1 id="title"></h1><p>Download the original clips and copy the approved post text. Share the main music video separately.</p>
<section><h2>Main post</h2><pre id="post"></pre><button id="copy-main">Copy main post</button></section>
<div id="items"></div><section id="notes"><h2>Before posting</h2><ul></ul></section><p class="status" role="status" aria-live="polite"></p></main>
<script id="payload" type="application/json">__PAYLOAD__</script>
<script>
const data=JSON.parse(document.getElementById('payload').textContent);
document.title=data.title;document.getElementById('title').textContent=data.title;document.getElementById('post').textContent=data.main_post;
const status=document.querySelector('.status');let statusTimer;
function announce(message){status.textContent=message;clearTimeout(statusTimer);statusTimer=setTimeout(()=>{status.textContent='';},4000);}
async function copy(text){
 try{
  if(navigator.clipboard&&window.isSecureContext){await navigator.clipboard.writeText(text);}
  else{const field=document.createElement('textarea');field.value=text;field.style.position='fixed';field.style.opacity='0';document.body.append(field);field.select();const ok=document.execCommand('copy');field.remove();if(!ok)throw Error('copy failed');}
  announce('Copied.');
 }catch{announce('Copy was unavailable. Select and copy the text above.');}
}
document.getElementById('copy-main').onclick=()=>copy(data.main_post);
const videos=[];
for(const item of data.items){
 const row=document.createElement('article'),video=document.createElement('video'),text=document.createElement('div');
 const bytes=Uint8Array.from(atob(item.video),c=>c.charCodeAt(0));const url=URL.createObjectURL(new Blob([bytes],{type:'video/mp4'}));
 video.src=url;video.controls=true;video.muted=true;video.loop=true;video.playsInline=true;video.preload='metadata';video.setAttribute('aria-label',item.title);videos.push(video);
 const title=document.createElement('h2');title.textContent=item.title;const desc=document.createElement('p');desc.textContent=item.description;
 const button=document.createElement('button');button.textContent='Copy reply';button.onclick=()=>copy(item.title+'\n\n'+item.description);
 const link=document.createElement('a');link.className='download';link.textContent='Download MP4';link.href=url;link.download=item.filename;
 text.append(title,desc,button,link);row.append(video,text);document.getElementById('items').append(row);
}
const reduced=window.matchMedia('(prefers-reduced-motion: reduce)');let observer;
function playback(){
 observer?.disconnect();videos.forEach(v=>v.pause());
 if(reduced.matches||!('IntersectionObserver' in window))return;
 observer=new IntersectionObserver(entries=>entries.forEach(e=>{if(e.isIntersecting)e.target.play().catch(()=>{});else e.target.pause();}),{threshold:.4});videos.forEach(v=>observer.observe(v));
}
playback();reduced.addEventListener('change',playback);
for(const note of data.before_posting){const li=document.createElement('li');li.textContent=note;document.querySelector('#notes ul').append(li);}
if(!data.before_posting.length)document.getElementById('notes').hidden=true;
// Blob URLs live for the document lifetime so back/forward restoration keeps downloads working.
</script></html>'''


def build(manifest, output):
    manifest, output = manifest.resolve(), output.resolve()
    data = json.loads(manifest.read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise ValueError('manifest must be an object')
    for key in ['title', 'main_post']:
        if not isinstance(data.get(key), str) or not data[key].strip():
            raise ValueError(f'{key} must be nonempty text')
    notes = data.get('before_posting', [])
    if not isinstance(notes, list) or not all(isinstance(n, str) for n in notes):
        raise ValueError('before_posting must be a list of strings')
    data['before_posting'] = notes
    if not isinstance(data.get('items'), list) or not data['items']:
        raise ValueError('items must be a nonempty list')
    if output.exists() and any(output.iterdir()):
        raise ValueError('output directory is not empty; choose a new directory')
    files, names, inventory = [], set(), []
    for item in data['items']:
        if not isinstance(item, dict):
            raise ValueError('each item must be an object')
        for key in ['title', 'description', 'clip', 'filename']:
            if not isinstance(item.get(key), str) or not item[key].strip():
                raise ValueError(f'each item needs nonempty {key}')
        name = item['filename']
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,100}\.mp4', name) or name.lower() in names:
            raise ValueError('filenames must be unique simple MP4 names')
        names.add(name.lower())
        source = (manifest.parent / item['clip']).resolve()
        if not source.is_relative_to(manifest.parent) or source.is_relative_to(output):
            raise ValueError('clips must stay in the episode directory and outside output')
        if not source.is_file():
            raise ValueError(f'clip for "{item["title"]}" not found: {item["clip"]} (relative to the manifest)')
        info = inspect(source)
        if info['audio_streams'] or info['codec'] != 'h264' or not 4 <= info['duration_seconds'] <= 9.1:
            raise ValueError('demos must be silent H.264 clips, 4–9 seconds long')
        raw = source.read_bytes()
        if sum(len(b) for _, _, b in files) + len(raw) > 25 * 1024 * 1024:
            raise ValueError('embedded clips exceed 25 MiB; make a smaller kit or use a hosted workflow')
        item['video'] = base64.b64encode(raw).decode()
        files.append((source, name, raw))
        inventory.append({'filename': name, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(),
                          'duration_seconds': info['duration_seconds'], 'width': info['width'], 'height': info['height']})
    output.mkdir(parents=True, exist_ok=True)
    demos = output / 'demos'
    demos.mkdir()
    for source, name, raw in files:
        target = demos / name
        shutil.copyfile(source, target)
        if hashlib.sha256(target.read_bytes()).hexdigest() != hashlib.sha256(raw).hexdigest():
            raise ValueError('clip changed while building; use stable source files')
    public_data = {key: data[key] for key in ['title', 'main_post', 'before_posting']}
    public_data['items'] = [{key: item[key] for key in ['title', 'description', 'filename', 'video']}
                            for item in data['items']]
    payload = json.dumps(public_data, ensure_ascii=False).replace('<', '\\u003c')
    (output / 'posting-kit.html').write_text(HTML.replace('__PAYLOAD__', payload), encoding='utf-8')
    copy = data['main_post'] + '\n\n' + '\n\n'.join(i['title'] + '\n\n' + i['description'] for i in data['items']) + '\n'
    (output / 'post-copy.txt').write_text(copy, encoding='utf-8')
    (output / 'manifest.json').write_text(json.dumps(inventory, indent=2) + '\n', encoding='utf-8')
    (output / 'README.txt').write_text('Open posting-kit.html in your browser. It works offline. The demos folder contains the original silent MP4s. Post the main music video separately. Review Before posting notes before forwarding this kit.\n', encoding='utf-8')
    with zipfile.ZipFile(output / 'posting-kit.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in ['posting-kit.html', 'post-copy.txt', 'manifest.json', 'README.txt']:
            archive.write(output / name, name)
        for _, name, _ in files:
            archive.write(demos / name, 'demos/' + name)
    return {'html': str(output / 'posting-kit.html'), 'zip': str(output / 'posting-kit.zip'), 'clips': inventory}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = build(args.manifest.resolve(), args.output.resolve())
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f'Cannot build posting kit: {exc}\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
