"""Reuse physical mark capture for declared inventory and MES lot birth, without a SAP order."""
from decimal import Decimal
from hashlib import sha256
import json
from .receiving_marks import ReceivingMarks
from ..domain.mark_identity import canonical_mark


def plan_births(cursor, document):
    kind=document["command_type"];meta=document["metadata"]
    if kind=="INVENTORY_REGISTER_LOT":
        candidates=[(meta["uid"],meta["article"],meta["cell"],meta["quantity"],None,None)]
    elif kind=="MES_MOVEMENTS":
        candidates=[]
        for movement_id in document["source"]["movement_ids"]:
            cursor.execute("select m.UID_PALLET,o.TARGET_ARTICUL,m.TARGET_LOCATION,to_char(m.QUANTITY,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''),m.UNIT_CODE "
                           "from RRL_MES_MOVEMENT m join RRL_PRODUCTION_ORDER o "
                           "on o.PRODUCTION_ORDER_ID=m.PRODUCTION_ORDER_ID "
                           "where m.MOVEMENT_ID=:id and m.MOVEMENT_TYPE='FG_PALLET_RELEASE'",id=movement_id)
            row=cursor.fetchone()
            if row:candidates.append((*row,movement_id))
    else:return {"births":[]},{}
    births=[];captures={};provided=meta.get("birth_captures",{})
    if set(provided)-{row[0] for row in candidates}:raise ValueError("Capture belongs to another physical lot")
    for uid,article,cell,quantity,input_uom,movement_id in candidates:
        cursor.execute("select greatest(nvl((select MARKING_REQUIRED from RRL_SKU_RECEIPT_POLICY where ARTICUL=:a),0),"
                       "nvl((select CRPT_REQUIRED from RRL_FINISHED_GOODS_SKU where ARTICUL=:a),0),"
                       "case when exists(select 1 from RRL_SKU_RECEIPT_PROFILE where ARTICUL=:a) then 1 else 0 end) from dual",a=article)
        marked=cursor.fetchone()[0]
        if not marked:
            if uid in provided:raise ValueError("Unmarked lot cannot contain marking capture")
            continue
        if uid not in provided:raise ValueError("Unique unit capture is required for marked lot "+uid)
        cursor.execute("select BASE_UOM,NUMERATOR,DENOMINATOR,BASE_SCALE,POLICY_VERSION "
                       "from RRL_STOCK_UOM_CONVERSION where ARTICUL=:a and "
                       "((:u is not null and INPUT_UOM=:u) or (:u is null and INPUT_UOM=BASE_UOM and NUMERATOR=1 and DENOMINATOR=1)) "
                       "order by POLICY_VERSION desc",a=article,u=input_uom)
        policies=cursor.fetchall()
        if not policies or (input_uom is None and len({r[0] for r in policies})!=1):raise ValueError("Unambiguous base policy required")
        base,num,den,scale,version=policies[0]
        from ..domain.stock_quantity import convert_exact
        qbase=convert_exact(str(quantity),int(num),int(den),int(scale))
        payload={**provided[uid],"units":provided[uid].get("units",[]),"aggregations":provided[uid].get("aggregations",[])}
        marks=ReceivingMarks(cursor).resolve("STOCK.BIRTH",article,str(movement_id or ""),qbase,payload,base,lock_policy=False)
        cursor.execute("select nvl(f.GTIN,a.BARCODE_SHT) from RRL_ARTICULS a left join "
                       "RRL_FINISHED_GOODS_SKU f on f.ARTICUL=a.ACTICUL where a.ACTICUL=:a",a=article)
        gtin=str(cursor.fetchone()[0]).zfill(14)
        bindings=[];aliases={}
        for unit_id,codes in marks["units"].items():
            identities=[]
            for profile,code in codes.items():
                normalized=canonical_mark(*profile,code,gtin if profile[0]=="CRPT" else None)
                digest=sha256(normalized["identity"].encode()).hexdigest()
                key=(profile[0],digest)
                if key in aliases and aliases[key]["unit_id"]!=unit_id:raise ValueError("One code identifies multiple physical units")
                aliases[key]={"system":profile[0],"hash":digest,"unit_id":unit_id}
                identities.append(profile[0]+":"+normalized["identity"])
            bindings.append({"unit_id":unit_id,"key":sha256(min(identities).encode()).hexdigest(),
                             "quantity":format(marks["unit_quantities"][unit_id],"f")})
        if len({b["key"] for b in bindings})!=len(bindings):raise ValueError("Duplicate physical unit")
        births.append({"uid":uid,"article":article,"cell":cell,"quantity":format(qbase,"f"),"base":base,
                       "policy_version":marks["policy_version"],"unit_bindings":bindings,"aliases":list(aliases.values()),
                       "movement_id":movement_id})
        captures[uid]=marks
        if sum(len(b["unit_bindings"]) for b in births)>10000:raise ValueError("At most 10000 physical units per birth command")
    return {"births":births},captures


def stage_births(cursor,document,captures):
    cursor.execute("select RESOLVED_PLAN_JSON from RRL_STOCK_OPERATION where OPERATION_ID=:id",id=document["operation_id"])
    raw=cursor.fetchone()[0];plan=json.loads(raw.read() if hasattr(raw,"read") else raw)
    for birth in plan.get("births",[]):
        cursor.execute("begin RRL_STOCK_POSTING_API.stage_birth(:uid); end;",uid=birth["uid"])
        ReceivingMarks(cursor).persist(birth["uid"],captures[birth["uid"]],document["actor"],
            bindings=birth["unit_bindings"],base_uom=birth["base"],cell=birth["cell"],
            source_kind="INVENTORY_BIRTH" if document["command_type"]=="INVENTORY_REGISTER_LOT" else "PRODUCTION_RELEASE")
        cursor.execute("begin RRL_STOCK_POSTING_API.finish_birth_capture; end;")
