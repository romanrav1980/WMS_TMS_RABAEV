"""Atomic file publication. EXPORTED denotes local delivery, not SAP acceptance."""
from hashlib import sha256
import json
from pathlib import Path
import os
from uuid import uuid4
import xml.etree.ElementTree as ET

from ....oracle_gateway import OracleGateway


class ReceiptOutbox:
    def __init__(self, gateway: OracleGateway) -> None:
        self.gateway = gateway

    def export(self, directory: Path, limit: int = 20) -> list[dict]:
        directory = directory.resolve()
        directory.mkdir(parents=True, exist_ok=True)
        exported = []
        for _ in range(limit):
            with self.gateway.transaction("NI01 publish SAP receipt event file") as cur:
                cur.arraysize = 1
                cur.prefetchrows = 0
                # Lock an oldest pending row; competing workers skip claimed rows.
                cur.execute("select EVENT_ID,EVENT_TYPE,PAYLOAD_JSON from RRL_SAP_RECEIPT_OUTBOX where STATUS='PENDING' order by CREATED_AT for update skip locked")
                row = cur.fetchone()
                if not row:
                    break
                raw = row[2].read() if hasattr(row[2], "read") else row[2]
                event = ET.Element("WmsReceiptEvent", {"version": "1"})
                ET.SubElement(event, "EventId").text = row[0]
                ET.SubElement(event, "EventType").text = row[1]
                for key, value in json.loads(raw).items():
                    if value is not None:
                        tag = "".join(part.capitalize() for part in key.split("_"))
                        child = ET.SubElement(event, tag)
                        if isinstance(value, (list, dict)):
                            child.set("encoding", "json")
                            child.text = json.dumps(value, ensure_ascii=False)
                        elif isinstance(value, bool):
                            child.text = str(value).lower()
                        else:
                            child.text = str(value)
                body = ET.tostring(event, encoding="utf-8", xml_declaration=True)
                name = sha256(row[0].encode()).hexdigest() + ".xml"
                target = directory / name
                temporary = directory / (name + ".writing-" + uuid4().hex)
                if target.is_symlink():
                    raise ValueError("Outbox target must not be a symbolic link")
                try:
                    with temporary.open("xb") as file:
                        file.write(body)
                        file.flush()
                        os.fsync(file.fileno())
                    os.replace(temporary, target)
                finally:
                    if temporary.exists():
                        temporary.unlink()
                cur.execute("update RRL_SAP_RECEIPT_OUTBOX set STATUS='EXPORTED',EXPORTED_AT=systimestamp,FILE_NAME=:f,FILE_HASH=:h,LAST_ERROR=null where EVENT_ID=:i", {"f": name, "i": row[0], "h": sha256(body).hexdigest()})
                exported.append({"event_id": row[0], "file": name, "status": "EXPORTED"})
        return exported
