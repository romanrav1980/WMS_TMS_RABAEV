import json
from uuid import uuid4

import oracledb

from ....oracle_gateway import OracleGateway
from ..application.ingestion import IdocConflict


class ArtmasInbox:
    def __init__(self, gateway: OracleGateway) -> None:
        self.gateway = gateway

    def receive(self, envelope: dict, actor: str) -> dict:
        previous = self._find(envelope["sender"], envelope["docnum"])
        if previous:
            return self._repeat(previous, envelope)
        inbox_id = uuid4().hex
        parsed = {k: v for k, v in envelope.items() if k != "raw_xml"}
        try:
            with self.gateway.transaction("NI01 receive SAP ARTMAS10") as cursor:
                cursor.setinputsizes(raw_xml=oracledb.DB_TYPE_CLOB, parsed=oracledb.DB_TYPE_CLOB)
                cursor.execute(
                    """insert into RRL_SAP_IDOC_INBOX
                         (INBOX_ID,SENDER,DOCNUM,MESSAGE_TYPE,BASIC_TYPE,EXTENSION_TYPE,
                          PAYLOAD_HASH,RAW_XML,PARSED_JSON,STATUS,RECEIVED_BY)
                         values (:id,:sender,:docnum,'ARTMAS','ARTMAS10',:ext,
                                 :hash,:raw_xml,:parsed,'RECEIVED',:actor)""",
                    {"id": inbox_id, "sender": envelope["sender"], "docnum": envelope["docnum"],
                     "ext": envelope["extension"], "hash": envelope["payload_hash"],
                     "raw_xml": envelope["raw_xml"], "parsed": json.dumps(parsed, ensure_ascii=False), "actor": actor})
        except oracledb.IntegrityError as exc:
            if exc.args[0].code != 1:
                raise
            previous = self._find(envelope["sender"], envelope["docnum"])
            if not previous:
                raise
            return self._repeat(previous, envelope)
        return {"inbox_id": inbox_id, "status": "RECEIVED", "idempotent": False,
                "articles_applied": False, "materials": envelope["materials"]}

    def _find(self, sender: str, docnum: str) -> dict | None:
        rows = self.gateway.fetch_all(
            "select INBOX_ID,STATUS,PAYLOAD_HASH from RRL_SAP_IDOC_INBOX where SENDER=:s and DOCNUM=:d",
            {"s": sender, "d": docnum})
        return rows[0] if rows else None

    def _repeat(self, old: dict, envelope: dict) -> dict:
        if old["payload_hash"] != envelope["payload_hash"]:
            raise IdocConflict("Sender/DOCNUM already received with a different payload.")
        return {"inbox_id": old["inbox_id"], "status": old["status"],
                "idempotent": True, "articles_applied": old["status"] == "APPLIED", "materials": envelope["materials"]}

    def get(self, inbox_id: str) -> dict:
        rows = self.gateway.fetch_all(
            """select INBOX_ID,SENDER,DOCNUM,MESSAGE_TYPE,BASIC_TYPE,EXTENSION_TYPE,
                       STATUS,PARSED_JSON,RESULT_JSON,LAST_ERROR,RECEIVED_AT,RECEIVED_BY
                  from RRL_SAP_IDOC_INBOX where INBOX_ID=:id""", {"id": inbox_id})
        if not rows:
            raise LookupError("IDoc inbox entry not found.")
        return rows[0]
