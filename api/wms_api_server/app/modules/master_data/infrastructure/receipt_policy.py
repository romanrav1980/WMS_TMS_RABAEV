from ...inventory.infrastructure.configuration_uow import configuration_transaction
import json
import oracledb

from ....oracle_gateway import OracleGateway
from ..contracts import ReceiptPolicyUpdate
from ..application.policy import PolicyConflict


class ReceiptPolicyRepository:
    def __init__(self, gateway: OracleGateway) -> None:
        self.gateway = gateway

    def get(self, articul: str) -> dict:
        rows = self.gateway.fetch_all(
            """select a.ROWID LEGACY_ROW_ID, a.ACTICUL, p.POLICY_VERSION, p.MARKING_REQUIRED,
                      nvl(s.CRPT_REQUIRED,0) LEGACY_CRPT_REQUIRED,
                      r.SYSTEM_CODE,r.PROFILE_CODE,r.PROFILE_VERSION,r.SCAN_MODE
                 from RRL_ARTICULS a
                 left join RRL_SKU_RECEIPT_POLICY p on p.ARTICUL=a.ACTICUL
                 left join RRL_FINISHED_GOODS_SKU s on s.ARTICUL=a.ACTICUL
                 left join RRL_SKU_RECEIPT_PROFILE r on r.ARTICUL=a.ACTICUL
                where a.ACTICUL=:articul
                order by r.SYSTEM_CODE,r.PROFILE_CODE""", {"articul": articul})
        if not rows or len({r["legacy_row_id"] for r in rows}) != 1:
            raise LookupError("SKU not found or legacy key is ambiguous.")
        row = rows[0]
        profiles = [{key: r[key] for key in ("system_code", "profile_code", "profile_version", "scan_mode")}
                    for r in rows if r["system_code"] is not None]
        configured = row["policy_version"] is not None
        expected_crpt = int(any(p["system_code"] == "CRPT" for p in profiles))
        return {"articul": articul, "version": int(row["policy_version"] or 0),
                "configured": configured,
                "marking_required": bool(row["marking_required"] if configured else row["legacy_crpt_required"]),
                "profiles": profiles,
                "legacy_mismatch": configured and expected_crpt != int(row["legacy_crpt_required"]),
                "unmarked_scan_modes": ["ITEM_BARCODE", "BOX_BARCODE"]}

    def replace(self, articul: str, request: ReceiptPolicyUpdate, actor: str) -> dict:
        with configuration_transaction(self.gateway, "NI01 save SKU receiving policy", actor, "finished_goods_edit") as cursor:
            cursor.execute("select ACTICUL from RRL_ARTICULS where ACTICUL=:a for update", {"a": articul})
            if len(cursor.fetchall()) != 1:
                raise LookupError("SKU not found or legacy key is ambiguous.")
            cursor.execute("select POLICY_VERSION from RRL_SKU_RECEIPT_POLICY where ARTICUL=:a", {"a": articul})
            old = cursor.fetchone()
            version = int(old[0]) if old else 0
            if version != request.expected_version:
                raise PolicyConflict("SKU policy changed. Reload before saving.")
            params = {"a": articul, "v": version + 1, "m": int(request.marking_required), "actor": actor}
            cursor.execute(
                """merge into RRL_SKU_RECEIPT_POLICY d using (select :a ARTICUL from dual) s
                    on (d.ARTICUL=s.ARTICUL)
                    when matched then update set POLICY_VERSION=:v, MARKING_REQUIRED=:m,
                         UPDATED_AT=systimestamp, UPDATED_BY=:actor
                    when not matched then insert (ARTICUL,POLICY_VERSION,MARKING_REQUIRED,UPDATED_AT,UPDATED_BY)
                         values (:a,:v,:m,systimestamp,:actor)""", params)
            cursor.execute("delete from RRL_SKU_RECEIPT_PROFILE where ARTICUL=:a", {"a": articul})
            for profile in request.profiles:
                cursor.execute(
                    """insert into RRL_SKU_RECEIPT_PROFILE
                         (ARTICUL,SYSTEM_CODE,PROFILE_CODE,PROFILE_VERSION,SCAN_MODE)
                         values (:a,:system_code,:profile_code,:profile_version,:scan_mode)""",
                    {"a": articul, **profile.model_dump()})
            crpt = int(any(p.system_code == "CRPT" for p in request.profiles))
            aggregation = int(any(p.scan_mode != "UNIT" for p in request.profiles))
            cursor.execute(
                """merge into RRL_FINISHED_GOODS_SKU d using (select :a ARTICUL from dual) s
                    on (d.ARTICUL=s.ARTICUL)
                    when matched then update set CRPT_REQUIRED=:c, AGGREGATION_REQUIRED=:g,
                         UPDATED_AT=systimestamp,UPDATED_BY=:actor
                    when not matched then insert (ARTICUL,CRPT_REQUIRED,AGGREGATION_REQUIRED,CREATED_BY)
                         values (:a,:c,:g,:actor)""",
                {"a": articul, "c": crpt, "g": aggregation, "actor": actor})
            payload = {"marking_required": request.marking_required,
                       "profiles": [p.model_dump() for p in request.profiles]}
            cursor.setinputsizes(payload=oracledb.DB_TYPE_CLOB)
            cursor.execute(
                """insert into RRL_SKU_RECEIPT_POLICY_LOG
                     (ARTICUL,POLICY_VERSION,POLICY_JSON,CHANGED_BY)
                     values (:a,:v,:payload,:actor)""",
                {"a": articul, "v": version + 1,
                 "payload": json.dumps(payload, ensure_ascii=False), "actor": actor})
        return {"articul": articul, "version": version + 1, "configured": True,
                "marking_required": request.marking_required,
                "profiles": [p.model_dump() for p in request.profiles], "legacy_mismatch": False,
                "unmarked_scan_modes": ["ITEM_BARCODE", "BOX_BARCODE"]}
