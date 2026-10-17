"""Atomic local capture/raw journal; outbound HTTP acknowledgements stay independent."""
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
from typing import Any, Iterator
import sqlite3
from ..contracts_scales import ScaleGatewayError, ScaleOutbox
from .scale_outbox import _unique_object


def packet(body: bytes, maximum: int) -> dict[str, Any]:
    if not isinstance(body,bytes) or not 1 <= len(body) <= maximum:
        raise ValueError('SCALE_BUNDLE_PACKET_BOUND')
    value=json.loads(body.decode('utf-8'),object_pairs_hook=_unique_object)
    if not isinstance(value,dict):
        raise ValueError('SCALE_BUNDLE_OBJECT_REQUIRED')
    for key in ('device_id','capture_id'):
        if not isinstance(value.get(key),str) or not 1 <= len(value[key]) <= 100:
            raise ValueError('SCALE_BUNDLE_ID_REQUIRED')
    return value


class SqliteScaleBundleJournal:
    def __init__(self,path:Path) -> None:
        self.path=path
        self._raw_checked_rowid = 0
        with self._connection() as db:
            db.execute('''create table if not exists scale_bundle(
                kind text not null,device text not null,capture text not null,
                body blob not null,raw blob not null,mirrored integer not null default 0,
                primary key(kind,device,capture))''')

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        db=sqlite3.connect(self.path,timeout=5)
        try:
            db.execute('pragma synchronous=FULL')
            with db:
                yield db
        finally:
            db.close()

    def stage(self,body:bytes,raw:bytes) -> None:
        source=packet(body,65536)
        evidence=packet(raw,131072)
        kind=evidence.get('capture_kind')
        if kind not in {'STORE_RECEIPT','WAREHOUSE_PICK','WAREHOUSE_FINAL','WAREHOUSE_ASSEMBLY','WAREHOUSE_ASSEMBLY_RECON'}:
            raise ValueError('SCALE_BUNDLE_KIND_REQUIRED')
        if any(source[key]!=evidence[key] for key in ('device_id','capture_id')):
            raise ValueError('SCALE_BUNDLE_ID_CONFLICT')
        canonical=json.dumps(source,ensure_ascii=True,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
        if evidence.get('capture_sha256')!=hashlib.sha256(canonical).hexdigest().upper():
            raise ValueError('SCALE_BUNDLE_HASH_CONFLICT')
        identity=(kind,source['device_id'],source['capture_id'])
        with self._connection() as db:
            db.execute('begin immediate')
            old=db.execute('select body,raw from scale_bundle where kind=? and device=? and capture=?',identity).fetchone()
            if old and old!=(body,raw):
                raise ScaleGatewayError('SCALE_BUNDLE_IMMUTABLE_CONFLICT')
            db.execute('insert or ignore into scale_bundle(kind,device,capture,body,raw)values(?,?,?,?,?)',(*identity,body,raw))

    def get(self,kind:str,device:str,capture:str) -> tuple[bytes, bytes] | None:
        with self._connection() as db:
            return db.execute('select body,raw from scale_bundle where kind=? and device=? and capture=?',(kind,device,capture)).fetchone()

    def reconcile(self,captures: ScaleOutbox,evidence: ScaleOutbox) -> None:
        # Neither mirror's ACK is reset by stage; a crash before the flag repeats exact bytes.
        while True:
            with self._connection() as db:
                row=db.execute('select kind,device,capture,body,raw from scale_bundle where mirrored=0 limit 1').fetchone()
            if row is None:
                break
            captures.stage(row[3])
            evidence.stage(row[4])
            with self._connection() as db:
                db.execute('update scale_bundle set mirrored=1 where kind=? and device=? and capture=?',row[:3])
        # Pre-bundle records remain delivery-owned. Dangling raw needs explicit investigation.
        for rowid,body in evidence.entries(self._raw_checked_rowid):
            source=packet(body,131072)
            if not captures.has_capture(source['device_id'],source['capture_id']):
                raise ScaleGatewayError('SCALE_LEGACY_RAW_NEEDS_RECONCILIATION')
            self._raw_checked_rowid = rowid


