"""Validate and install the repository-owned NICORA skills without replacing other skills."""
from __future__ import annotations
import argparse
import hashlib
import os
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
NAMES = ('nicora-delivery', 'nicora-oracle', 'nicora-api-integrations',
         'nicora-ui-terminal', 'nicora-acceptance', 'nicora-operations')


def validate(source: Path, name: str) -> bytes:
    content = source.read_bytes()
    text = content.decode('utf-8')
    front = re.match(r'\A---\nname: ([a-z0-9-]+)\ndescription: ([^\n]+)\n---\n', text)
    if not front or front.group(1) != name:
        raise ValueError(f'Invalid skill metadata: {source}')
    for relative in re.findall(r'\b(?:wiki|config)/[a-zA-Z0-9_./-]+\.(?:md|json)', text):
        if not (ROOT / relative).is_file():
            raise ValueError(f'Missing repository reference: {relative}')
    return content


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--install', action='store_true')
    parser.add_argument('--target', type=Path, default=Path(os.environ.get('CODEX_HOME', Path.home() / '.codex')) / 'skills')
    args = parser.parse_args()
    sources = [(name, ROOT / 'tools' / 'skills' / name / 'SKILL.md') for name in NAMES]
    validated = [(name, source, validate(source, name)) for name, source in sources]
    target_root = args.target.resolve()
    # Inspect all destinations before any mutation. Never overwrite a different local skill.
    if args.install:
        for name, _, content in validated:
            target = target_root / name / 'SKILL.md'
            if target.parent.is_symlink() or target.is_symlink():
                raise ValueError(f'Refusing symlink destination: {target}')
            if target.exists() and target.read_bytes() != content:
                raise ValueError(f'Existing local skill differs; reconcile before installation: {target}')
        for name, source, content in validated:
            target = target_root / name / 'SKILL.md'
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            if target.read_bytes() != content:
                raise RuntimeError(f'Installed copy differs: {target}')
    for name, _, content in validated:
        action = 'installed' if args.install else 'validated'
        print(f'{name}: {action}; sha256={hashlib.sha256(content).hexdigest()}')
    if args.install:
        print(f'Discovery location: {target_root}; start a fresh Codex session to refresh the skill catalog.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
