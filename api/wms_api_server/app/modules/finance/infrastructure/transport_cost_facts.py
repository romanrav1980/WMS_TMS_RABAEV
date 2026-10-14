"""Use immutable departure, destination and unloading facts; never mutable trip pricing."""
from typing import Any
from ...platform.public import read_oracle_json
from ..contracts import LogisticsCostError
from .cost_access import require_warehouse


def transport_facts(cursor: Any,trip: int,ware: int,actor: str)->dict[str,Any]:
    require_warehouse(cursor,ware,actor,"transport_dispatch_view")
    cursor.execute("""select s.SOURCE_JSON from RRL_TT_VEHICLE_SOURCE s
     join RRL_STOCK_OPERATION o on o.OPERATION_ID=s.DEPARTURE_OPERATION_ID and o.STATE='APPLIED'
     where s.TT_ID=:trip""",trip=trip)
    rows=cursor.fetchall()
    if len(rows)!=1:
        raise LogisticsCostError("TRANSPORT_DEPARTURE_SOURCE_REQUIRED","Нет зафиксированного источника машины на выезде")
    source=read_oracle_json(rows[0][0])
    cursor.execute("""select l.LOAD_OPERATION_ID,l.WARE_ID,l.VEHICLE_ID,l.VEHICLE_NUMBER
     from RRL_TT_HU_LOAD_FACT l join RRL_STOCK_OPERATION o on o.OPERATION_ID=l.LOAD_OPERATION_ID and o.STATE='APPLIED'
     where l.TT_ID=:trip and l.DEPARTURE_OPERATION_ID=:departure order by l.LOAD_OPERATION_ID fetch first 201 rows only""",
                   trip=trip,departure=source["departure_operation_id"])
    loads=cursor.fetchall()
    if not loads or len(loads)>200:
        raise LogisticsCostError("TRANSPORT_SOURCE_BOUND","Нужны исходные места выезда, не более 200")
    warehouses=sorted({int(row[1])for row in loads})
    if ware not in warehouses:
        raise LogisticsCostError("TRANSPORT_SOURCE_WAREHOUSE_REQUIRED","Выбранный склад не является источником рейса",403)
    for owner in warehouses:
        require_warehouse(cursor,owner,actor,"transport_dispatch_view")
    if any(row[2]!=source["vehicle_id"]or row[3]!=source["vehicle_number"]for row in loads):
        raise LogisticsCostError("TRANSPORT_VEHICLE_SOURCE_MISMATCH","Места не соответствуют машине исходного выезда")
    cursor.execute("""select distinct l.LOAD_OPERATION_ID,m.DESTINATION_ADDR
     from RRL_TT_HU_LOAD_FACT l join RRL_TT_HU_LOAD_ST m on m.LOAD_OPERATION_ID=l.LOAD_OPERATION_ID
     where l.TT_ID=:trip and l.DEPARTURE_OPERATION_ID=:departure
     order by l.LOAD_OPERATION_ID,m.DESTINATION_ADDR fetch first 201 rows only""",
                   trip=trip,departure=source["departure_operation_id"])
    destinations=cursor.fetchall()
    if not destinations or len(destinations)>200 or any(addr is None for _,addr in destinations):
        raise LogisticsCostError("TRANSPORT_DESTINATION_SOURCE_REQUIRED","Нужен полный архив адресов мест, не более 200 пар")
    if {load for load,_ in destinations}!={row[0]for row in loads}:
        raise LogisticsCostError("TRANSPORT_DESTINATION_COVERAGE_REQUIRED","Архив адресов не покрывает каждое место выезда")
    cursor.execute("""select r.LOAD_OPERATION_ID,r.STORE_ADDR,r.OPERATION_ID,
       u.METHOD,u.ROLLING_DIFFICULT,u.LOADER_PRESENT,u.EVIDENCE_REFERENCE,
       to_char(s.STARTED_AT_INSTANT,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'),
       to_char(u.FINISHED_AT_INSTANT,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM')
     from RRL_STORE_RECEIPT_FACT r join RRL_STOCK_OPERATION op on op.OPERATION_ID=r.OPERATION_ID and op.STATE='APPLIED'
     join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=r.LOAD_OPERATION_ID
     left join RRL_STORE_UNLOAD_FACT u on u.RECEIPT_OPERATION_ID=r.OPERATION_ID
     left join RRL_STORE_UNLOAD_START s on s.OPERATION_ID=u.START_OPERATION_ID
     where l.TT_ID=:trip and l.DEPARTURE_OPERATION_ID=:departure
     order by r.LOAD_OPERATION_ID,r.STORE_ADDR fetch first 201 rows only""",
                   trip=trip,departure=source["departure_operation_id"])
    receipts=cursor.fetchall()
    if len(receipts)>200:
        raise LogisticsCostError("TRANSPORT_RECEIPT_BOUND","Не более 200 приёмок в одном начислении")
    received={(row[0],row[1]):row for row in receipts}
    if len(received)!=len(receipts)or any(key not in set(destinations)for key in received):
        raise LogisticsCostError("TRANSPORT_RECEIPT_SOURCE_MISMATCH","Приёмка не соответствует архивному адресу")
    details=[];missing=[]
    for load,address in destinations:
        row=received.get((load,address))
        if row is None or row[3]is None or row[7]is None or row[8]is None:
            missing.append({"load_operation_id":load,"address":address,"reason":"ACTUAL_UNLOADING_REQUIRED"});continue
        details.append({"load_operation_id":load,"address":address,"receipt_operation_id":row[2],"method":row[3],
                        "rolling_difficult":bool(row[4]),"loader_present":bool(row[5]),"evidence_reference":row[6],
                        "started_at_instant":row[7],"finished_at_instant":row[8]})
    if source["profile_state"]!="READY":
        missing.append({"reason":"VEHICLE_PROFILE_"+source["profile_state"]})
    return {"trip_id":trip,"warehouse_id":ware,"source_warehouses":warehouses,"departure":source,
            "load_count":len(loads),"destination_count":len(destinations),"served_addresses":len({r["address"]for r in details}),
            "unloads":details,"missing":missing,"complete":not missing,"cost_posted":False,"stock_changed":False}
