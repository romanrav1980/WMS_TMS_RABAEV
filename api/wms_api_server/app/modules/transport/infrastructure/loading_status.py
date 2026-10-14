"""Current warehouse scoped physical loading facts in one READ ONLY snapshot."""
from typing import Any
from ..contracts import TransportLoadingError
from .loading_thermal_read import loading_thermal_read
from .loading_floor_read import loading_floor_read

def loading_status(gateway: Any, trip: int, actor: str) -> dict[str, Any]:
    with gateway.transaction("Current physical trip loading READ ONLY snapshot") as cur:
        cur.execute("set transaction read only")
        return read_loading_status(cur, trip, actor)

def read_loading_status(cur: Any, trip: int, actor: str) -> dict[str, Any]:
    cur.execute("""select WARE_ID,USER_GROUP from RUSERS where ID=:actor
        and nvl(DELETED,0)=0 and RRL_HAS_WRIGHT(ID,'transport_dispatch_view')=1""",actor=actor)
    user=cur.fetchone()
    if user is None:
        raise TransportLoadingError("LOADING_CURRENT_VIEW_ACTOR_REQUIRED","Недоступен просмотр погрузки",status=403)
    global_scope=str(user[1]or"").strip().upper()=="GLOBAL_ADMIN"
    cur.execute("select ID,TRANSPORT,DOCK,CONDITION,VODITEL_ID,USER_ID from RRL_TRANSPORT_TASK where ID=:trip_id",trip_id=trip)
    header=cur.fetchone()
    if header is None:
        raise TransportLoadingError("TRIP_NOT_FOUND","Рейс не найден",status=404)
    cur.execute("""select sp.ID,sp.ST_NUMBER,sp.PALLET_UID,sp.CONDITION,
        ls.DESTINATION_ADDR,lf.LOAD_OPERATION_ID,
        coalesce(lf.ROOT_UID,case when lf.ROOT_CASE_TASK_ID is not null then 'CASE:'||to_char(lf.ROOT_CASE_TASK_ID)end),lf.STATUS,
        lf.VEHICLE_NUMBER,lf.DOCK,sp.WARE_ID,lf.TT_ID,op.STATE
        from RRL_SBORKA_PALLETS sp left join RRL_TT_HU_LOAD_ST ls
          on ls.SBORKA_PALLET_ID=sp.ID and ls.ACTIVE_FLAG=1
        left join RRL_TT_HU_LOAD_FACT lf on lf.LOAD_OPERATION_ID=ls.LOAD_OPERATION_ID
        left join RRL_STOCK_OPERATION op on op.OPERATION_ID=lf.LOAD_OPERATION_ID
        where sp.TRANSTASK_ID=:trip_id order by sp.ID fetch first 201 rows only""",trip_id=trip)
    raw_members=cur.fetchall()
    if len(raw_members)>200:
        raise TransportLoadingError("TRIP_MEMBER_BOUND_200","Разбейте рейс: больше200 СТ")
    member_names=("id","st_number","pallet_uid","condition","destination_addr","load_operation_id",
                  "root_uid","load_status","vehicle_number","dock","warehouse_id","load_trip_id","stock_operation_state")
    members=[dict(zip(member_names,row))for row in raw_members]
    cur.execute("""select LOAD_OPERATION_ID,coalesce(ROOT_UID,case when ROOT_CASE_TASK_ID is not null then 'CASE:'||to_char(ROOT_CASE_TASK_ID)end),
        VEHICLE_NUMBER,DOCK,STATUS,
        to_char(GROSS_WEIGHT_KG,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''),
        LOADED_BY,LOADED_AT,DEPARTURE_OPERATION_ID,DEPARTED_AT,CONTENT_VERSION,ROOT_CASE_TASK_ID,WARE_ID,
        json_value(COMPOSITION_JSON,'$.nodes[0].sscc'),json_value(COMPOSITION_JSON,'$.nodes[0].kind'),
        json_value(COMPOSITION_JSON,'$.cell'),CUSTODY_RELEASED_AT,CUSTODY_RELEASE_OPERATION_ID
        from RRL_TT_HU_LOAD_FACT where TT_ID=:trip_id order by LOADED_AT,LOAD_OPERATION_ID
        fetch first 201 rows only""",trip_id=trip)
    raw_loads=cur.fetchall()
    if len(raw_loads)>200:
        raise TransportLoadingError("TRIP_LOAD_HISTORY_BOUND_200","История рейса превышает окно")
    load_names=("load_operation_id","root_uid","vehicle_number","dock","status","gross_weight_kg",
                "loaded_by","loaded_at","departure_operation_id","departed_at","content_version",
                "root_case_task_id","ware_id","root_scan_identifier","root_kind","origin_cell",
                "custody_released_at","custody_release_operation")
    loads=[dict(zip(load_names,row))for row in raw_loads]
    warehouses={row["warehouse_id"]for row in members}|{row["ware_id"]for row in loads}
    if not warehouses and not global_scope and header[5]!=actor:
        raise TransportLoadingError("LOADING_EMPTY_TRIP_OWNER_REQUIRED","Недоступный пустой рейс",status=403)
    for warehouse in warehouses:
        cur.execute("select count(*)from RRL_WARES where ID=:ware_id",ware_id=warehouse)
        if cur.fetchone()[0]!=1 or (not global_scope and user[0]!=warehouse):
            raise TransportLoadingError("LOADING_CURRENT_WARE_REQUIRED","Недоступный склад рейса",status=403)
    def physically_loaded(row: dict[str,Any]) -> bool:
        return (row["load_status"]in{"LOADED","DEPARTED"} and row["stock_operation_state"]=="APPLIED"
                and row["load_trip_id"]==trip and row["vehicle_number"]==header[1])
    pending=[row["id"]for row in members if not physically_loaded(row)]
    thermal=loading_thermal_read(cur,header[1],[row["load_operation_id"]for row in loads],trip)
    floor=loading_floor_read(cur,[row["load_operation_id"]for row in loads],trip)
    return {"trip":dict(zip(("id","transport","dock","condition","voditel_id"),header[:5])),
        "members":members,"physical_places":loads,"temperature":thermal,"floor_capacity":floor,
        "loaded_place_count":sum(row["status"]in{"LOADED","DEPARTED"}for row in loads),
        "pending_st_ids":pending,"all_members_physically_loaded":bool(members)and not pending,
        "logically_shipped_without_load_st_ids":[row["id"]for row in members if row["condition"]==2 and not row["load_operation_id"]],
        "departure_requires_server_confirmation":True,"read_only":True,
        "scope":"CURRENT_ACTOR_WAREHOUSE","operational_admission":False}
