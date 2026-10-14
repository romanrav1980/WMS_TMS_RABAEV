"""Immutable non-SAP sender proof; native birth remains the sole unit/stock writer."""
from __future__ import annotations
from decimal import Decimal
from hashlib import sha256
from typing import Any
import json
import oracledb
from ...platform.public import read_oracle_json
from ..contracts_trace_manifest import TraceManifestError
from ..domain.trace_manifest import parse_manifest,validate_units,resolve_aggregates
from .metadata_transactions import receipt_task_metadata

class TraceSenderManifest:
    def __init__(self,gateway: Any) -> None:
        self.gateway=gateway

    def import_manifest(self,operation_id: str,raw: str,actor: str) -> dict[str,Any]:
        try:
            document=parse_manifest(raw)
            digest=sha256(json.dumps([raw,actor],ensure_ascii=False,separators=(",",":")).encode()).digest()
            with receipt_task_metadata(self.gateway,"Non-SAP sender aggregation evidence",actor,"trace_manifest_import") as cur:
                self._scope(cur,document["warehouse_id"],actor)
                cur.execute("select PAYLOAD_HASH,RESULT_JSON from RRL_TRACE_SENDER_MANIFEST where OPERATION_ID=:op",op=operation_id)
                old=cur.fetchone()
                if old:
                    if old[0]!=digest:
                        raise TraceManifestError("TRACE_MANIFEST_PAYLOAD_CONFLICT","Operation content changed")
                    return read_oracle_json(old[1])
                cur.execute("select POLICY_VERSION,MARKING_REQUIRED from RRL_SKU_RECEIPT_POLICY where ARTICUL=:article",article=document["article"])
                policy=cur.fetchone()
                if not policy or policy!=(document["policy_version"],1):
                    raise TraceManifestError("TRACE_MANIFEST_POLICY_CHANGED","Current marked WMS policy required")
                cur.execute("select SYSTEM_CODE,PROFILE_CODE,PROFILE_VERSION,SCAN_MODE from RRL_SKU_RECEIPT_PROFILE where ARTICUL=:article order by SYSTEM_CODE,PROFILE_CODE",article=document["article"])
                profiles={(r[0],r[1]):{"version":r[2],"mode":r[3]}for r in cur.fetchmany(51)}
                if not 1<=len(profiles)<=50:
                    raise TraceManifestError("TRACE_MANIFEST_PROFILE_BOUND","Current 1..50 profiles required")
                cur.execute("select nvl(f.GTIN,a.BARCODE_SHT)from RRL_ARTICULS a left join RRL_FINISHED_GOODS_SKU f on f.ARTICUL=a.ACTICUL where a.ACTICUL=:article",article=document["article"])
                article_row=cur.fetchone()
                if not article_row:
                    raise TraceManifestError("TRACE_MANIFEST_ARTICLE_REQUIRED","Existing article required")
                units=validate_units(document,profiles,str(article_row[0]).zfill(14))
                aggregates=resolve_aggregates(document,units,profiles)
                quantity=sum((Decimal(item["quantity"])for item in units.values()),Decimal(0))
                result={"operation_id":operation_id,"status":"IMPORTED_EVIDENCE","warehouse_id":document["warehouse_id"],"pallet_identifier":document["pallet_identifier"],"article":document["article"],"base_uom":document["base_uom"],"quantity":format(quantity,"f"),"physical_unit_count":len(units),"aggregate_count":len(aggregates),"source_kind":document["source_kind"],"source_document_id":document["source_document_id"],"raw_sha256":sha256(raw.encode()).hexdigest(),"stock_changed":False,"government_ack_created":False}
                self._persist(cur,operation_id,digest,raw,document,profiles,aggregates,quantity,result,actor)
                return result
        except (ValueError,TypeError,KeyError) as exc:
            raise TraceManifestError("TRACE_MANIFEST_INVALID",str(exc),422) from exc
        except oracledb.DatabaseError as exc:
            code=getattr(exc.args[0],"code",0)
            if code==1 or 20800<=code<=20999:
                raise TraceManifestError("TRACE_MANIFEST_REJECTED",str(exc.args[0]).split("\n",1)[0],403 if code==20882 else 409) from exc
            raise TraceManifestError("TRACE_MANIFEST_RESULT_UNCONFIRMED","Repeat original operation after technical failure",503) from exc

    @staticmethod
    def _scope(cur: Any,ware: int,actor: str) -> None:
        cur.execute("select count(*)from RUSERS where ID=:actor and nvl(DELETED,0)=0 and(WARE_ID=:ware or upper(trim(USER_GROUP))='GLOBAL_ADMIN')",actor=actor,ware=ware)
        if cur.fetchone()[0]!=1:
            raise TraceManifestError("TRACE_MANIFEST_WARE_FORBIDDEN","Current warehouse binding required",403)

    @staticmethod
    def _persist(cur: Any,op: str,digest: bytes,raw: str,document: dict[str,Any],profiles: dict[tuple[str,str],dict[str,Any]],aggregates: list[dict[str,Any]],quantity: Decimal,result: dict[str,Any],actor: str) -> None:
        cur.setinputsizes(profiles=oracledb.DB_TYPE_CLOB,raw_body=oracledb.DB_TYPE_CLOB,result_body=oracledb.DB_TYPE_CLOB)
        cur.execute("""insert into RRL_TRACE_SENDER_MANIFEST(OPERATION_ID,PAYLOAD_HASH,SOURCE_KIND,SOURCE_DOC_ID,WARE_ID,UID_PALLET,ARTICLE,BASE_UOM,DECLARED_BASE_QTY,POLICY_VERSION,PROFILES_JSON,RAW_JSON,RAW_SHA256,DOCUMENT_REFERENCE,ACTOR,RESULT_JSON)values(:op,:digest,:source_kind,:doc,:ware,:lot_id,:article,:base,:qty,:policy,:profiles,:raw_body,:raw_hash,:reference,:actor,:result_body)""",op=op,digest=digest,source_kind=document["source_kind"],doc=document["source_document_id"],ware=document["warehouse_id"],lot_id=document["pallet_identifier"],article=document["article"],base=document["base_uom"],qty=quantity,policy=document["policy_version"],profiles=json.dumps([{"system_code":key[0],"profile_code":key[1],**value}for key,value in sorted(profiles.items())]),raw_body=raw,raw_hash=result["raw_sha256"],reference=document["document_reference"],actor=actor,result_body=json.dumps(result))
        for aggregate in aggregates:
            cur.setinputsizes(code_body=oracledb.DB_TYPE_CLOB,units_body=oracledb.DB_TYPE_CLOB)
            cur.execute("""insert into RRL_TRACE_SENDER_AGG(MANIFEST_OPERATION_ID,AGGREGATION_ID,SYSTEM_CODE,PROFILE_CODE,PROFILE_VERSION,AGG_LEVEL,CODE_HASH,RAW_CODE,UNITS_JSON)values(:op,:agg_id,:system_code,:profile_code,:profile_version,:agg_level,:code_hash,:code_body,:units_body)""",op=op,agg_id=aggregate["aggregation_id"],system_code=aggregate["system_code"],profile_code=aggregate["profile_code"],profile_version=profiles[(aggregate["system_code"],aggregate["profile_code"])]["version"],agg_level=aggregate["level"],code_hash=aggregate["code_hash"],code_body=aggregate["code"],units_body=json.dumps(aggregate["units"]))

    def list(self,ware_id: int,actor: str) -> list[dict[str,Any]]:
        with self.gateway.transaction("Scoped sender evidence queue") as cur:
            self._scope(cur,ware_id,actor)
            cur.execute("""select m.OPERATION_ID,m.SOURCE_KIND,m.SOURCE_DOC_ID,m.UID_PALLET PALLET_IDENTIFIER,m.ARTICLE,m.BASE_UOM,to_char(m.DECLARED_BASE_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') QUANTITY,m.POLICY_VERSION,m.RAW_SHA256,m.DOCUMENT_REFERENCE,m.ACTOR,u.STOCK_OPERATION_ID from RRL_TRACE_SENDER_MANIFEST m left join RRL_TRACE_MANIFEST_USE u on u.MANIFEST_OPERATION_ID=m.OPERATION_ID where m.WARE_ID=:ware order by m.CREATED_AT,m.OPERATION_ID fetch first 100 rows only""",ware=ware_id)
            names=[column[0].lower()for column in cur.description]
            return [dict(zip(names,row))for row in cur.fetchall()]

    def capture_context(self,kind: str,document_id: int,article: str,cell: str,pallet: str,actor: str) -> dict[str,Any]:
        from .trace_capture_context import capture_context
        return capture_context(self.gateway,kind,document_id,article,cell,pallet,actor)

    def invalidate_aggregate(self,operation_id: str,request: dict[str,Any],actor: str) -> dict[str,Any]:
        from .trace_aggregation_lifecycle import TraceAggregationLifecycle
        return TraceAggregationLifecycle(self.gateway).invalidate(operation_id,request,actor)

    def aggregates(self,origin: str,ware: int,actor: str) -> list[dict[str,Any]]:
        from .trace_aggregation_lifecycle import TraceAggregationLifecycle
        return TraceAggregationLifecycle(self.gateway).list(origin,ware,actor)
