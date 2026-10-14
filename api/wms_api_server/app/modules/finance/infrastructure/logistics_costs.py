from typing import Any
from ..contracts import LogisticsCostError
from .box_rates import set_box_rate
from .monthly_rates import set_monthly_rate
from .box_costs import calculate_box_cost
from .cost_access import require_warehouse

class LogisticsCosts:
    def __init__(self,gateway: Any) -> None:
        self.gateway=gateway

    def invoice_transport_costs(self,invoice: int,actor: str)->dict[str,Any]:
        from .transport_cost_read import invoice_transport_costs
        return invoice_transport_costs(self.gateway,invoice,actor)

    def transport_costs(self,trip: int,ware: int,actor: str)->dict[str,Any]:
        from .transport_cost_read import transport_costs
        return transport_costs(self.gateway,trip,ware,actor)

    def conduct_transport_cost(self,body: dict[str,Any],actor: str)->dict[str,Any]:
        from .transport_cost_preview import conduct_transport_cost
        return conduct_transport_cost(self.gateway,body,actor)

    def transport_cost_preview(self,trip: int,ware: int,price_id: int,actor: str)->dict[str,Any]:
        from .transport_cost_preview import preview_transport_cost
        with self.gateway.transaction("Explain immutable transport cost")as cursor:
            cursor.execute("set transaction read only")
            return preview_transport_cost(cursor,trip,ware,price_id,actor)

    def transport_facts(self,trip: int,ware: int,actor: str)->dict[str,Any]:
        from .transport_cost_facts import transport_facts
        with self.gateway.transaction('Read immutable transport cost facts')as cursor:
            cursor.execute('set transaction read only')
            return transport_facts(cursor,trip,ware,actor)

    def transport_tariff_sources(self,trip: int,ware: int,actor: str)->dict[str,Any]:
        from .transport_tariff_sources import transport_tariff_sources
        return transport_tariff_sources(self.gateway,trip,ware,actor)

    def publish_transport_norm(self,body: dict[str,Any],actor: str)->dict[str,Any]:
        from .transport_norms import publish_transport_norm
        return publish_transport_norm(self.gateway,body,actor)

    def transport_norm_history(self,ware: int,price_id: int,before: int|None,limit: int,actor: str)->dict[str,Any]:
        from .transport_norms import transport_norm_history
        return transport_norm_history(self.gateway,ware,price_id,before,limit,actor)

    def rate(self,ware: int,currency: str,value: str,effective: str,version: int,reason: str,reference: str,actor: str) -> dict[str,Any]:
        return set_box_rate(self.gateway,ware,currency,value,effective,version,reason,reference,actor)

    def monthly_rate(self,ware: int,currency: str,month: str,picking: str,common: str,boxes: str,version: int,reason: str,reference: str,actor: str) -> dict[str,Any]:
        return set_monthly_rate(self.gateway,ware,currency,month,picking,common,boxes,version,reason,reference,actor)

    def calculate(self,op: str,trip: int,ware: int,currency: str,actor: str) -> dict[str,Any]:
        return calculate_box_cost(self.gateway,op,trip,ware,currency,actor)

    def rate_history(self,ware: int,currency: str,before: int,limit: int,actor: str) -> dict[str,Any]:
        from .rate_history import read_rate_history
        return read_rate_history(self.gateway,ware,currency,before,limit,actor)

    def assembly_period(self,trip: int,ware: int,region: str,actor: str) -> dict[str,Any]:
        from .assembly_period import read_assembly_period
        return read_assembly_period(self.gateway,trip,ware,region,actor)

    def period_policy(self,ware: int,actor: str) -> dict[str,Any]:
        from .period_policy import read_policy
        return read_policy(self.gateway,ware,actor)

    def configure_period(self,op: str,ware: int,mode: str,region: str|None,version: int,reason: str,reference: str,actor: str) -> dict[str,Any]:
        from .period_policy import set_policy
        return set_policy(self.gateway,op,ware,mode,region,version,reason,reference,actor)

    def rates(self,ware: int,actor: str) -> list[dict[str,Any]]:
        from ...platform.public import read_oracle_json
        with self.gateway.transaction("Read current warehouse cost rate") as cur:
            cur.execute("set transaction read only")
            require_warehouse(cur,ware,actor,"transport_dispatch_view")
            cur.execute("""select h.CURRENCY,h.VERSION_NO,to_char(r.RATE_VALUE,'TM9') RATE_VALUE,
            to_char(r.EFFECTIVE_FROM,'YYYY-MM-DD') EFFECTIVE_FROM,r.BASIS,r.REASON_TEXT,r.DECISION_REFERENCE,r.COMPONENTS_JSON
            from RRL_LOGISTICS_RATE_HEAD h join RRL_LOGISTICS_RATE_HISTORY r on r.RATE_KEY=h.RATE_KEY and r.VERSION_NO=h.VERSION_NO
            where h.WARE_ID=:ware order by h.CURRENCY fetch first 50 rows only""",ware=ware)
            columns=[x[0].lower()for x in cur.description]
            rows=[]
            for values in cur.fetchall():
                row=dict(zip(columns,values));wire=row.pop("components_json");row["components"]=read_oracle_json(wire)if wire is not None else None;rows.append(row)
            return rows

    def trip(self,trip: int,actor: str) -> dict[str,Any]:
        from ..domain.cost_summary import recognized_cost_summary
        rows=self._lines("l.TT_ID=:id",trip,actor)
        try:
            return {"trip_id":trip,"lines":rows,"summary":recognized_cost_summary(rows)}
        except ValueError as exc:
            raise LogisticsCostError("COST_SUMMARY_SOURCE_INVALID",str(exc))from exc

    def invoice(self,invoice: int,actor: str) -> list[dict[str,Any]]:
        exists=self.gateway.fetch_all("select count(*) CNT from RRL_BILL_ORDERS where ID=:id",{"id":invoice})
        if exists[0]["cnt"]!=1:raise LogisticsCostError("COST_INVOICE_NOT_FOUND","Счёт не найден",404)
        return self._lines("t.PAY_ORDER_ID=:id",invoice,actor)

    def invoice_summary(self,invoice: int,actor: str) -> dict[str,Any]:
        from ..domain.cost_summary import recognized_cost_summary
        rows=self.invoice(invoice,actor)
        try:
            return {"invoice_id":invoice,"lines":rows,**recognized_cost_summary(rows)}
        except ValueError as exc:
            raise LogisticsCostError("COST_SUMMARY_SOURCE_INVALID",str(exc))from exc

    def _lines(self,clause: str,object_id: int,actor: str) -> list[dict[str,Any]]:
        rows=self.gateway.fetch_all("""select r.OPERATION_ID,l.TT_ID,l.WARE_ID,c.LOAD_OPERATION_ID,c.COST_CODE,c.CURRENCY,
        c.QUANTITY,to_char(c.RATE_VALUE,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') RATE_VALUE,to_char(c.AMOUNT,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') AMOUNT,c.VERSION_NO,c.BASIS,h.COMPONENTS_JSON COMPONENTS,
        to_char(c.RATE_DATE,'YYYY-MM-DD') RATE_DATE,c.PERIOD_MODE,c.PERIOD_TIME_ZONE,c.PERIOD_POLICY_VERSION
        from RRL_LOGISTICS_COST_RUN r join RRL_LOGISTICS_COST_LINE c on c.OPERATION_ID=r.OPERATION_ID
        join RRL_LOGISTICS_RATE_HISTORY h on h.RATE_KEY=c.RATE_KEY and h.VERSION_NO=c.VERSION_NO
        join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=c.LOAD_OPERATION_ID join RRL_TRANSPORT_TASK t on t.ID=l.TT_ID
        join RUSERS u on u.ID=:actor and nvl(u.DELETED,0)=0 and(u.WARE_ID=l.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')
        where """+clause+" order by l.TT_ID,c.LOAD_OPERATION_ID,c.RATE_DATE fetch first 501 rows only",{"id":object_id,"actor":actor})
        from ...platform.public import read_oracle_json
        for row in rows:
            if row["components"] is not None:row["components"]=read_oracle_json(row["components"])
        if len(rows)>500:raise LogisticsCostError("COST_DETAIL_BOUND","Детализацию более 500 строк следует выгрузить отдельными рейсами")
        return rows
