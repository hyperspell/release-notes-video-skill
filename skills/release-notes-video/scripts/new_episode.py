"""Create a local episode workspace without overwriting an existing project."""
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--audience', choices=['public', 'internal'], required=True)
    parser.add_argument('--duration', type=float, default=60)
    parser.add_argument('--aspect', choices=['4:5', '16:9'],
                        help='defaults to 4:5 for public; required for internal, after confirming the display')
    args = parser.parse_args()
    if not 0 < args.duration <= 3600:
        parser.error('duration must be positive and at most 3600 seconds')
    if args.audience == 'internal' and not args.aspect:
        parser.error('confirm the all-hands display, then pass --aspect 16:9 or --aspect 4:5')
    target = args.directory.resolve()
    if target.exists():
        parser.error('directory already exists; choose a new episode directory')
    aspect = args.aspect or '4:5'
    size = [1080, 1350] if aspect == '4:5' else [1920, 1080]
    target.mkdir(parents=True)
    for folder in ['notes', 'audio/originals', 'audio/takes', 'assets', 'timing', 'shots', 'deliver/demos', 'qa']:
        (target / folder).mkdir(parents=True)
    project = {'audience': args.audience, 'duration_seconds': args.duration, 'aspect_ratio': aspect,
               'width': size[0], 'height': size[1], 'fps': 24,
               'approvals': {'story': None, 'genre': None, 'lyrics': None, 'take': None, 'final': None},
               'generation_budget': None, 'publishing_authorized': False}
    (target / 'project.json').write_text(json.dumps(project, indent=2) + '\n', encoding='utf-8')
    brief = (f'# Episode brief\n\nAudience: {args.audience}\nTarget: {args.duration:g} seconds, {aspect}\n\n'
             '## Story\n\nRecord the source window, proposed headline and intended takeaway.\n\n'
             '## Evidence\n\n| Update | Status | Source | Audience | Demonstration | Caveat |\n'
             '|---|---|---|---|---|---|\n\n'
             '## Approvals\n\nRecord choices and authorized generation spend before dependent work.\n\n'
             '## Feedback\n\nKeep private conversation details here, outside the distributed skill.\n')
    (target / 'notes/brief.md').write_text(brief, encoding='utf-8')
    kit = {'title': 'Weekly update', 'main_post': 'Our weekly update, in a song. Sound on.',
           'before_posting': ['Confirm the audience, final approval and availability wording.'],
           'items': [{'title': 'A verified capability', 'description': 'Replace this example with approved copy.',
                      'clip': 'deliver/demos/example.mp4', 'filename': 'example-demo.mp4'}]}
    (target / 'kit.json').write_text(json.dumps(kit, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'directory': str(target), 'project': project}))


if __name__ == '__main__':
    main()
