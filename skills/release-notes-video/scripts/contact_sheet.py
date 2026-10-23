"""Sample actual exported frames into a timestamped contact sheet (requires Pillow)."""
import argparse
import io
import math
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw
from inspect_media import inspect


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('video', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--interval', type=float, default=2.5)
    parser.add_argument('--columns', type=int, default=4)
    parser.add_argument('--width', type=int, default=240)
    args = parser.parse_args()
    if args.interval <= 0 or not 1 <= args.columns <= 12 or not 80 <= args.width <= 1920:
        parser.error('use a positive interval, 1–12 columns and a width of 80–1920 pixels')
    if args.video.resolve() == args.output.resolve():
        parser.error('output must not overwrite the source video')
    Image.init()
    if args.output.suffix.lower() not in Image.registered_extensions():
        parser.error('output needs an image extension such as .jpg or .png')
    info = inspect(args.video)
    samples = max(1, math.ceil(info['duration_seconds'] / args.interval))
    if samples > 500:
        parser.error('too many samples; increase the interval to produce at most 500')
    height = max(2, round(args.width * info['height'] / info['width']))
    label = 24
    sheet = Image.new('RGB', (args.columns * args.width, math.ceil(samples / args.columns) * (height + label)), '#17171b')
    draw = ImageDraw.Draw(sheet)
    for i in range(samples):
        time = min(i * args.interval, max(0, info['duration_seconds'] - .05))
        raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', str(time), '-i', str(args.video),
              '-frames:v', '1', '-vf', f'scale={args.width}:{height}', '-f', 'image2pipe', '-vcodec', 'mjpeg', '-'])
        with Image.open(io.BytesIO(raw)) as frame:
            x, y = (i % args.columns) * args.width, (i // args.columns) * (height + label)
            sheet.paste(frame.convert('RGB'), (x, y + label))
            draw.text((x + 7, y + 5), f'{int(time // 60):02d}:{time % 60:05.2f}', fill='#ffffff')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.output)
    print(f'{samples} frames -> {args.output}')


if __name__ == '__main__':
    main()
