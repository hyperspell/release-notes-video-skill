"""Align the sung sheet to word evidence and report every unresolved/interpolated word."""
import argparse
import difflib
import json
import math
import re
from pathlib import Path


def norm(value):
    return re.sub(r'[^a-z0-9]', '', value.lower())


def parse_sheet(text):
    lines, section = [], 'Song'
    for raw in text.splitlines():
        raw = raw.strip()
        if not raw:
            continue
        if raw.startswith('[') and raw.endswith(']'):
            section = raw[1:-1]
            continue
        words, crowd = [], False
        for token in raw.split():
            crowd = crowd or token.startswith('(')
            word = token.strip('()')
            if not norm(word):
                raise ValueError(f'unsupported lyric token: {token!r}; use words with Latin letters or digits')
            words.append({'text': word, 'crowd': crowd})
            if token.endswith(')'):
                crowd = False
        lines.append({'section': section, 'text': raw, 'words': words})
    if not lines:
        raise ValueError('the sung sheet contains no words')
    return lines


def evidence_words(data, duration):
    raw = data if isinstance(data, list) else data.get('words')
    if raw is None:
        raw = [word for segment in data.get('segments', []) for word in segment.get('words', [])]
    result, previous = [], -1
    for word in raw:
        text = word.get('word', word.get('text', '')).strip()
        start, end = float(word['start']), float(word['end'])
        if not math.isfinite(start + end) or not 0 <= start < end <= duration or start < previous:
            raise ValueError(f'invalid or unordered evidence interval for {text!r}')
        previous = start
        if not norm(text):
            continue
        if len(text.split()) != 1:
            raise ValueError('evidence must contain one word per timing entry')
        result.append({'text': text, 'start': start, 'end': end})
    return result


def matches(flat, evidence):
    matcher = difflib.SequenceMatcher(a=[norm(w['text']) for w in flat],
                                    b=[norm(w['text']) for w in evidence], autojunk=False)
    return {i + k: evidence[j + k] for i, j, count in matcher.get_matching_blocks() for k in range(count)}


