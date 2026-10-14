import json
from pathlib import Path
p=Path("api/wms_api_server/app/modules/integrations/infrastructure/outbox_response_journal.py");s=p.read_text(encoding="utf-8")
start=s.index('        with directory_owner(self._owner(key)) as owned:',s.index('    def save'))
end=s.index('        return key',s.index('            finally:',start))+len('        return key')
s=s[:start]+'''        if path.is_symlink():
            raise ValueError("Response journal entry must not be a symbolic link")
        temporary = self.pending / (key + ".writing-" + uuid4().hex)
        try:
            with temporary.open("xb") as handle:
                handle.write(raw); handle.flush(); os.fsync(handle.fileno())
            # Atomic create-if-absent publication on local NTFS/POSIX; immutable payload.
            # A recovery may remove an already finalized record between attempts.
            for _ in range(3):
                try:
                    os.link(temporary, path)
                    break
                except FileExistsError:
                    try:
                        existing = path.read_bytes()
                    except FileNotFoundError:
                        continue
                    if existing != raw:
                        raise RuntimeError("OUTBOX_RESPONSE_JOURNAL_CONTENT_CONFLICT")
                    break
            else:
                raise RuntimeError("OUTBOX_RESPONSE_JOURNAL_PUBLICATION_UNCONFIRMED")
        finally:
            if temporary.exists():
                temporary.unlink()
        return key''' +s[end:]
s=s.replace('                with path.open("rb") as handle:\n                    raw = handle.read(self.MAX_BYTES + 1)', '''                try:
                    with path.open("rb") as handle:
                        raw = handle.read(self.MAX_BYTES + 1)
                except FileNotFoundError:
                    continue''')
print(json.dumps({str(p):s}))
