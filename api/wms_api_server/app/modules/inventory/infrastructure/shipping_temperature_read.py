"""Current warehouse SKU ranges for planning; no vehicle or sensor admission."""
from decimal import Decimal
import oracledb

def read_shipping_temperature_requirements(cur: oracledb.Cursor, member_ids: list[int], actor: str) -> dict:
    if len(member_ids)>5000 or any(isinstance(x,bool) or not isinstance(x,int) or x<1 for x in member_ids):
        raise ValueError("PLAN_THERMAL_SOURCE_BOUND_5000")
    cur.execute("""select WARE_ID,USER_GROUP from RUSERS where ID=:a and nvl(DELETED,0)=0
        and RRL_HAS_WRIGHT(ID,'transport_dispatch_edit')=1""", a=actor)
    user=cur.fetchone()
    if user is None:
        raise PermissionError("PLAN_THERMAL_CURRENT_DISPATCHER_REQUIRED")
    # Bounded IN batches expose actual cardinality. JSON_TABLE's estimate caused
    # a full legacy-row scan even for two selected places in the first live case.
    rows=set()
    for offset in range(0,len(member_ids),200):
        batch=member_ids[offset:offset+200]
        binds={"id"+str(i):value for i,value in enumerate(batch)}
        names=",".join(":"+name for name in binds)
        cur.execute("""select /* CURRENT_ST_SKU_THERMAL1142 */ distinct p.WARE_ID,r.ARTICUL,
            cfg.ARTICUL,to_char(cfg.TEMP_MIN,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''),
            to_char(cfg.TEMP_MAX,'TM9','NLS_NUMERIC_CHARACTERS=''.,''')
            from RRL_SBORKA_PALLETS p
            left join RRL_SBORKA_PALLET_ROWS r on r.PALLET_UID=p.PALLET_UID
            left join RRL_RECEIPT_SKU_RULE cfg on cfg.WARE_ID=p.WARE_ID and cfg.ARTICUL=r.ARTICUL
            where p.ID in ("""+names+") order by p.WARE_ID,r.ARTICUL fetch first 1001 rows only",binds)
        current=cur.fetchall()
        rows.update(current)
        if len(current)>1000 or len(rows)>1000:
            raise ValueError("PLAN_THERMAL_SKU_BOUND_1000")
    raw=sorted(rows,key=lambda row:(row[0] is None,row[0] or 0,row[1] or ""))
    global_scope=str(user[1] or "").strip().upper()=="GLOBAL_ADMIN"
    if any(w is None or (not global_scope and w!=user[0]) for w,*_ in raw):
        raise PermissionError("PLAN_THERMAL_CURRENT_WARE_REQUIRED")
    items=[];lower=[];upper=[]
    for ware,article,found,lo,hi in raw:
        status="CURRENT_RANGE"
        if article is None:
            status="SOURCE_ARTICLE_MISSING"
        elif found is None:
            status="RULE_NOT_CONFIGURED"
        elif lo is None and hi is None:
            status="NO_RANGE_CONFIGURED"
        elif lo is not None and hi is not None and Decimal(lo)>Decimal(hi):
            status="CURRENT_RANGE_INVALID"
        if status=="CURRENT_RANGE":
            if lo is not None:lower.append(Decimal(lo))
            if hi is not None:upper.append(Decimal(hi))
        items.append({"warehouse_id":int(ware),"articul":article,"temp_min_c":lo,"temp_max_c":hi,"status":status})
    lo=max(lower) if lower else None
    hi=min(upper) if upper else None
    conflict=lo is not None and hi is not None and lo>hi
    return {"basis":"CURRENT_WAREHOUSE_SKU_RULE","items":items,
            "common_min_c":str(lo) if lo is not None else None,"common_max_c":str(hi) if hi is not None else None,
            "ranges_conflict":conflict,"all_ranges_configured":bool(items) and all(x["status"]=="CURRENT_RANGE" for x in items),
            "vehicle_temperature_verified":False,"sensor_temperature_verified":False,
            "operational_admission":False}
