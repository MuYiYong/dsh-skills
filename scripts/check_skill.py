#!/usr/bin/env python3
"""Check portable skill packaging and local reference integrity, using stdlib."""
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'dsh-plugin'
text = (SKILL / 'SKILL.md').read_text()
assert text.startswith('---\n')
frontmatter = text.split('---', 2)[1]
assert re.search(r'^name: dsh-plugin$', frontmatter, re.M)
assert re.search(r'^description: .+', frontmatter, re.M)
assert len(text.splitlines()) < 250
for path in [ROOT / 'README.md', *SKILL.rglob('*.md')]:
    for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
        if '://' in target or target.startswith('#'):
            continue
        dest = (path.parent / target.split('#')[0]).resolve()
        assert dest.is_file(), f'{path}: broken link {target}'
        if SKILL in path.parents:
            assert dest.is_relative_to(SKILL), f'skill depends on uninstalled resource: {target}'
for path in SKILL.rglob('*.py'):
    compile(path.read_text(), str(path), 'exec')
for path in [*SKILL.rglob('*.js'), *SKILL.rglob('*.mjs')]:
    subprocess.run(['node', '--check', str(path)], check=True)
assert not any(SKILL.rglob('node_modules'))
print('Skill metadata, self-contained links, Python and JavaScript syntax: OK')
