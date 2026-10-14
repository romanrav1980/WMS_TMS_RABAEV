from datetime import date,datetime,timezone
from typing import Any
import oracledb
from ..contracts import LogisticsCostError
from ..domain.day_window import day_window
from .cost_access import require_warehouse
from .reconciliation_documents import daily_counts,backlog_documents
from .reconciliation_external_documents import external_documents
from .reconciliation_stock import stock_snapshot
from .reconciliation_stock_documents import stock_documents
from .reconciliation_erp import erp_snapshot
from .reconciliation_regulatory import regulatory_snapshot
from .reconciliation_task_times import task_time_coverage
from .shipping_register import read_snapshot

class DayReconciliation:
    def __init__(self,gateway: Any) -> None:
        self.gateway=gateway

    def stock_conflicts(self,ware: int,metric: str,after: str | None,limit: int,actor: str) -> dict[str,Any]:
        from .stock_conflict_page import stock_conflict_page
        return stock_conflict_page(self.gateway,ware,metric,after,limit,actor)

    def report(self,ware: int,day: date,region: str,actor: str) -> dict[str,Any]:
        local_start,local_end=day_window(day)
        with self.gateway.transaction("Consistent current stock and operational-day reconciliation") as cur:
            cur.execute("set transaction read only")
            require_warehouse(cur,ware,actor,"transport_dispatch_view")
            try:
                cur.execute("select sys_extract_utc(to_timestamp_tz(:local_start||' '||:region,'FXYYYY-MM-DD HH24:MI:SS TZR')),sys_extract_utc(to_timestamp_tz(:local_end||' '||:region,'FXYYYY-MM-DD HH24:MI:SS TZR'))from dual",{"local_start":local_start,"local_end":local_end,"region":region})
                raw_start,raw_end=cur.fetchone();start=raw_start.replace(tzinfo=timezone.utc);end=raw_end.replace(tzinfo=timezone.utc)
            except oracledb.DatabaseError as exc:
                if getattr(exc.args[0],"code",0) in(1882,1878,1861):raise LogisticsCostError("RECONCILIATION_TIMEZONE","Неизвестный часовой пояс или недопустимая граница дня",422)from exc
                raise
            cur.setinputsizes(day_from=oracledb.DB_TYPE_TIMESTAMP_TZ,day_to=oracledb.DB_TYPE_TIMESTAMP_TZ)
            daily=daily_counts(cur,{"ware":ware,"day_from":start,"day_to":end})
            backlog,documents=backlog_documents(cur,ware)
            stock=stock_snapshot(cur,ware);erp=erp_snapshot(cur,ware);regulatory=regulatory_snapshot(cur,ware)
            task_times=task_time_coverage(cur,ware)
            shipping=read_snapshot(cur,ware,day,0,20)
            blockers=[{"code":key,"count":count,"documents":documents[key]}for key,count in backlog.items()if count>0]
            if shipping["has_more"]:blockers.append({"code":"shipping_register_page_incomplete","count":1})
            if not shipping["all_shipping_zone_coverage_verified"]:blockers.append({"code":"shipping_zone_classification_incomplete","count":1})
            occupied=sum(row["occupied"]for row in shipping["cells"])
            if occupied:blockers.append({"code":"shipping_declared_cells_occupied","count":occupied})
            pending=sum(not row["physical_departure_confirmed"]for row in shipping["rows"])
            if pending:blockers.append({"code":"shipping_members_not_departed_in_page","count":pending})
            invalid=sum(int(row["invalid_rows"]or 0)for row in stock["by_base_uom"])
            if invalid:blockers.append({"code":"stock_quantity_invariants","count":invalid})
            if stock["physical_unit_composition_conflicts"]:blockers.append({"code":"physical_unit_composition","count":stock["physical_unit_composition_conflicts"]})
            if erp:blockers.append({"code":"external_erp_ack_pending","count":sum(row["count"]for row in erp)})
            if regulatory["message_count"]:blockers.append({"code":"regulatory_ack_not_reconciled","count":regulatory["message_count"]})
            if regulatory["source_operation_unverified_count"]:blockers.append({"code":"regulatory_stock_source_unverified","count":regulatory["source_operation_unverified_count"]})
            external=external_documents(cur,ware,{item["code"]:item["count"] for item in blockers})
            external.update(stock_documents(cur,ware,{item["code"]:item["count"] for item in blockers}))
            for item in blockers:
                if item["code"] in external:item["documents"]=external[item["code"]]
                item.setdefault("documents",{"available":False,"document_ids":[],"has_more":None,"reason":"DERIVED_COUNTER_SOURCE_REGISTER_REQUIRED"})
            return {"warehouse_id":ware,"business_date":day.isoformat(),"timezone_region":region,"from_utc":start.isoformat(),"to_utc":end.isoformat(),"read_at_utc":datetime.now(timezone.utc).isoformat(),"consistent_snapshot":True,"daily_facts":daily,"current_backlog":backlog,"current_backlog_documents":documents,"stock":stock,"erp_unacknowledged":erp,"regulatory":regulatory,"warehouse_task_time_coverage":task_times,"shipping_register":shipping,"open_items":blockers,"day_closed":False,"full_regulatory_reconciliation_verified":False,"legacy_naive_timestamps_used_for_daily_counts":False}
