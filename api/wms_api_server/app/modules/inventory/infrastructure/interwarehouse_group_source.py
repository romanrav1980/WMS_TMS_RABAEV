"""Bounded first-leg composition from the existing immutable HU shipment."""
from decimal import Decimal
import json
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ..contracts_store_returns import StoreReturnReceiveError


def _archive(q: Any, load: str, actor: str) -> tuple[Any, dict[str, Any], dict[str, Any]]:
    q.callproc("RRL_INTERWARE_UNIT_SOURCE.assert_scope", [load, actor])
    q.execute("""select f.TT_ID,f.WARE_ID,f.ROOT_UID,f.STATUS,f.COMPOSITION_JSON,
        o.COMMAND_TYPE,o.RESOLVED_PLAN_JSON from RRL_TT_HU_LOAD_FACT f
        join RRL_STOCK_OPERATION o on o.OPERATION_ID=f.LOAD_OPERATION_ID and o.STATE='APPLIED'
        where f.LOAD_OPERATION_ID=:load_id""", load_id=load)
    row=q.fetchone()
    if row is None:
        raise StoreReturnReceiveError("INTERWARE_SOURCE_NOT_FOUND","Actual source load required")
    tree=read_oracle_json(row[4]); domain=read_oracle_json(row[6])["domain"]
    if row[5]!="HU_SHIP" or row[3]!="DEPARTED":
        raise StoreReturnReceiveError("INTERWARE_GROUP_DEPARTED_HU_REQUIRED","Departed whole HU required")
    nodes=tree.get("nodes",[])
    if not 2<=len(nodes)<=200 or tree.get("top_place_count")!=1 or tree.get("root")!=row[2]:
        raise StoreReturnReceiveError("INTERWARE_GROUP_ARCHIVE_BOUND","One top place and at most 200 nodes required")
    return row,tree,domain


def _members(q: Any, load: str, tree: dict[str, Any], domain: dict[str, Any]) -> list[dict[str, Any]]:
    q.execute("""select SBORKA_PALLET_ID from RRL_TT_HU_LOAD_ST
        where LOAD_OPERATION_ID=:load_id and ACTIVE_FLAG=1
        order by SBORKA_PALLET_ID fetch first 201 rows only""",load_id=load)
    actual={int(r[0]) for r in q.fetchall()}
    shipments=domain.get("shipments",[])
    if not 2<=len(actual)<=200 or len(shipments)!=len(actual):
        raise StoreReturnReceiveError("INTERWARE_GROUP_MEMBERS_REQUIRED","Two to 200 archived ST required")
    seen=set(); result=[]
    leaves={n["uid"]:n for n in tree["nodes"] if n.get("kind")=="STOCK"}
    for item in shipments:
        part=item["domain"]; st=int(part["document_id"]); legs=part.get("legs",[])
        if st not in actual or st in seen or len(legs)!=1:
            raise StoreReturnReceiveError("INTERWARE_GROUP_EXACT_ST_LEAF_REQUIRED","Each ST must own one whole stock leaf")
        seen.add(st); leg=legs[0]; node=leaves.get(leg["uid"])
        if node is None or node.get("case_task_id") is not None or part.get("case_task") is not None:
            raise StoreReturnReceiveError("INTERWARE_GROUP_STOCK_CONTAINER_ONLY","CASE requires its own receiving contract")
        if node["article"]!=leg["article"] or node["base_uom"]!=leg["base_uom"] or Decimal(node["quantity"])!=Decimal(leg["quantity"]):
            raise StoreReturnReceiveError("INTERWARE_GROUP_WHOLE_LEAF_REQUIRED","Exact archived quantity and UOM required")
        result.append(dict(st_id=st,uid=leg["uid"],article=leg["article"],quantity=leg["quantity"],
                           base_uom=leg["base_uom"],onward=bool(part.get("interwarehouse_onward_source")),
                           supplier_return=part.get("return_supplier_id") is not None))
    if len({x["uid"] for x in result})!=len(leaves) or len(result)!=len(leaves):
        raise StoreReturnReceiveError("INTERWARE_GROUP_DISTINCT_WHOLE_LEAVES_REQUIRED","Every leaf must belong to exactly one ST")
    return sorted(result,key=lambda x:x["uid"])


