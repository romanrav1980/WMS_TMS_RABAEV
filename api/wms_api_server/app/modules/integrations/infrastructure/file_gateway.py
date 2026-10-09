"""One OS-owned directory lock; abandoned XML claims recover after process death."""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import time
from typing import Iterator, Protocol
from uuid import uuid4


class XmlReceiver(Protocol):
    def receive(self, raw: bytes, actor: str) -> dict: ...


@contextmanager
def directory_owner(root: Path) -> Iterator[bool]:
    path = root / '.worker.lock'
    if path.is_symlink():
        raise ValueError('Gateway lock must not be a symbolic link')
    with path.open('a+b') as handle:
        handle.seek(0)
        if not handle.read(1):
            handle.write(b'0'); handle.flush()
        handle.seek(0)
        acquired = False
        try:
            if os.name == 'nt':
                import msvcrt
                try:
                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                    acquired = True
                except OSError:
                    pass
            else:
                import fcntl
                try:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    acquired = True
                except BlockingIOError:
                    pass
            yield acquired
        finally:
            if acquired:
                handle.seek(0)
                if os.name == 'nt':
                    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def receive_files(root: Path, receiver: XmlReceiver, limit: int = 20, min_age: int = 2) -> list[dict]:
    root = root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    folders = {n: (root / n).resolve() for n in ('inbox', 'archive', 'error')}
    for path in folders.values():
        if not path.is_relative_to(root):
            raise ValueError('Gateway directory escapes root')
        path.mkdir(parents=True, exist_ok=True)
    with directory_owner(root) as acquired:
        if not acquired:
            return [{'status': 'BUSY', 'reason': 'another worker owns this directory'}]
        # The OS released the previous owner's lock: no still-running claim is reclaimed.
        for abandoned in folders['inbox'].glob('*.processing-*'):
            if abandoned.is_symlink() or not abandoned.is_file():
                continue
            token = uuid4().hex
            abandoned.rename(folders['inbox'] / ('recovered-' + token + '.xml'))
        results = []
        for path in sorted(folders['inbox'].glob('*.xml'))[:limit]:
            if path.is_symlink() or not path.resolve().is_relative_to(root):
                continue
            if time.time() - path.stat().st_mtime < min_age:
                continue
            token = uuid4().hex
            claimed = path.with_suffix('.processing-' + token)
            path.rename(claimed)
            result = {'file': path.name, 'claim': token}
            try:
                with claimed.open('rb') as handle:
                    raw = handle.read(4 * 1024 * 1024 + 1)
                result.update(receiver.receive(raw, 'SAP_FILE_GATEWAY'))
                directory = folders['archive']
            except Exception as exc:
                result.update(status='ERROR', error=str(exc))
                directory = folders['error']
            destination = directory / (token + '-' + path.name)
            # Publish the result first; an interrupted rename leaves the XML claim recoverable.
            destination.with_suffix('.result.json').write_text(json.dumps(result, ensure_ascii=False, default=str), encoding='utf-8')
            claimed.rename(destination)
            results.append(result)
        return results
