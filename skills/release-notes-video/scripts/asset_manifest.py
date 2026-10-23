"""Create or verify a local SHA-256 inventory for an episode archive."""
import argparse
import hashlib
import json
from pathlib import Path


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['create', 'verify'])
    parser.add_argument('root', type=Path)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--exclude', action='append', default=[], help='relative directory to omit; repeatable')
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        if not root.is_dir():
            raise ValueError('archive root must be a directory')
        if args.mode == 'create':
            excludes = []
            for value in args.exclude:
                relative = Path(value)
                if relative.is_absolute() or '..' in relative.parts:
                    raise ValueError('exclude paths must stay inside the archive root')
                excludes.append(relative)
            rows = []
            for path in sorted(root.rglob('*')):
                relative = path.relative_to(root)
                if any(relative == excluded or excluded in relative.parents for excluded in excludes):
                    continue
                if path.is_symlink():
                    raise ValueError(f'symlink in archive: {relative}')
                if path.is_file() and path.resolve() != args.manifest.resolve():
                    rows.append({'path': relative.as_posix(), 'bytes': path.stat().st_size, 'sha256': sha256(path)})
            if not rows:
                raise ValueError('archive contains no files')
            if args.manifest.exists():
                raise ValueError('manifest already exists; choose a new filename')
            args.manifest.write_text(json.dumps({'files': rows}, indent=2) + '\n', encoding='utf-8')
        else:
            rows = json.loads(args.manifest.read_text(encoding='utf-8'))['files']
            seen = set()
            for row in rows:
                relative = Path(row['path'])
                path = root / relative
                if relative.is_absolute() or '..' in relative.parts or row['path'] in seen:
                    raise ValueError('unsafe or duplicated manifest path')
                seen.add(row['path'])
                if root not in path.resolve().parents or any(part.is_symlink() for part in [path, *path.parents] if part != root and root in part.parents):
                    raise ValueError('manifest path escapes the root or uses a symlink')
                if path.stat().st_size != row['bytes'] or sha256(path) != row['sha256']:
                    raise ValueError(f'archive mismatch: {relative}')
            if not rows:
                raise ValueError('manifest contains no files')
        print(json.dumps({'mode': args.mode, 'files': len(rows), 'verified': args.mode == 'verify'}))
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.error(str(error))


if __name__ == '__main__':
    main()
