"""Evidence readers shared by existing stock birth capture; no second code registry."""
from hashlib import sha256
from typing import Any
from decimal import Decimal
from ...platform.public import read_oracle_json
from ..domain.mark_identity import canonical_mark
from ..domain.unit_quantity import unit_quantity

def source_header(cur: Any,manifest_id: str,uid: str,article: str,base: str,cell: str,source_kind: str,source_doc: int,actor: str,policy_version: int,profiles: dict[tuple[str,str],dict[str,Any]]) -> dict[str,Any]:
    cur.execute("""select m.RAW_JSON,m.PROFILES_JSON,to_char(m.DECLARED_BASE_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''),nvl(f.GTIN,a.BARCODE_SHT) from RRL_TRACE_SENDER_MANIFEST m join RRL_CELLS c on c.WARE_ID=m.WARE_ID join RRL_ARTICULS a on a.ACTICUL=m.ARTICLE left join RRL_FINISHED_GOODS_SKU f on f.ARTICUL=a.ACTICUL where m.OPERATION_ID=:op and m.UID_PALLET=:lot_id and m.ARTICLE=:article and m.BASE_UOM=:base and c.CELL=:cell and m.SOURCE_KIND=:source_kind and m.SOURCE_DOC_ID=:doc and m.POLICY_VERSION=:policy and exists(select 1 from RUSERS u where u.ID=:actor and nvl(u.DELETED,0)=0 and(u.WARE_ID=m.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN'))""",op=manifest_id,lot_id=uid,article=article,base=base,cell=cell,source_kind=source_kind,doc=source_doc,policy=policy_version,actor=actor)
    row=cur.fetchone()
    if not row:
        raise ValueError("Sender manifest belongs to another pallet/SKU/warehouse/source/policy")
    saved={(item["system_code"],item["profile_code"]):{"version":item["version"],"mode":item["mode"]}for item in read_oracle_json(row[1])}
    if saved!=profiles:
        raise ValueError("Sender manifest profile version or scan mode is obsolete")
    return {"document":read_oracle_json(row[0]),"quantity":Decimal(str(row[2])),"gtin":str(row[3]).zfill(14)}

def aggregation_members(cur: Any,order_id: str,line_number: str,profile: tuple[str,str],code: str,agg_level: str,manifest_id: str|None) -> list[dict[str,Any]]:
    digest=sha256(code.encode()).hexdigest()
    if manifest_id:
        cur.execute("select UNITS_JSON from RRL_TRACE_SENDER_AGG where MANIFEST_OPERATION_ID=:op and SYSTEM_CODE=:system_code and PROFILE_CODE=:profile_code and CODE_HASH=:code_hash and AGG_LEVEL=:agg_level",op=manifest_id,system_code=profile[0],profile_code=profile[1],code_hash=digest,agg_level=agg_level)
    else:
        cur.execute("select UNITS_JSON from RRL_SAP_TRACE_AGG where ORDER_ID=:order_id and LINE_NUMBER=:line_no and SYSTEM_CODE=:system_code and PROFILE_CODE=:profile_code and CODE_HASH=:code_hash and AGG_LEVEL=:agg_level",order_id=order_id,line_no=line_number,system_code=profile[0],profile_code=profile[1],code_hash=digest,agg_level=agg_level)
    row=cur.fetchone()
    if not row:
        raise ValueError("Unknown aggregation composition: import exact sender manifest")
    return read_oracle_json(row[0])

def assert_sender_capture(header: dict[str,Any],units: dict[str,dict[tuple[str,str],str]],quantities: dict[str,Decimal],base: str) -> None:
    original=header["document"]["units"]
    if set(units)!={item["unit_id"]for item in original}:
        raise ValueError("Capture must cover exactly the declared sender units")
    for item in original:
        uid=item["unit_id"]
        if quantities[uid]!=unit_quantity(item["quantity"],base,None):
            raise ValueError("Capture unit quantity differs from sender document")
        expected={(code["system_code"],code["profile_code"]):canonical_mark(code["system_code"],code["profile_code"],code["code"],header["gtin"] if code["system_code"]=="CRPT" else None)["identity"]for code in item["codes"]}
        actual={profile:canonical_mark(*profile,code,header["gtin"] if profile[0]=="CRPT" else None)["identity"]for profile,code in units[uid].items()}
        if expected!=actual:
            raise ValueError("Captured unique codes differ from original sender composition")

def assert_current_mark_policy(cur: Any,pallet: str,marks: dict[str,Any]) -> None:
    cur.execute("select p.POLICY_VERSION,p.MARKING_REQUIRED from RRL_SKU_RECEIPT_POLICY p join RRL_PALLETS lot on lot.ARTICUL=p.ARTICUL where lot.UID_PALLET=:lot_id",lot_id=pallet)
    if cur.fetchone()!=(marks["policy_version"],1):
        raise ValueError("Marked policy changed after capture planning")
    cur.execute("select p.SYSTEM_CODE,p.PROFILE_CODE,p.PROFILE_VERSION,p.SCAN_MODE from RRL_SKU_RECEIPT_PROFILE p join RRL_PALLETS lot on lot.ARTICUL=p.ARTICUL where lot.UID_PALLET=:lot_id",lot_id=pallet)
    current={(r[0],r[1]):{"version":r[2],"mode":r[3]}for r in cur.fetchmany(51)}
    if current!=marks["profiles"]:
        raise ValueError("Marking profile/version/mode changed after capture planning")

def persist_scanned_aggregates(cur: Any,pallet: str,scanned: list[dict[str,Any]]) -> None:
    import oracledb
    seen=set()
    for aggregation in scanned:
        key=(aggregation["system"],sha256(aggregation["code"].encode()).hexdigest())
        if key in seen:
            continue
        seen.add(key)
        cur.setinputsizes(code_body=oracledb.DB_TYPE_CLOB)
        cur.execute("insert into RRL_WMS_RECEIPT_AGG(SYSTEM_CODE,CODE_HASH,UID_PALLET,PROFILE_CODE,AGG_LEVEL,RAW_CODE) values(:system_code,:code_hash,:lot_id,:profile_code,:agg_level,:code_body)",system_code=aggregation["system"],code_hash=key[1],lot_id=pallet,profile_code=aggregation["profile"],agg_level=aggregation["level"],code_body=aggregation["code"])
