"""One durable claim identity per request; expiry never silently creates another attempt."""
from contextlib import contextmanager
import json
from pathlib import Path
import sqlite3
from typing import Iterator
from uuid import uuid4
from ..contracts_scales import ScaleGatewayError


class SqliteWarehouseScaleClaims:
    def __init__(self, path: Path) -> None:
        self.path = path
        with self._connection() as db:
            db.execute('''create table if not exists warehouse_claim(
                request_id text primary key, device_id text not null, body blob not null,
                state text not null default 'PENDING', last_error text)''')
            db.execute('''create table if not exists warehouse_zero(
                claim_id text primary key, request_id text not null, body blob not null)''')

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        db = sqlite3.connect(self.path, timeout=5)
        try:
            db.execute('pragma synchronous=FULL')
            with db:
                yield db
        finally:
            db.close()

    def prepare(self, request_id: str, device_id: str) -> bytes:
        for value in (request_id, device_id):
            if not isinstance(value, str) or not 1 <= len(value) <= 100:
                raise ValueError('WAREHOUSE_CLAIM_ID_REQUIRED')
        with self._connection() as db:
            db.execute('begin immediate')
            row = db.execute('select device_id,body,state from warehouse_claim where request_id=?', (request_id,)).fetchone()
            if row:
                if row[0] != device_id:
                    raise ScaleGatewayError('WAREHOUSE_CLAIM_DEVICE_CONFLICT')
                if row[2] == 'TERMINAL':
                    raise ScaleGatewayError('WAREHOUSE_CLAIM_TERMINAL_REVIEW_REQUIRED')
                return row[1]
            body = json.dumps(dict(claim_id='WH.OPC.'+uuid4().hex, device_id=device_id),
                              sort_keys=True, separators=(',', ':')).encode()
            db.execute('insert into warehouse_claim(request_id,device_id,body)values(?,?,?)', (request_id, device_id, body))
            return body

    def terminal(self, request_id: str, error: str) -> None:
        with self._connection() as db:
            db.execute("update warehouse_claim set state='TERMINAL',last_error=? where request_id=?", (error[:200], request_id))

    def zero(self, claim_id: str) -> bytes | None:
        with self._connection() as db:
            row = db.execute('select body from warehouse_zero where claim_id=?', (claim_id,)).fetchone()
            return row[0] if row else None

    def stage_zero(self, request_id: str, claim_id: str, body: bytes) -> None:
        with self._connection() as db:
            db.execute('begin immediate')
            row = db.execute('select request_id,body from warehouse_zero where claim_id=?', (claim_id,)).fetchone()
            if row:
                if row != (request_id, body):
                    raise ScaleGatewayError('WAREHOUSE_ZERO_IMMUTABLE_BODY_CONFLICT')
                return
            db.execute('insert into warehouse_zero(claim_id,request_id,body)values(?,?,?)', (claim_id, request_id, body))
