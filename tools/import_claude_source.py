"""Import checksummed GitHub file payloads without executing downloaded source."""

import argparse
import base64
import hashlib
import json
from pathlib import Path, PurePosixPath


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('indexes', nargs='+', type=Path)
    args = parser.parse_args()
    repository = Path(__file__).resolve().parents[1]
    root = repository / 'plugins/codex-seo'
    writes = []
    inventory = []
    revision = None
    for index in args.indexes:
        source = json.loads(index.read_text(encoding='utf-8'))
        if revision is not None and revision != source['commit']:
            raise ValueError('Mixed source revisions')
        revision = source['commit']
        for entry in source['files']:
            relative = entry['path']
            parts = PurePosixPath(relative).parts
            if not parts or PurePosixPath(relative).is_absolute() or ':' in relative or '\\' in relative:
                raise ValueError('Invalid source path: ' + relative)
            if any(part in ('.', '..', '.git', '.codex', '.agents', '.aws') for part in parts):
                raise ValueError('Protected source path: ' + relative)
            if entry['mode'] not in ('100644', '100755'):
                raise ValueError('Unsupported source file mode')
            target = (root / relative).resolve()
            target.relative_to(root.resolve())
            if target.exists():
                raise ValueError('Refusing to overwrite: ' + relative)
            data = base64.b64decode(entry['content'])
            digest = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
            if digest != entry['sha']:
                raise ValueError('Git source checksum mismatch: ' + relative)
            writes.append((target, data, entry['mode']))
            inventory.append({key: entry[key] for key in ('path', 'sha', 'mode', 'size')})
    if len({str(target).casefold() for target, _, _ in writes}) != len(writes):
        raise ValueError('Source names collide on Windows')
    for target, data, mode in writes:
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as handle:
            handle.write(data)
        if mode == '100755':
            target.chmod(target.stat().st_mode | 0o111)
    output = repository / 'docs/claude-source-inventory.json'
    output.write_text(json.dumps({'repository': 'https://github.com/AgriciDaniel/claude-seo',
                                  'commit': revision, 'files': inventory}, indent=2) + '\n',
                      encoding='utf-8', newline='\n')
    print(json.dumps({'imported': len(writes), 'commit': revision, 'root': str(root)}))


if __name__ == '__main__':
    main()
