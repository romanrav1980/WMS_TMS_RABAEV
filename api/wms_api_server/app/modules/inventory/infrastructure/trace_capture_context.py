"""Read current source and SKU profiles for physical unit scanning."""
from typing import Any
from ..contracts_trace_manifest import TraceManifestError

def capture_context(gateway: Any,kind: str,document_id: int,article: str,cell: str,pallet: str,actor: str) -> dict[str,Any]:
    with gateway.transaction("Current physical mark capture context") as cur:
        if kind=="INVENTORY":
            cur.execute("select r.WARE_ID from RRL_REVIZION r join RRL_CELLS c on c.WARE_ID=r.WARE_ID where r.ID=:doc and r.CONDITION in(0,1)and c.CELL=:cell",doc=document_id,cell=cell)
        else:
            cur.execute("select c.WARE_ID from RRL_MES_MOVEMENT m join RRL_PRODUCTION_ORDER p on p.PRODUCTION_ORDER_ID=m.PRODUCTION_ORDER_ID join RRL_CELLS c on c.CELL=m.TARGET_LOCATION where m.MOVEMENT_ID=:doc and m.MOVEMENT_TYPE='FG_PALLET_RELEASE' and m.UID_PALLET=:lot_id and p.TARGET_ARTICUL=:article and c.CELL=:cell and c.WARE_ID=p.WARE_ID and m.STATUS in('MES_POSTED','ERROR')",doc=document_id,lot_id=pallet,article=article,cell=cell)
        rows=cur.fetchmany(2)
        if len(rows)!=1:
            raise TraceManifestError("TRACE_CAPTURE_SOURCE_REQUIRED","Current source/pallet/cell required")
        ware=int(rows[0][0])
        cur.execute("select count(*)from RUSERS where ID=:actor and nvl(DELETED,0)=0 and(WARE_ID=:ware or upper(trim(USER_GROUP))='GLOBAL_ADMIN')",actor=actor,ware=ware)
        if cur.fetchone()[0]!=1:
            raise TraceManifestError("TRACE_CAPTURE_WARE_FORBIDDEN","Current warehouse actor required",403)
        cur.execute("select POLICY_VERSION,MARKING_REQUIRED from RRL_SKU_RECEIPT_POLICY where ARTICUL=:article",article=article)
        policy=cur.fetchone()
        if not policy or policy[1]!=1:
            raise TraceManifestError("TRACE_CAPTURE_MARKED_POLICY_REQUIRED","Current marked WMS policy required")
        cur.execute("select SYSTEM_CODE,PROFILE_CODE,PROFILE_VERSION,SCAN_MODE from RRL_SKU_RECEIPT_PROFILE where ARTICUL=:article order by SYSTEM_CODE,PROFILE_CODE",article=article)
        rows=cur.fetchmany(51)
        if not 1<=len(rows)<=50:
            raise TraceManifestError("TRACE_CAPTURE_PROFILE_BOUND","1..50 current profiles required")
        profiles=[{"system_code":r[0],"profile_code":r[1],"version":r[2],"mode":r[3]}for r in rows]
        cur.execute("select distinct BASE_UOM from RRL_STOCK_UOM_CONVERSION where ARTICUL=:article and INPUT_UOM=BASE_UOM and NUMERATOR=1 and DENOMINATOR=1",article=article)
        bases=cur.fetchmany(2)
        if len(bases)!=1:
            raise TraceManifestError("TRACE_CAPTURE_BASE_REQUIRED","Unambiguous native base unit required")
        return {"source_kind":kind,"source_document_id":document_id,"warehouse_id":ware,"article":article,"cell":cell,"pallet_identifier":pallet,"base_uom":bases[0][0],"policy_version":int(policy[0]),"profile_versions":profiles,"government_validation":"NOT_PERFORMED"}