def _lot(q: Any, load: str, archive_wire: Any, member: dict[str, Any]) -> dict[str, Any]:
    q.execute("select sum(nvl(REMAIN,0)),sum(nvl(HARD_RESERVED_BASE,0)) from RRL_REMAINS where UID_POLETA=:lot_id",
              lot_id=member["uid"])
    physical,hard=q.fetchone()
    blockers=[]
    if physical or hard: blockers.append("SOURCE_STOCK_ALREADY_PRESENT")
    if member["onward"]: blockers.append("EXISTING_ONWARD_LINEAGE_REQUIRES_GROUP_HOP_CONTRACT")
    if member["supplier_return"]: blockers.append("SUPPLIER_RETURN_NOT_CUSTOMER_CARGO")
    q.execute("""select SYSTEM_CODE,PROFILE_CODE,PROFILE_VERSION,SCAN_MODE from RRL_SKU_RECEIPT_PROFILE
        where ARTICUL=:article order by SYSTEM_CODE,PROFILE_CODE fetch first 51 rows only""",article=member["article"])
    profiles=[dict(system_code=r[0],profile_code=r[1],profile_version=r[2],scan_mode=r[3]) for r in q.fetchall()]
    if len(profiles)>50: blockers.append("PROFILE_BOUND")
    try:
        q.setinputsizes(snapshot=oracledb.DB_TYPE_CLOB)
        q.execute("select RRL_INTERWARE_UNIT_SOURCE.issued_manifest(:load_id,:lot_id,:snapshot)from dual",
                  load_id=load,lot_id=member["uid"],snapshot=json.dumps(archive_wire)if isinstance(archive_wire,dict)else archive_wire)
        manifest=read_oracle_json(q.fetchone()[0])
    except oracledb.DatabaseError as exc:
        code=getattr(exc.args[0],"code",0)
        if not 20800<=code<=20999: raise
        manifest=None; blockers.append(str(exc.args[0]).split("\n",1)[0])
    return dict(member,profiles=profiles,issued_manifest=manifest,blockers=blockers)


class InterwarehouseGroupSource:
    def __init__(self,gateway: Any)->None:
        self.gateway=gateway

    def read(self,load: str,actor: str)->dict[str,Any]:
        try:
            with self.gateway.transaction("Bounded grouped interwarehouse source")as q:
                q.execute("set transaction read only")
                row,tree,domain=_archive(q,load,actor)
                if any(node.get("kind") == "CASE" for node in tree["nodes"]):
                    from .interwarehouse_case_source import read_case_group
                    return read_case_group(q, load, actor)
                members=_members(q,load,tree,domain)
                lots=[_lot(q,load,row[4].read() if hasattr(row[4],"read")else row[4],x)for x in members]
                q.execute("""select count(*)from RRL_STORE_RECEIPT_FACT where LOAD_OPERATION_ID=:load_id""",load_id=load)
                blockers=["ALREADY_ACCEPTED_BY_RECIPIENT"]if q.fetchone()[0]else []
                q.execute("select count(*)from RRL_INTERWARE_PLAN where SOURCE_LOAD_OPERATION_ID=:load_id",load_id=load)
                if q.fetchone()[0]: blockers.append("EXISTING_SCALAR_PLAN")
                if any(n.get("kind")not in("STOCK","CONTAINER")for n in tree["nodes"]):
                    blockers.append("STOCK_CONTAINER_ONLY")
                for lot in lots:
                    blockers.extend(lot["uid"]+":"+b for b in lot["blockers"])
                totals={}
                for lot in lots:
                    key=(lot["article"],lot["base_uom"])
                    totals[key]=totals.get(key,Decimal(0))+Decimal(lot["quantity"])
                return dict(source_load_operation_id=load,source_trip_id=row[0],source_warehouse_id=row[1],
                    physical_place_identifier=row[2],physical_place_count=1,stock_leaf_count=len(lots),
                    source_composition=tree,lots=lots,quantity_by_article=[
                        dict(article=a,base_uom=u,quantity=format(v,"f"))for(a,u),v in sorted(totals.items())],
                    source_eligible=not blockers,blockers=blockers,stock_changed=False,
                    grouped_receipt_available=False,regulatory_ack_verified=False)
        except oracledb.DatabaseError as exc:
            code=getattr(exc.args[0],"code",0)
            if 20800<=code<=20999:
                raise StoreReturnReceiveError("INTERWARE_GROUP_SOURCE_REJECTED",str(exc.args[0]).split("\n",1)[0],
                                              403 if code==20882 else 409)from exc
            raise
