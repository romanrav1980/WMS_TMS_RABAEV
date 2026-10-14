"""Read bounded daily aggregates and projection gaps in one Oracle snapshot."""
from datetime import datetime
from hashlib import sha256
import json
from typing import Any
from ..contracts_forecast import ForecastQuery,WarehouseForecastError
from ..domain.forecast_quantity import history_window,forecast_quantity
from .forecast_access import require_forecast_warehouse,forecast_rows
from .forecast_projection import ForecastProjection
from ...resources.public import forecast_norm_basis,forecast_labour

class WarehouseForecast(ForecastProjection):
    def get(self,ware: int,query: ForecastQuery,actor: str) -> dict[str,Any]:
        with self.gateway.transaction("Warehouse forecast READ ONLY snapshot")as cur:
            cur.execute("set transaction read only")
            require_forecast_warehouse(cur,ware,actor)
            cur.execute("""select to_char(systimestamp at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM')from dual""")
            now=datetime.fromisoformat(cur.fetchone()[0])
            start,end,exposure=history_window(now,query.history_days,query.include_current_day)
            window={"ware":ware,"start_day":start.date(),"end_day":end.date(),"current_day":1 if query.include_current_day else 0}
            cur.execute("""select count(*)from(select f.LOAD_OPERATION_ID from RRL_TT_HU_LOAD_FACT f where f.WARE_ID=:ware and f.STATUS='DEPARTED'
                and f.DEPARTED_AT>=from_tz(cast(:start_day as timestamp),'UTC')
                and f.DEPARTED_AT<case when :current_day=1 then systimestamp else from_tz(cast(:end_day as timestamp),'UTC')end
                and not exists(select 1 from RRL_FORECAST_LOAD p where p.LOAD_OPERATION_ID=f.LOAD_OPERATION_ID)and rownum<=501)""",window)
            missing=int(cur.fetchone()[0])
            cur.execute("""select to_char(DAY_UTC,'YYYY-MM-DD')DAY_UTC,LOAD_COUNT,TOP_PLACES from RRL_FORECAST_DAY
                where WARE_ID=:ware and DAY_UTC>=:start_day and(DAY_UTC<:end_day or(:current_day=1 and DAY_UTC=:end_day))order by DAY_UTC""",window)
            days=forecast_rows(cur)
            series=self._series(cur,window,query.scope)
            norm_basis=forecast_norm_basis(cur,ware,query.scope,series)
        complete=missing==0
        predictions=[forecast_quantity(row,exposure,query.horizon_days,query.minimum_active_days,complete)for row in series]
        labour=forecast_labour(predictions,norm_basis)
        signature=sha256(json.dumps([ware,start.date().isoformat(),end.date().isoformat(),query.include_current_day,query.scope,days,series,missing],sort_keys=True,separators=(",",":")).encode()).hexdigest()
        status="NEEDS_PROJECTION"if missing else"NO_SERIES"if not predictions else"ADVISORY"if any(row["status"]=="READY"for row in predictions)else"INSUFFICIENT_HISTORY"
        return {"warehouse_id":ware,"status":status,"source":"NATIVE_DEPARTED_FROZEN_STOCK","quantity_scope":query.scope,
            "window_from_utc":start.isoformat(),"window_to_utc":end.isoformat(),"exposure_calendar_days":format(exposure,"f"),
            "includes_partial_current_day":query.include_current_day,"minimum_active_days":query.minimum_active_days,
            "projection_gaps_at_least":missing,"gap_count_capped":missing==501,"source_data_signature":signature,
            "observed_days":days,"series":predictions,"labour_estimate":labour,
            "norm_data_signature":sha256(json.dumps(norm_basis,sort_keys=True,separators=(",",":")).encode()).hexdigest(),"stock_changed":False,"plan_applied":False,
            "legacy_naive_dates_included":False,"forecast_method":"CALENDAR_DAY_MEAN"}

    @staticmethod
    def _series(cur: Any,window: dict[str,Any],scope: str) -> list[dict[str,Any]]:
        cur.execute("""with history as(select ARTICLE,BASE_UOM,to_char(sum(BASE_QTY),'TM9','NLS_NUMERIC_CHARACTERS=''.,''')OBSERVED_QUANTITY,
            count(distinct DAY_UTC)ACTIVE_DAYS,sum(LEAF_COUNT)LEAF_COUNT,sum(SOURCE_COUNT)SOURCE_COUNT
            from RRL_FORECAST_SKU_DAY where WARE_ID=:ware and DAY_UTC>=:start_day
            and(DAY_UTC<:end_day or(:current_day=1 and DAY_UTC=:end_day))
            and(:work_scope='OUTBOUND_WORKLOAD'or WORK_KIND=:work_scope)group by ARTICLE,BASE_UOM)
            select h.*,u.BASE_SCALE,u.POLICY_VERSION from history h left join RRL_STOCK_UOM_CONVERSION u
            on u.ARTICUL=h.ARTICLE and u.INPUT_UOM=h.BASE_UOM and u.BASE_UOM=h.BASE_UOM and u.NUMERATOR=1 and u.DENOMINATOR=1
            and u.POLICY_VERSION=(select max(p.POLICY_VERSION)from RRL_STOCK_UOM_CONVERSION p
                where p.ARTICUL=h.ARTICLE and p.INPUT_UOM=h.BASE_UOM and p.BASE_UOM=h.BASE_UOM and p.NUMERATOR=1 and p.DENOMINATOR=1)
            order by h.ARTICLE,h.BASE_UOM fetch first 501 rows only""",{**window,"work_scope":scope})
        rows=forecast_rows(cur)
        if len(rows)>500:
            raise WarehouseForecastError("FORECAST_SERIES_BOUND_500","Сузьте аналитическое окно: больше 500 товарных рядов")
        return rows
