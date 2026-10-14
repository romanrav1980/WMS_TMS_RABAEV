"""Expose existing Oracle QC; successful control grants approval for separate loading."""
import json
from hashlib import sha256
from typing import Any
from fastapi import HTTPException
import oracledb
from ..domain.mark_identity import canonical_mark
from ..contracts_stock import StockCommand,StockPostingError
from ...platform.public import read_oracle_json
from .stock_posting_uow import StockPosting


class OutgoingQuality:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def status(self, identifier: str, actor: str|None=None) -> dict:
        try:
            if actor is not None:
                with self.gateway.transaction("Current warehouse QC status access")as q:
                    q.execute("set transaction read only")
                    from .quality_identifier import quality_identifier
                    canonical = quality_identifier(q, identifier, actor)
                    q.execute("select RRL_STOCK_QC_GATE.status_json(:p_identifier) from dual",p_identifier=canonical)
                    result = read_oracle_json(q.fetchone()[0])
                    from .quality_transport_read import quality_transport_read
                    result["transport_assignment"] = quality_transport_read(q, canonical, actor)
                    if canonical != identifier:
                        result["requested_identifier"] = identifier
                    return result
            rows = self.gateway.fetch_all(
                "select RRL_STOCK_QC_GATE.status_json(:p_identifier) STATUS_JSON from dual",
                {"p_identifier": identifier})
        except oracledb.DatabaseError as exc:
            if getattr(exc.args[0],"code",None)==20882:raise StockPostingError("OUTGOING_QC_FORBIDDEN","",20882)from exc
            if getattr(exc.args[0],"code",None)==1403:
                raise HTTPException(404,"СТ не найдена") from exc
            raise
        if not rows or rows[0].get("status_json") is None:
            raise HTTPException(404,"СТ не найдена")
        value = rows[0]["status_json"]
        return value if isinstance(value, dict) else json.loads(value)

    def check(self, identifier: str, body: dict, actor: str) -> dict:
        metadata = {key: value for key, value in body.items() if key != "operation_id"}
        raw_scans = metadata.pop("scans",None)
        if raw_scans is not None:
            normalized = []
            for scan in raw_scans:
                try:
                    identity = canonical_mark(scan["system_code"],scan["profile_code"],scan["code"])["identity"]
                except ValueError as exc:
                    raise HTTPException(422,str(exc)) from exc
                normalized.append({"system_code":scan["system_code"],"profile_code":scan["profile_code"],
                                   "code_hash":sha256(identity.encode("utf-8")).hexdigest()})
            metadata["unit_scans"] = normalized
        return StockPosting().post(StockCommand(
            operation_id=body["operation_id"], command_type="OUTGOING_PALLET_CHECK",
            actor=actor, source={"pallet_identifier": identifier}, lines=(),
            metadata=metadata,
        ))


    def check_final(self,identifier:str,body:dict,actor:str)->dict:
        try:
            with self.gateway.transaction("Immutable whole CASE final scale source")as q:
                q.execute("set transaction read only")
                q.callproc("RRL_OUTGOING_QC_ACCESS.assert_identifier",[identifier,actor])
                q.execute("select RESULT_JSON from RRL_WH_SCALE_CAPTURE where CAPTURE_KEY=:p_key and CAPTURE_PURPOSE='FINAL_GROSS'",p_key=body["capture_key"])
                row=q.fetchone()
                if row is None:raise StockPostingError("FINAL_SCALE_CAPTURE_NOT_FOUND",body["operation_id"],20886)
                original=read_oracle_json(row[0])
        except oracledb.DatabaseError as exc:
            error=exc.args[0]
            raise StockPostingError("FINAL_SCALE_READ_REJECTED"if 20800<=error.code<=20899 else"RESULT_UNCERTAIN",body["operation_id"],error.code,str(error).split("\n")[0])from exc
        metadata={key:value for key,value in body.items()if key!="capture_key"}
        metadata.update(quality_kind="WEIGHT",gross_weight=original["weight_kg"],wood_weight=original["tare_weight_kg"],final_scale_capture=body["capture_key"])
        return self.check(identifier,metadata,actor)


    def final_readings(self,identifier:str,actor:str)->dict:
        try:
            with self.gateway.transaction("Current QC whole CASE final scale readings")as q:
                q.execute("set transaction read only")
                q.callproc("RRL_OUTGOING_QC_ACCESS.assert_identifier",[identifier,actor])
                q.execute("select c.CASE_PICK_TASK_ID,c.CONTENT_VERSION from RRL_CASE_PICK_TASK c join RRL_SBORKA_PALLETS s on s.ID=c.LEGACY_SBORKA_PALLET_ID where s.PALLET_UID=:p_id",p_id=identifier)
                case=q.fetchone()
                if case is None:return {"items":[],"has_older":False,"use_by_capture":{}}
                q.execute("select c.RESULT_JSON,c.CAPTURE_KEY,u.STOCK_OPERATION_ID from(select RESULT_JSON,CAPTURE_KEY,RECEIVED_AT from RRL_WH_SCALE_CAPTURE where CASE_PICK_TASK_ID=:p_task and CAPTURE_PURPOSE='FINAL_GROSS' order by RECEIVED_AT desc,CAPTURE_KEY desc fetch first 51 rows only)c left join RRL_WH_FINAL_SCALE_USE u on u.CAPTURE_KEY=c.CAPTURE_KEY order by c.RECEIVED_AT desc,c.CAPTURE_KEY desc",p_task=case[0])
                rows=q.fetchall()
                return {"case_task_id":int(case[0]),"case_content_version":int(case[1]),"items":[read_oracle_json(row[0])for row in rows[:50]],"has_older":len(rows)>50,"use_by_capture":{row[1]:{"operation_id":row[2]}for row in rows[:50]if row[2]is not None}}
        except oracledb.DatabaseError as exc:
            error=exc.args[0]
            raise StockPostingError("FINAL_SCALE_READ_REJECTED"if 20800<=error.code<=20899 else"RESULT_UNCERTAIN","",error.code,str(error).split("\n")[0])from exc
