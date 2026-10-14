"""Same-snapshot legacy calendar orders/secured overlap/old pick stock; no mutations."""
from datetime import date
from decimal import Decimal,localcontext
from hashlib import sha256
import json
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ..contracts_slotting import SlottingError
from ..domain.slotting_demand import unpicked_demand,quantity_scenario
from .slotting_stock import old_stock_credit,incoming_stock_credit
from .slotting_layout import range_capacity
from .slotting_candidates import recommendation_sources

class SlottingDemand:
    def __init__(self,gateway: Any) -> None:self.gateway=gateway

    def preview(self,ware: int,article: str,start: date,end: date,forecast: Decimal|None,forecast_unit: str|None,actor: str,pallet_weight: Decimal|None=None,costs: list[dict[str,Any]]|None=None,candidate_route: int|None=None) -> dict[str,Any]:
        try:
            with self.gateway.transaction("Slotting demand sources READ ONLY snapshot")as cur:
                cur.execute("set transaction read only")
                return self.snapshot(cur,ware,article,start,end,forecast,forecast_unit,actor,pallet_weight,costs,candidate_route)
        except ValueError as exc:raise SlottingError("SLOTTING_SOURCE_INVALID",str(exc)) from exc
        except oracledb.DatabaseError as exc:
            code=getattr(exc.args[0],"code",0)
            if code==1403:raise SlottingError("SLOTTING_SOURCE_NOT_FOUND","Товар или правило отсутствует",404) from exc
            if 20800<=code<=20999:raise SlottingError("SLOTTING_SOURCE_REJECTED",str(exc.args[0]).split("\n",1)[0]) from exc
            raise SlottingError("SLOTTING_SOURCE_UNAVAILABLE","Не удалось прочитать согласованный состав источников",503) from exc

    def snapshot(self,cur: Any,ware: int,article: str,start: date,end: date,forecast: Decimal|None,
                 forecast_unit: str|None,actor: str,pallet_weight: Decimal|None=None,
                 costs: list[dict[str,Any]]|None=None,candidate_route: int|None=None) -> dict[str,Any]:
        cur.execute("""select count(*)from RUSERS where ID=:actor and nvl(DELETED,0)=0
            and(WARE_ID=:ware or upper(trim(USER_GROUP))='GLOBAL_ADMIN')""",actor=actor,ware=ware)
        if cur.fetchone()[0]!=1:raise SlottingError("SLOTTING_CURRENT_WARE_ACTOR_REQUIRED","Требуется текущий склад исполнителя",403)
        cur.execute("select RRL_STOCK_POOL_READ.snapshot_json(:ware,:article)from dual",ware=ware,article=article)
        pool=read_oracle_json(cur.fetchone()[0])
        if forecast is not None and forecast_unit!=pool["unit"]:raise SlottingError("SLOTTING_FORECAST_BASE_MISMATCH","Прогноз должен быть в текущей базовой единице")
        orders,undated=self._orders(cur,pool["orders"],start,end)
        with localcontext()as ctx:
            ctx.prec=80
            firm=sum((unpicked_demand(row)for row in orders),Decimal(0))
            unknown=sum((unpicked_demand(row)for row in undated),Decimal(0))
            old,stock=old_stock_credit(cur,ware,article,[int(row["line_id"])for row in orders])
            incoming,inbound=incoming_stock_credit(cur,ware,article)
            cur.execute("select to_char(PALLET_MULTIPLE,'TM9','NLS_NUMERIC_CHARACTERS=''.,''')from RRL_ARTICULS where ACTICUL=:article",article=article)
            row=cur.fetchone();multiple=Decimal(row[0])if row and row[0]is not None else None
            scenario=quantity_scenario(firm,forecast,old,incoming,multiple)
            layout=range_capacity(cur,ware,article,scenario["nominal_additional_quantity"])
            recommendation=recommendation_sources(cur,ware,article,scenario,layout,pallet_weight,costs or [],candidate_route)
        sources={"orders":orders,"undated_orders":undated,"old_stock":stock,"scheduled_inbound":inbound,"existing_range":layout,"range_recommendation":recommendation}
        signature=sha256(json.dumps(sources,sort_keys=True,separators=(",",":")).encode()).hexdigest()
        return {"warehouse_id":ware,"article":article,"base_uom":pool["unit"],"period_from":start.isoformat(),"period_to_exclusive":end.isoformat(),
            "calendar_basis":"LEGACY_REQUESTED_SHIPMENT_DATE","business_calendar_verified":False,
            "scenario":scenario,"existing_range":layout,"range_recommendation":recommendation,"sources":sources,"source_signature":signature,"stock_changed":False,"plan_applied":False,
            "apply_allowed":False,"status":"PERIOD_ASSIGNMENT_REQUIRED"if unknown>0 else"SCENARIO_ONLY","automatic_sales_forecast":False,
            "undated_unpicked_quantity":format(unknown,"f"),
            "missing_evidence":["AVAILABILITY_HISTORY","CASE_CLASSIFICATION_FOR_UNPLANNED_ORDERS","PHYSICAL_LAYOUT","RANGE_APPROVAL"]+(["UNDATED_OPEN_ORDERS"]if unknown>0 else[])}

    @staticmethod
    def _orders(cur: Any,orders: list[dict[str,Any]],start: date,end: date) -> tuple[list[dict[str,Any]],list[dict[str,Any]]]:
        cur.execute("""select r.CUSTOMER_ORDER_ROW_ID,to_char(h.SHIPMENT_DATE,'YYYY-MM-DD')DAY
            from RRL_CUSTOMER_ORDER_ROW r join RRL_CUSTOMER_ORDER h on h.CUSTOMER_ORDER_ID=r.CUSTOMER_ORDER_ID
            where r.CUSTOMER_ORDER_ROW_ID in(select ID from json_table(:ids,'$[*]'columns(ID number path '$')))""",ids=json.dumps([int(row["line_id"])for row in orders]))
        days={int(identity):day for identity,day in cur.fetchall()}
        selected=[];undated=[]
        for row in orders:
            day=days.get(int(row["line_id"]))
            value={**row,"requested_shipment_day":day,"unpicked_quantity":format(unpicked_demand(row),"f")}
            if day is None:undated.append(value)
            elif start.isoformat()<=day<end.isoformat():selected.append(value)
        return selected,undated
