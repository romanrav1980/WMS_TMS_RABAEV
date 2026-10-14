"""Local physical invalidation; quantities and government statuses retain their owners."""
import json
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ..contracts_trace_manifest import TraceManifestError
from .metadata_transactions import receipt_task_metadata


class TraceAggregationLifecycle:
    def __init__(self,gateway: Any)->None:
        self.gateway=gateway

    def invalidate(self,operation_id: str,request: dict[str,Any],actor: str)->dict[str,Any]:
        wire=json.dumps(request,sort_keys=True,separators=(",",":"),ensure_ascii=False)
        try:
            with receipt_task_metadata(self.gateway,"Invalidate a physical aggregate",actor,"trace_manifest_import")as q:
                q.setinputsizes(body=oracledb.DB_TYPE_CLOB)
                result=q.var(oracledb.DB_TYPE_CLOB)
                q.execute("begin :result:=RRL_TRACE_AGG_LIFECYCLE.invalidate(:op,:body,:actor);end;",
                          result=result,op=operation_id,body=wire,actor=actor)
                return read_oracle_json(result.getvalue())
        except oracledb.DatabaseError as exc:
            code=getattr(exc.args[0],"code",0)
            if code==1 or 20800<=code<=20999:
                raise TraceManifestError("TRACE_AGG_INVALIDATION_REJECTED",str(exc.args[0]).split("\n",1)[0],403 if code==20882 else 409)from exc
            raise TraceManifestError("TRACE_AGG_INVALIDATION_UNCONFIRMED","Repeat the same operation after a technical failure",503)from exc

    def list(self,origin: str,ware: int,actor: str)->list[dict[str,Any]]:
        with self.gateway.transaction("Warehouse-scoped aggregate lifecycle")as q:
            q.execute("set transaction read only")
            q.execute("""select count(*)from RUSERS where ID=:actor and nvl(DELETED,0)=0
                and(WARE_ID=:ware or upper(trim(USER_GROUP))='GLOBAL_ADMIN')
                and RRL_HAS_WRIGHT(ID,'traceability_view')=1""",actor=actor,ware=ware)
            if q.fetchone()[0]!=1:
                raise TraceManifestError("TRACE_AGG_WARE_FORBIDDEN","Current warehouse access required",403)
            q.execute("""select count(*)from RRL_WMS_RECEIPT_UNIT u join RRL_CELLS c on c.CELL=u.CURRENT_CELL
                where u.UID_PALLET=:origin and c.WARE_ID=:ware""",origin=origin,ware=ware)
            if q.fetchone()[0]==0:
                raise TraceManifestError("TRACE_AGG_LOCAL_ORIGIN_REQUIRED","Origin has no physical unit location in this warehouse",404)
            q.execute("""with aggregates as(
 select SYSTEM_CODE,PROFILE_CODE,CODE_HASH,AGG_LEVEL from RRL_WMS_RECEIPT_AGG where UID_PALLET=:origin
 union
 select a.SYSTEM_CODE,a.PROFILE_CODE,a.CODE_HASH,a.AGG_LEVEL from RRL_TRACE_SENDER_AGG a
 join RRL_TRACE_MANIFEST_USE u on u.MANIFEST_OPERATION_ID=a.MANIFEST_OPERATION_ID
 join RRL_STOCK_OPERATION op on op.OPERATION_ID=u.STOCK_OPERATION_ID and op.STATE='APPLIED'
 where u.UID_PALLET=:origin
 union
 select a.SYSTEM_CODE,a.PROFILE_CODE,a.CODE_HASH,a.AGG_LEVEL from RRL_SAP_TRACE_AGG a
 join RRL_SAP_PALLET_RECEIPT r on r.ORDER_ID=a.ORDER_ID and r.LINE_NUMBER=a.LINE_NUMBER
 join RRL_STOCK_OPERATION op on op.OPERATION_ID=r.STOCK_OPERATION_ID and op.STATE='APPLIED'and op.COMMAND_TYPE='SAP_RECEIPT'
 where r.UID_PALLET=:origin and r.POSTED_BASE_QTY>0)
 select a.SYSTEM_CODE,a.PROFILE_CODE,a.CODE_HASH,a.AGG_LEVEL,
                i.OPERATION_ID,i.REASON_CODE,i.DOCUMENT_REFERENCE,i.ACTOR,i.JOURNAL_ID,
                to_char(i.CREATED_AT,'YYYY-MM-DD"T"HH24:MI:SSTZH:TZM')
                from aggregates a left join RRL_TRACE_AGG_BLOCK b
                on b.SYSTEM_CODE=a.SYSTEM_CODE and b.PROFILE_CODE=a.PROFILE_CODE and b.CODE_HASH=a.CODE_HASH
                left join RRL_TRACE_AGG_INVALIDATION i on i.OPERATION_ID=b.INVALIDATION_OPERATION_ID
                order by a.SYSTEM_CODE,a.PROFILE_CODE,a.CODE_HASH
                fetch first 1001 rows only""",origin=origin)
            rows=q.fetchmany(1001)
            if len(rows)>1000:
                raise TraceManifestError("TRACE_AGG_READ_BOUND","Aggregate count exceeds the explicit 1000 limit")
            keys=("system_code","profile_code","code_hash","level","invalidation_operation_id",
                  "reason_code","document_reference","actor","journal_id","invalidated_at")
            result=[]
            for row in rows:
                item=dict(zip(keys,row))
                item.update(origin_pallet_identifier=origin,warehouse_id=ware,
                            local_state="INVALIDATED"if row[4]else"REGISTERED_EVIDENCE",
                            scan_admission_verified=False,government_ack_verified=False)
                result.append(item)
            return result
