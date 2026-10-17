"""Fenced physical-device ownership; independent of the HTTP outbox lease."""
from pathlib import Path
import sqlite3
from uuid import uuid4
import math
from ..contracts_scales import ScaleGatewayError


class SqliteScaleDeviceLease:
    def __init__(self, path: Path) -> None:
        self.path = path
        with sqlite3.connect(path, timeout=5) as db:
            db.execute("create table if not exists device_lease(device text primary key,token text,until_at real)")

    def acquire(self, device: str, now: float, seconds: int = 30) -> str:
        self._validate(now, seconds)
        with sqlite3.connect(self.path, timeout=5) as db:
            db.execute("begin immediate")
            row = db.execute("select until_at from device_lease where device=?", (device,)).fetchone()
            if row and row[0] > now:
                raise ScaleGatewayError("OPC_DEVICE_BUSY", True)
            token = uuid4().hex
            db.execute("insert or replace into device_lease values(?,?,?)", (device, token, now+seconds))
            return token

    def renew(self, device: str, token: str, now: float, seconds: int = 30) -> None:
        self._validate(now, seconds)
        with sqlite3.connect(self.path, timeout=5) as db:
            n = db.execute("update device_lease set until_at=? where device=? and token=? and until_at>?",
                           (now+seconds, device, token, now)).rowcount
            if n != 1:
                raise ScaleGatewayError("OPC_DEVICE_LEASE_LOST")

    def release(self, device: str, token: str) -> None:
        with sqlite3.connect(self.path, timeout=5) as db:
            db.execute("delete from device_lease where device=? and token=?", (device, token))

    @staticmethod
    def _validate(now: float, seconds: int) -> None:
        if isinstance(now, bool) or not math.isfinite(now) or now < 0 or type(seconds) is not int or not 1 <= seconds <= 60:
            raise ScaleGatewayError("OPC_LEASE_CLOCK_INVALID")
