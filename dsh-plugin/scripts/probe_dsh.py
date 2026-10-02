#!/usr/bin/env python3
"""Read a DSH checkout baseline without importing plugins or reading secrets."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

SURFACES = [
    'AGENTS.md', 'docs/architecture.zh.md', 'docs/development.zh.md',
    'vendor/README.md', 'vendor/cordis/src/context.ts', 'vendor/cordis/src/fiber.ts',
    'packages/boot/app-boot/README.zh.md', 'packages/boot/plugin-manager/README.zh.md',
    'packages/core/tools/src/index.ts', 'packages/core/tools/src/schema.ts',
    'packages/client/modules/src/client/manifest.ts',
    'packages/client/ui-conversation/src/client/contract/slots.ts',
    'packages/client/ui-plugin-manager/src/client/slot-contract.ts',
    'packages/client/locale/src/client/index.ts',
    'packages/client/ui-theme/src/styles/design-platform.css',
]


def git(root, *args):
    result = subprocess.run(['git', '-C', str(root), *args], capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else None


def probe(root):
    manifest_path = root / 'apps/cli/package.json'
    manifest = json.loads(manifest_path.read_text())
    if manifest.get('name') != '@deepseek-ai/dsh':
        raise ValueError('Expected a DSH source checkout with apps/cli/package.json')
    surfaces = {}
    for relative in SURFACES:
        path = root / relative
        surfaces[relative] = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
    return {
        'formatVersion': 1, 'dshVersion': manifest['version'],
        'commit': git(root, 'rev-parse', 'HEAD'),
        'worktreeStatus': git(root, 'status', '--short'),
        'surfaces': surfaces,
        'limitation': 'Source evidence only; not runtime, installation or compatibility verification.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dsh', required=True, type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        result = json.dumps(probe(args.dsh.resolve()), indent=2, ensure_ascii=False) + '\n'
        if args.output:
            # Deliberately refuse replacement: comparisons need both baselines.
            with args.output.open('x') as file:
                file.write(result)
        else:
            print(result, end='')
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f'probe failed: {error}\n')


if __name__ == '__main__':
    main()