def align(sheet, transcript, service, duration, envelope=None, overrides=None):
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError('duration must be finite and positive')
    lines = parse_sheet(sheet)
    flat = [word for line in lines for word in line['words']]
    heard = matches(flat, evidence_words(transcript, duration))
    supplied = matches(flat, evidence_words(service, duration))
    manual = (overrides or {}).get('words', {})
    if any(str(i) not in {str(n) for n in range(len(flat))} for i in manual):
        raise ValueError('override keys must be zero-based word indices from the sung sheet')
    if envelope:
        rate = float(envelope['rate'])
        onsets = [float(t) for t in envelope['onsets']]
        db = [float(value) for value in envelope['db']]
        if not math.isfinite(rate) or rate <= 0 or not db or not all(math.isfinite(t) and 0 <= t <= duration for t in onsets) or not all(math.isfinite(value) for value in db):
            raise ValueError('invalid vocal envelope')
    unresolved, discrepancies, rejected_service = [], [], []
    for index, word in enumerate(flat):
        whisper, aligned = heard.get(index), supplied.get(index)
        if whisper:
            word['transcript_start'] = whisper['start']
        if aligned:
            word['service_start'] = aligned['start']
        if whisper and aligned and abs(whisper['start'] - aligned['start']) > .25:
            discrepancies.append({'index': index, 'text': word['text'], 'transcript': whisper['start'], 'service': aligned['start']})
        if whisper and aligned and abs(whisper['start'] - aligned['start']) > 3 and str(index) not in manual:
            rejected_service.append({'index': index, 'text': word['text']})
            aligned = None
        chosen = manual.get(str(index)) or aligned or whisper
        if chosen is None:
            unresolved.append({'index': index, 'text': word['text']})
            continue
        word.update(start=float(chosen['start']), end=float(chosen['end']),
                    source='manual' if str(index) in manual else 'service' if aligned else 'transcript')
        if envelope and word['source'] == 'service':
            left = flat[index - 1].get('start', -1) if index else -1
            successor = manual.get(str(index + 1)) or supplied.get(index + 1) or heard.get(index + 1)
            right = float(successor['start']) if successor else duration
            near = [t for t in onsets if word['start'] - .2 <= t <= word['start'] + .05 and left < t < min(right, word['end'])]
            if near:
                word['start'] = min(near, key=lambda t: abs(t - word['start']))
                word['source'] += '+onset'
    # Draft timings remain explicitly marked. The CLI refuses to publish them by default.
    index = 0
    while index < len(flat):
        if 'start' in flat[index]:
            index += 1
            continue
        first = index
        while index < len(flat) and 'start' not in flat[index]:
            index += 1
        left = flat[first - 1]['end'] if first else 0
        right = flat[index]['start'] if index < len(flat) else duration
        if right <= left:
            raise ValueError('no room for untimed words; supply manual overrides')
        step = (right - left) / (index - first)
        for n in range(first, index):
            flat[n].update(start=left + (n - first) * step, end=left + (n - first + 1) * step, source='interpolated')
    previous = -1
    for i, word in enumerate(flat):
        start = word['start']
        cap = min(duration, flat[i + 1]['start']) if i + 1 < len(flat) else duration
        if not math.isfinite(start + word['end']) or start < 0 or start <= previous or start >= cap:
            raise ValueError(f'conflicting timing at word {i} ({word["text"]}); supply manual overrides')
        if envelope and word['source'] != 'manual':
            quiet = 0
            for j in range(int((start + .15) * rate), min(len(db), int(cap * rate))):
                quiet = quiet + 1 if db[j] < -42 else 0
                if quiet / rate >= .15:
                    word['end'] = max(start + .01, (j - quiet + 1) / rate)
                    break
        word['end'] = min(cap, word['end'])
        if word['end'] <= start:
            raise ValueError(f'nonpositive word interval at index {i}')
        if word['source'] == 'manual' and float(manual[str(i)]['end']) > cap:
            raise ValueError(f'manual word {i} overlaps its successor or exceeds duration')
        previous = start
    for i, line in enumerate(lines):
        line.update(id=f'line-{i + 1}', start=line['words'][0]['start'], end=line['words'][-1]['end'])
    report = {'total_words': len(flat), 'timed_from_evidence': len(flat) - len(unresolved),
              'unresolved': unresolved, 'discrepancies_over_250ms': discrepancies,
              'service_rejected_over_3s': rejected_service,
              'gate_passed': not unresolved}
    return {'duration': duration, 'lines': lines}, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sheet', type=Path, required=True)
    parser.add_argument('--transcript', type=Path, required=True)
    parser.add_argument('--service-words', type=Path)
    parser.add_argument('--envelope', type=Path)
    parser.add_argument('--overrides', type=Path)
    parser.add_argument('--duration', type=float, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--allow-interpolation', action='store_true')
    args = parser.parse_args()
    load = lambda path, default: json.loads(path.read_text(encoding='utf-8')) if path else default
    try:
        if args.output.exists():
            raise ValueError('output directory already exists; choose a new alignment version')
        timing, report = align(args.sheet.read_text(encoding='utf-8'), load(args.transcript, []),
                               load(args.service_words, []), args.duration,
                               load(args.envelope, None), load(args.overrides, None))
        args.output.mkdir(parents=True)
        (args.output / 'alignment-report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        if report['unresolved'] and not args.allow_interpolation:
            parser.exit(1, f'{len(report["unresolved"])} unresolved words; inspect alignment-report.json and add overrides\n')
        (args.output / 'lyrics.json').write_text(json.dumps(timing, indent=2) + '\n', encoding='utf-8')
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.error(str(error))
    print(json.dumps(report))


if __name__ == '__main__':
    main()
