"""Bounded picker projection of existing TMS trips and original address/store mappings."""
from datetime import date,datetime,timedelta
from ..contracts_plan import TransportPlanError
from ...platform.public import read_oracle_json
import oracledb
from ....oracle_gateway import OracleGateway

def _window(context: dict,start: date|None,end: date|None) -> tuple[date,date,date]:
    raw=context["source_trip"].get("shipment_date")
    if not raw:
        raise TransportPlanError("ST_TRIP_SOURCE_DATE_REQUIRED","У исходного рейса не задана дата отгрузки",409)
    minimum=date.fromisoformat(raw[:10])
    for member in context["members"]:
        if member.get("st_date"):minimum=max(minimum,date.fromisoformat(member["st_date"][:10]))
    start=start or minimum
    end=end or start+timedelta(days=7)
    if start<minimum:
        raise TransportPlanError("ST_TRIP_DATE_BEFORE_PROMISE","Ищите рейсы начиная с "+minimum.isoformat(),422)
    if end<start or (end-start).days>30:
        raise TransportPlanError("ST_TRIP_DATE_WINDOW_INVALID","Период поиска должен составлять не более 31 дня",422)
    return minimum,start,end

def _headers(cur: oracledb.Cursor,context: dict,start: date,end: date,district: str|None,store: str|None,
             after_date: datetime|None,after_id: int,limit: int) -> list:
    conditions=["t.CONDITION=:planned","nvl(t.DELETED,0)=0","nvl(t.PAY_ORDER_ID,0)=0",
                "t.SHIPMENT_DATE>=:day_from","t.SHIPMENT_DATE<:day_to","t.ID!=:source_trip",
                "exists(select 1 from RRL_TR_VEHICLE v where v.NUM=t.TRANSPORT)",
                """not exists(select 1 from RRL_TT_HU_LOAD_FACT l join RRL_TT_HU_LOAD_ST ls on ls.LOAD_OPERATION_ID=l.LOAD_OPERATION_ID
                    where l.TT_ID=t.ID and ls.ACTIVE_FLAG=1 and l.STATUS in('LOADED','DEPARTED'))"""]
    binds={"planned":"Спланирован","day_from":start,"day_to":end+timedelta(days=1),
           "source_trip":context["source_trip_id"],"max_rows":limit+1}
    if district or store:
        stop=["p.TRANSTASK_ID=t.ID","nvl(p.CONDITION,0)!=2"]
        if district:
            stop.append("instr(upper(a.RAION),upper(:district))>0")
            binds["district"]=district
        if store:
            stop.append("""exists(select 1 from RRL_CUSTOMER_STORE_MAP m where m.LEGACY_ADDR=p.ADDR
                        and m.ACTIVE=1 and upper(trim(m.STORE_CODE))=upper(:store_code))""")
            binds["store_code"]=store
        conditions.append("exists(select 1 from RRL_SBORKA_PALLETS p left join RRL_ADDR a on a.ADDR=p.ADDR where "+" and ".join(stop)+")")
    if after_date is not None:
        conditions.append("(t.SHIPMENT_DATE>:cursor_date or(t.SHIPMENT_DATE=:cursor_date and t.ID>:cursor_id))")
        binds.update(cursor_date=after_date,cursor_id=after_id)
    cur.execute("""select t.ID,t.SHIPMENT_DATE,t.TRANSPORT,t.TEMP_REGION,t.DOCK,t.TEMP_WEIGHT,
                    (select count(distinct p.PALLET_UID)from RRL_SBORKA_PALLETS p where p.TRANSTASK_ID=t.ID and nvl(p.CONDITION,0)!=2)
                    from RRL_TRANSPORT_TASK t where """+" and ".join(conditions)+
                    " order by t.SHIPMENT_DATE,t.ID fetch first :max_rows rows only",binds)
    return cur.fetchall()

def _stops(cur: oracledb.Cursor,ids: list[int]) -> dict:
    if not ids:return {}
    binds={f"id{i}":value for i,value in enumerate(ids)}
    placeholders=",".join(":"+name for name in binds)
    cur.execute("""select distinct p.TRANSTASK_ID,a.RAION,m.STORE_CODE from RRL_SBORKA_PALLETS p
                left join RRL_ADDR a on a.ADDR=p.ADDR
                left join RRL_CUSTOMER_STORE_MAP m on m.LEGACY_ADDR=p.ADDR and m.ACTIVE=1
                where nvl(p.CONDITION,0)!=2 and p.TRANSTASK_ID in ("""+placeholders+
                ") order by p.TRANSTASK_ID,a.RAION,m.STORE_CODE fetch first 1001 rows only",binds)
    result={}
    for index,(trip,district,store) in enumerate(cur):
        if index==1000:
            raise TransportPlanError("ST_TRIP_STOP_DETAILS_BOUND","Слишком много адресов на странице; уменьшите число рейсов",409)
        values=result.setdefault(trip,{"districts":set(),"stores":set()})
        if district:values["districts"].add(district)
        if store:values["stores"].add(store)
    return result

def candidates(gateway: OracleGateway,st: str,actor: str,start: date|None,end: date|None,district: str|None,store: str|None,
               after_date: datetime|None,after_id: int,limit: int,purpose: str="DEFER") -> dict:
    if (after_date is None)!=(after_id==0) or (after_date is not None and after_date.tzinfo is not None):
        raise TransportPlanError("ST_TRIP_CURSOR_INVALID","Курсор даты и номера рейса должен передаваться вместе без часового пояса",422)
    with gateway.transaction("Existing TMS trip picker READ ONLY bounded source scope") as cur:
        cur.execute("set transaction read only")
        out=cur.var(oracledb.DB_TYPE_CLOB)
        if purpose=="ASSIGN":
            from .assignment_picker_source import assignment_picker_source
            context=assignment_picker_source(cur,st,actor)
        elif purpose=="DEFER":
            cur.callproc("RRL_ST_DEFER_API.context",[st,actor,out]);context=read_oracle_json(out.getvalue())
        else:raise TransportPlanError("ST_TRIP_PURPOSE_INVALID","Допустимы ASSIGN/DEFER",422)
        minimum,start,end=_window(context,start,end)
        headers=_headers(cur,context,start,end,(district or "").strip() or None,(store or "").strip() or None,after_date,after_id,limit)
        chosen=headers[:limit]
        stops=_stops(cur,[row[0]for row in chosen])
        rows=[]
        for trip,day,vehicle,regions,dock,weight,pallets in chosen:
            detail=stops.get(trip,{"districts":set(),"stores":set()})
            rows.append({"trip_id":trip,"shipment_date":day.date().isoformat(),"shipment_time":day.isoformat(timespec="seconds"),
                         "vehicle":vehicle,"regions":regions,"dock":dock,"planned_weight":str(weight) if weight is not None else None,
                         "pallet_count":pallets,"districts":sorted(detail["districts"]),"stores":sorted(detail["stores"])})
        more=len(headers)>limit
        return {"st_number":st,"warehouse_id":context["warehouse_id"],"source_hash":context["source_hash"],
                "minimum_date":minimum.isoformat(),"date_from":start.isoformat(),"date_to":end.isoformat(),"rows":rows,"has_more":more,
                "next_cursor":{"after_date":rows[-1]["shipment_time"],"after_trip_id":rows[-1]["trip_id"]} if more else None}
