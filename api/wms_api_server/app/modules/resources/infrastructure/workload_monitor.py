"""Existing live CASE lines, native current presence and approved person roster."""
from datetime import datetime
from decimal import Decimal,localcontext
from hashlib import sha256
import json
from typing import Any
from ..contracts_workload import WorkloadError
from ..domain.workload_intervals import interval_load,outside_view
from ..domain.workload_recommendations import workload_recommendations
from .workload_config import current_warehouse,workload_rows
from .wave_time_reader import approved_wave_windows

class WorkloadMonitor:
    def __init__(self,gateway: Any) -> None:self.gateway=gateway

    def preview(self,ware: int,site: str,start: datetime,end: datetime,minutes: int,windows: list[dict[str,Any]],actor: str) -> dict[str,Any]:
        with self.gateway.transaction("Live workload and person roster READ ONLY snapshot")as cur:
            cur.execute("set transaction read only");current_warehouse(cur,ware,actor)
            work=self._work(cur,ware,site);attendance=self._attendance(cur,ware,site,start,end)
            approved=approved_wave_windows(cur,ware)
            cur.execute("""select distinct s.OPERATOR_USER_ID PERSON_ID from RRL_RESOURCE_SESSION s
                join RRL_RESOURCE r on r.RESOURCE_ID=s.RESOURCE_ID join RUSERS u on u.ID=s.OPERATOR_USER_ID
                where r.WARE_ID=:ware and r.ACTIVE=1 and nvl(u.DELETED,0)=0 and u.WARE_ID=r.WARE_ID and RRL_HAS_WRIGHT(u.ID,'case_pick_execute')=1 and s.STATUS='ACTIVE'
                and s.LAST_HEARTBEAT_AT>=cast(systimestamp as timestamp)-interval '5'minute
                and exists(select 1 from RRL_RESOURCE_TASK_QUAL q where q.RESOURCE_ID=r.RESOURCE_ID and q.TASK_TYPE='CASE_PICK'
                  and q.ACTIVE=1 and q.VALID_FROM<=systimestamp and(q.VALID_UNTIL is null or q.VALID_UNTIL>systimestamp))
                order by s.OPERATOR_USER_ID fetch first 501 rows only""",ware=ware)
            presence=workload_rows(cur)
        by_wave={row["wave_id"]:row for row in windows}
        if len(by_wave)!=len(windows):raise WorkloadError("WORKLOAD_DUPLICATE_WAVE_WINDOW","Для волны допустим один интервал")
        unknown=set(by_wave)-{int(row["pick_wave_id"])for row in work}
        if unknown:raise WorkloadError("WORKLOAD_WAVE_WITHOUT_CURRENT_WORK","Указана чужая волна или волна без текущего CASE-отбора")
        for row in work:
            planned=by_wave.get(int(row["pick_wave_id"]))
            saved=approved.get(int(row["pick_wave_id"]))
            row["window"]=(planned["start_at"],planned["finish_at"])if planned else saved["window"] if saved else None
            row["window_source"]="EXPLICIT_PREVIEW" if planned else saved["status"] if saved else "NO_APPROVED_PLAN"
        unscheduled=[{key:value for key,value in row.items()if key!="window"}for row in work if row["window"]is None]
        intervals=interval_load(start,end,minutes,work,attendance)
        public_work=[{**row,"window":[v.isoformat()for v in row["window"]]if row["window"]else None}for row in work]
        source=sha256(json.dumps([ware,site,public_work,[{**r,"start":r["start"].isoformat(),"finish":r["finish"].isoformat()}for r in attendance]],sort_keys=True,separators=(",",":")).encode()).hexdigest()
        with localcontext()as ctx:
            ctx.prec=60
            total=sum((Decimal(row["remaining_quantity"])/Decimal(row["base_per_hour"])for row in work if row["base_per_hour"]is not None),Decimal(0))
        return {"warehouse_id":ware,"norm_site_code":site,"status":"NO_WORK"if not work else"UNSCHEDULED_WORK"if unscheduled else"NORM_REQUIRED"if any(row["base_per_hour"]is None for row in work)else"PREVIEW",
            "work_outside_view":outside_view(start,end,work),"intervals":intervals,"work":public_work,"unscheduled_work":unscheduled,"known_remaining_person_hours":format(total,"f"),
            "recommendations":workload_recommendations(intervals,work),"native_current_presence":presence,"current_presence_count":len(presence),"presence_duration_assumed":False,
            "source_signature":source,"plan_applied":False,"stock_changed":False,"task_assignments_changed":False,
            "window_source":"EXPLICIT_PREVIEW_OR_APPROVED_PLAN","subwarehouse_filter_applied":False}

    @staticmethod
    def _work(cur: Any,ware: int,site: str) -> list[dict[str,Any]]:
        cur.execute("""with base_policy as(select ARTICUL,BASE_UOM from RRL_STOCK_UOM_CONVERSION u
            where INPUT_UOM=BASE_UOM and NUMERATOR=1 and DENOMINATOR=1 and POLICY_VERSION=(select max(POLICY_VERSION)from RRL_STOCK_UOM_CONVERSION x where x.ARTICUL=u.ARTICUL))
            select l.CASE_PICK_LINE_ID,t.CASE_PICK_TASK_ID,t.PICK_WAVE_ID,t.STATUS TASK_STATUS,l.ARTICUL ARTICLE,b.BASE_UOM,
            to_char(l.PLANNED_QTY-l.PICKED_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''')REMAINING_QUANTITY,
            to_char(n.BASE_PER_HOUR,'TM9','NLS_NUMERIC_CHARACTERS=''.,''')BASE_PER_HOUR,n.VERSION_NO NORM_VERSION,
            to_char(w.PLANNED_START_AT,'YYYY-MM-DD"T"HH24:MI:SS')LEGACY_PLAN_START,
            to_char(w.PLANNED_FINISH_AT,'YYYY-MM-DD"T"HH24:MI:SS')LEGACY_PLAN_FINISH
            from RRL_CASE_PICK_LINE l join RRL_CASE_PICK_TASK t on t.CASE_PICK_TASK_ID=l.CASE_PICK_TASK_ID
            join RRL_PICK_WAVE w on w.PICK_WAVE_ID=t.PICK_WAVE_ID left join base_policy b on b.ARTICUL=l.ARTICUL
            left join RRL_WORKLOAD_NORM n on n.WARE_ID=t.WARE_ID and n.SITE_CODE=:site and n.ARTICLE=l.ARTICUL and n.BASE_UOM=b.BASE_UOM and n.ACTIVE=1
             and n.VERSION_NO=(select max(VERSION_NO)from RRL_WORKLOAD_NORM x where x.WARE_ID=n.WARE_ID and x.SITE_CODE=n.SITE_CODE and x.ARTICLE=n.ARTICLE and x.BASE_UOM=n.BASE_UOM)
            where t.WARE_ID=:ware and w.STATUS not in('DONE','CANCELLED')
             and t.STATUS in('NEW','ASSIGNED','IN_PROGRESS','PARTIAL','WAIT_REPLENISHMENT')and l.STATUS not in('DONE','CANCELLED')
             and l.PLANNED_QTY>l.PICKED_QTY order by t.PICK_WAVE_ID,l.CASE_PICK_LINE_ID fetch first 1001 rows only""",ware=ware,site=site)
        rows=workload_rows(cur)
        if len(rows)>1000 or len({row["case_pick_line_id"]for row in rows})!=len(rows):
            raise WorkloadError("WORKLOAD_LINE_BOUND_OR_BASE_AMBIGUITY","Больше1000 строк либо неоднозначна базовая единица")
        return rows

    @staticmethod
    def _attendance(cur: Any,ware: int,site: str,start: datetime,end: datetime) -> list[dict[str,Any]]:
        cur.execute("""select a.PERSON_ID,to_char(a.START_AT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM')START_AT,
            to_char(a.FINISH_AT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM')FINISH_AT
            from RRL_WORKLOAD_ATTENDANCE a join RRL_RESOURCE r on r.RESOURCE_ID=a.RESOURCE_ID join RUSERS u on u.ID=a.PERSON_ID
            where a.WARE_ID=:ware and a.SITE_CODE=:site and r.WARE_ID=a.WARE_ID and r.ACTIVE=1 and r.USER_ID=u.ID and u.WARE_ID=a.WARE_ID and nvl(u.DELETED,0)=0 and RRL_HAS_WRIGHT(u.ID,'case_pick_execute')=1
             and a.START_AT<to_timestamp_tz(:end_at,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM')
             and a.FINISH_AT>to_timestamp_tz(:start_at,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM')
             and exists(select 1 from RRL_RESOURCE_TASK_QUAL q where q.RESOURCE_ID=a.RESOURCE_ID and q.TASK_TYPE='CASE_PICK'and q.ACTIVE=1 and q.VALID_FROM<=systimestamp and q.VALID_UNTIL is null)
             and not exists(select 1 from RRL_WORKLOAD_ATTEND_CANCEL c where c.PLAN_OPERATION_ID=a.PLAN_OPERATION_ID)
            order by a.PERSON_ID,a.START_AT fetch first 501 rows only""",ware=ware,site=site,start_at=start.isoformat(timespec="microseconds"),end_at=end.isoformat(timespec="microseconds"))
        rows=workload_rows(cur)
        if len(rows)>500:raise WorkloadError("WORKLOAD_PERSON_PLAN_BOUND_500","Сузьте окно планов выхода")
        return [{"person_id":row["person_id"],"start":datetime.fromisoformat(row["start_at"]),"finish":datetime.fromisoformat(row["finish_at"])}for row in rows]
