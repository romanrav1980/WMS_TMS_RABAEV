"""Existing ST members and declared staging cells in one warehouse snapshot; never close the day."""
from datetime import date
from typing import Any
from datetime import timedelta
import json
import oracledb
from ..contracts import LogisticsCostError
from .cost_access import require_warehouse
from ...master_data.public import published_cell_coverage

def report(gateway: Any,ware: int,day: date,after: int,limit: int,actor: str) -> dict:
    if after<0 or not 1<=limit<=50:
        raise LogisticsCostError("SHIPPING_REGISTER_PAGE_BOUND","Недопустимая страница.",422)
    with gateway.transaction("Existing shipping ST and declared staging register READ ONLY")as cur:
        cur.execute("set transaction read only");require_warehouse(cur,ware,actor,"transport_dispatch_view")
        return read_snapshot(cur,ware,day,after,limit)

def read_snapshot(cur: Any,ware: int,day: date,after: int,limit: int) -> dict:
    cur.execute("""with candidate_ids as(
        select ID from RRL_SBORKA_PALLETS where WARE_ID=:ware and ID>:after_id and STDATE>=:business_day and STDATE<:day_end
        union all
        select p.ID from RRL_SBORKA_PALLETS p join RRL_TRANSPORT_TASK t on t.ID=p.TRANSTASK_ID
        where p.WARE_ID=:ware and p.ID>:after_id and p.STDATE is null and t.SHIPMENT_DATE>=:business_day and t.SHIPMENT_DATE<:day_end
        union
        select p.ID from RRL_ST_DEFER_DECISION d join RRL_SBORKA_PALLETS p
          on p.ST_NUMBER=d.ST_NUMBER and p.WARE_ID=d.WARE_ID
        where d.WARE_ID=:ware and p.ID>:after_id and p.STDATE is null
          and json_value(d.RESULT_JSON,'$.original_shipping_date'returning varchar2(10))=:original_day),
        bounded as(select ID from candidate_ids order by ID fetch first :page_limit rows only)
        select /* SHIPPING_MEMBER_BOUNDED275 */ p.ID,p.ST_NUMBER,p.PALLET_UID,p.CONDITION,p.TRANSTASK_ID,p.ADDR,
        p.STDATE,t.CONDITION,t.SHIPMENT_DATE,
        l.LOAD_OPERATION_ID,l.STATUS,l.TT_ID,l.VEHICLE_NUMBER,t.TRANSPORT,o.STATE,
        coalesce(l.ROOT_UID,'CASE:'||to_char(l.ROOT_CASE_TASK_ID)),
        (select max(d.VERSION_NO)from RRL_ST_DEFER_DECISION d where d.ST_NUMBER=p.ST_NUMBER and d.WARE_ID=p.WARE_ID)
        from bounded b join RRL_SBORKA_PALLETS p on p.ID=b.ID left join RRL_TRANSPORT_TASK t on t.ID=p.TRANSTASK_ID
        left join RRL_TT_HU_LOAD_ST binding on binding.SBORKA_PALLET_ID=p.ID and binding.ACTIVE_FLAG=1
        left join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=binding.LOAD_OPERATION_ID
        left join RRL_STOCK_OPERATION o on o.OPERATION_ID=l.LOAD_OPERATION_ID
        order by p.ID""",ware=ware,after_id=after,business_day=day,day_end=day+timedelta(days=1),original_day=day.isoformat(),page_limit=limit+1)
    records=cur.fetchall();more=len(records)>limit;records=records[:limit]
    rows=[]
    for r in records:
        sid,number,uid,condition,trip,address,st_day,trip_state,trip_day,load,load_state,load_trip,loaded_vehicle,vehicle,root_state,root_uid,deferral_version=r
        physical=bool(load and root_state=="APPLIED"and load_trip==trip and loaded_vehicle==vehicle and load_state in("LOADED","DEPARTED"))
        if physical and load_state=="DEPARTED":state="PHYSICALLY_DEPARTED"
        elif physical:state="LOADED_NOT_DEPARTED"
        elif condition==2:state="LOGICAL_SHIPPED_WITHOUT_CURRENT_LOAD_PROOF"
        elif not trip:state="TRIP_NOT_ASSIGNED"
        else:state="PHYSICAL_LOADING_NOT_CONFIRMED"
        rows.append({"st_pallet_id":sid,"st_number":number,"pallet_identifier":uid,"legacy_condition":condition,
            "trip_id":trip,"trip_state":trip_state,"address":address,"planned_st_date":st_day,"planned_trip_date":trip_day,
            "load_operation_id":load,"root_uid":root_uid if load else None,"physical_state":state,
            "deferral_version":deferral_version,"physical_departure_confirmed":state=="PHYSICALLY_DEPARTED"})
    cur.execute("""select CELL from(
        select c.CELL from RRL_CELLS c where c.WARE_ID=:ware and c.EXPEDITION_GROUP is not null
        union
        select c.CELL from RRL_TOPOLOGY_CELL tc join RRL_CELLS c on c.CELL=tc.LEGACY_CELL_CODE and c.WARE_ID=tc.WARE_ID
        where tc.WARE_ID=:ware and tc.ACTIVE=1 and tc.CELL_KIND in('TRANSPORT_STAGING','GATE','FILM_WRAP')
        and tc.TOPOLOGY_ID=(select max(TOPOLOGY_ID)from RRL_WAREHOUSE_TOPOLOGY where WARE_ID=:ware and STATUS='PUBLISHED'))
        order by CELL fetch first 501 rows only""",ware=ware)
    codes=[row[0]for row in cur.fetchall()]
    if len(codes)>500:raise LogisticsCostError("SHIPPING_REGISTER_CELL_BOUND_500","Слишком много ячеек грузовой зоны.",409)
    occupancy=[]
    if codes:
        payload=cur.var(oracledb.DB_TYPE_CLOB);payload.setvalue(0,json.dumps(codes))
        # Predicate exactly matches the already installed sparse container-cell index178.
        cur.execute("""with declared as(select CELL from json_table(:cell_codes,'$[*]'columns(CELL varchar2(50)path '$'))),
            facts as(
              select /*+ leading(d r) use_nl(r) */ d.CELL,'STOCK'kind,count(*)cnt from declared d join RRL_REMAINS r on r.CELL=d.CELL where r.REMAIN>0 group by d.CELL
              union all
              select /*+ leading(d p) use_nl(p) */ d.CELL,'CONTAINER',count(*)from declared d join RRL_PALLETS p
                on case when p.HU_KIND='CONTAINER'then p.HU_CURRENT_CELL end=d.CELL where p.HU_SHIPPED_OPERATION is null group by d.CELL
              union all
              select d.CELL,'CASE',count(*)from declared d join RRL_CASE_PICK_TASK t on t.CURRENT_CELL=d.CELL
                where t.WARE_ID=:ware and t.SHIPPED_OPERATION is null and t.STATUS not in('SHIPPED','CANCELLED','RETURNED')group by d.CELL)
            select /* SHIPPING_CELL_BOUNDED275 */ d.CELL,
              nvl(sum(case when f.kind='STOCK'then f.cnt end),0),
              nvl(sum(case when f.kind='CONTAINER'then f.cnt end),0),
              nvl(sum(case when f.kind='CASE'then f.cnt end),0)
            from declared d left join facts f on f.CELL=d.CELL group by d.CELL order by d.CELL""",cell_codes=payload,ware=ware)
        occupancy=[{"cell":r[0],"positive_quantity_rows":r[1],"unshipped_container_rows":r[2],"unshipped_case_rows":r[3],
            "occupied":any(value>0 for value in r[1:])}for r in cur.fetchall()]
    coverage=published_cell_coverage(cur,ware)
    verified=coverage["classification_complete"] and bool(codes)
    return {"warehouse_id":ware,"business_date":day.isoformat(),"rows":rows,"has_more":more,
        "next_after_id":rows[-1]["st_pallet_id"]if more else None,"consistent_snapshot":True,
        "member_scope":"CURRENT_ST_OR_ORIGINAL_DEFERRED_TRIP_BUSINESS_DATE","rows_are_physical_place_count":False,"cells":occupancy,
        "declared_cells_occupied":any(row["occupied"]for row in occupancy),
        "declared_cell_scope":"LATEST_PUBLISHED_STAGING_GATE_WRAP_OR_EXPLICIT_LEGACY_EXPEDITION_GROUP",
        "classification_coverage":coverage,
        "all_shipping_zone_coverage_verified":verified,
        "shipping_zone_empty_confirmed":verified and not any(row["occupied"]for row in occupancy),
        "stock_changed":False,"day_closed":False}
