"""Read recognised transport amounts separately from legacy carrier invoice prices."""
from typing import Any
from ...platform.public import read_oracle_json
from ..contracts import LogisticsCostError
from .cost_access import require_warehouse
from .normative_totals_read import confirmed_totals


def transport_costs(gateway: Any,trip: int,ware: int,actor: str)->dict[str,Any]:
    with gateway.transaction("Read immutable transport recognition")as cursor:
        cursor.execute("set transaction read only")
        require_warehouse(cursor,ware,actor,"transport_dispatch_view")
        cursor.execute("""select r.RESULT_JSON from RRL_TT_VEHICLE_SOURCE s
         join RRL_TRANSPORT_COST_CLAIM c on c.DEPARTURE_OPERATION_ID=s.DEPARTURE_OPERATION_ID
         join RRL_LOGISTICS_COST_RUN r on r.OPERATION_ID=c.OPERATION_ID and r.TT_ID=s.TT_ID
         where s.TT_ID=:trip and r.WARE_ID=:ware fetch first 2 rows only""",
                       trip=trip,ware=ware)
        rows=cursor.fetchall()
        if len(rows)>1:raise LogisticsCostError("TRANSPORT_COST_CLAIM_AMBIGUOUS","Несколько исходных начислений одного рейса")
        if rows:
            from .normative_correction import confirmed_total
            recognized=read_oracle_json(rows[0][0]);current_total=confirmed_total(cursor,recognized["operation_id"])
        else:recognized=None;current_total=None
        return {"trip_id":trip,"warehouse_id":ware,"recognized":recognized,"confirmed_total":current_total,
                "carrier_invoice_changed":False,"stock_changed":False}


def invoice_snapshot(cursor: Any,invoice: int,actor: str)->dict[str,Any]:
    from decimal import Decimal,localcontext
    cursor.execute("""select r.RESULT_JSON from RRL_LOGISTICS_COST_RUN r
     join RRL_TRANSPORT_COST_CLAIM c on c.OPERATION_ID=r.OPERATION_ID
     join RRL_TRANSPORT_TASK t on t.ID=r.TT_ID
     join RUSERS u on u.ID=:actor and nvl(u.DELETED,0)=0
      and(u.WARE_ID=r.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')
      and RRL_HAS_WRIGHT(u.ID,'transport_dispatch_view')=1
     where t.PAY_ORDER_ID=:invoice order by r.TT_ID,r.OPERATION_ID fetch first 201 rows only""",
                   actor=actor,invoice=invoice)
    rows=cursor.fetchall()
    if len(rows)>200:raise LogisticsCostError("TRANSPORT_INVOICE_BOUND","Не более 200 транспортных начислений; используйте детализацию рейса")
    items=[read_oracle_json(row[0])for row in rows]
    current=confirmed_totals(cursor,{item["operation_id"]:item["total"]for item in items})
    items=[{**item,"confirmed_total":current[item["operation_id"]]}for item in items]
    totals={};confirmed_currency_totals={}
    with localcontext()as context:
        context.prec=80
        for item in items:
            code=item["currency"];value=Decimal(item["total"])
            if not value.is_finite()or value<0:
                raise LogisticsCostError("TRANSPORT_RECOGNIZED_AMOUNT_INVALID","Некорректный сохранённый финансовый итог")
            totals[code]=totals.get(code,Decimal(0))+value
            confirmed=Decimal(item["confirmed_total"])
            if not confirmed.is_finite()or confirmed<0:raise LogisticsCostError("NORMATIVE_CONFIRMED_TOTAL_INVALID","Некорректный подтверждённый итог")
            confirmed_currency_totals[code]=confirmed_currency_totals.get(code,Decimal(0))+confirmed
    cursor.execute("""select distinct l.TT_ID,l.WARE_ID from RRL_TT_HU_LOAD_FACT l
     join RRL_TRANSPORT_TASK t on t.ID=l.TT_ID
     join RUSERS u on u.ID=:actor and nvl(u.DELETED,0)=0
      and(u.WARE_ID=l.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')
      and RRL_HAS_WRIGHT(u.ID,'transport_dispatch_view')=1
     where t.PAY_ORDER_ID=:invoice order by l.TT_ID,l.WARE_ID fetch first 201 rows only""",
                   actor=actor,invoice=invoice)
    sources=cursor.fetchall()
    if len(sources)>200:raise LogisticsCostError("TRANSPORT_INVOICE_SOURCE_BOUND","Не более 200 пар рейс/склад; используйте детализацию")
    return {"invoice_id":invoice,"sources":[{"trip":trip,"warehouse":ware}for trip,ware in sources],"items":items,"currency_totals":[{"currency":code,"amount":format(value,"f"),"confirmed_amount":format(confirmed_currency_totals[code],"f")}for code,value in sorted(totals.items())],
            "scope":"VISIBLE_WAREHOUSES","carrier_invoice_changed":False,"stock_changed":False}


def invoice_transport_costs(gateway: Any,invoice: int,actor: str)->dict[str,Any]:
    with gateway.transaction("Read invoice transport costs in current visible warehouse scope")as cursor:
        cursor.execute("set transaction read only")
        return invoice_snapshot(cursor,invoice,actor)


def normative_cost_sources(gateway: Any,ware: int,actor: str,cost_operation_id: str|None=None)->list[dict[str,Any]]:
    with gateway.transaction("Read original normative correction sources")as cursor:
        cursor.execute("set transaction read only")
        require_warehouse(cursor,ware,actor,"transport_dispatch_view")
        cursor.execute("""select r.OPERATION_ID,r.TT_ID,r.CURRENCY,json_value(r.RESULT_JSON,'$.total')
         from RRL_LOGISTICS_COST_RUN r join RRL_TRANSPORT_COST_CLAIM c on c.OPERATION_ID=r.OPERATION_ID
         where r.WARE_ID=:ware and(:cost_operation_id is null or r.OPERATION_ID=:cost_operation_id)order by r.CREATED_AT desc,r.OPERATION_ID desc fetch first 100 rows only""",ware=ware,cost_operation_id=cost_operation_id)
        rows=cursor.fetchall()
        current=confirmed_totals(cursor,{op:original for op,trip,currency,original in rows})
        return [{"operation_id":op,"trip_id":trip,"currency":currency,"original_total":original,"confirmed_total":current[op]}for op,trip,currency,original in rows]
