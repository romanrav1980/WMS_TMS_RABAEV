"""One native metadata command; existing employee/qualification source retained."""
import json
from datetime import datetime,timezone
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ..contracts_workload import WorkloadError

def current_warehouse(cur: Any,ware: int,actor: str) -> None:
    cur.execute("select count(*)from RUSERS u where ID=:actor and nvl(DELETED,0)=0 and(WARE_ID=:ware or upper(trim(USER_GROUP))='GLOBAL_ADMIN')",actor=actor,ware=ware)
    if cur.fetchone()[0]!=1:
        raise WorkloadError("WORKLOAD_CURRENT_WARE_ACTOR_REQUIRED","Требуется актуальная привязка исполнителя к складу",403)

def workload_rows(cur: Any) -> list[dict[str,Any]]:
    return [dict(zip([col[0].lower()for col in cur.description],row))for row in cur.fetchall()]

class WorkloadConfig:
    def __init__(self,gateway: Any) -> None:
        self.gateway=gateway

    def command(self,operation: str,action: str,body: dict[str,Any],actor: str) -> dict[str,Any]:
        serialized=json.dumps(body,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False)
        try:
            with self.gateway.transaction("Versioned workload administrative command")as cur:
                result=cur.var(oracledb.DB_TYPE_CLOB)
                cur.callproc("RRL_WORKLOAD_CONFIG_API.execute_command",[operation,actor,action,serialized,result])
                return read_oracle_json(result.getvalue())
        except oracledb.DatabaseError as exc:
            code=getattr(exc.args[0],"code",0)
            if code==1403:
                raise WorkloadError("WORKLOAD_CURRENT_RESOURCE_NOT_FOUND","Действующий ресурс или сотрудник не найден",404) from exc
            if 20800<=code<=20999:
                raise WorkloadError("WORKLOAD_CONFIG_REJECTED",str(exc.args[0]).split("\n",1)[0],403 if code==20882 else 409) from exc
            raise WorkloadError("WORKLOAD_COMMAND_UNCONFIRMED","Повторите исходную команду без изменения идентификатора",503) from exc

    def configuration(self,ware: int,actor: str,site: str | None=None,start: datetime | None=None,finish: datetime | None=None) -> dict[str,Any]:
        with self.gateway.transaction("Workload configuration READ ONLY")as cur:
            cur.execute("set transaction read only");current_warehouse(cur,ware,actor)
            norm_filter=" and n.SITE_CODE=:site" if site is not None else ""
            attendance_filter=" and a.SITE_CODE=:site" if site is not None else ""
            scoped={"ware":ware,**({"site":site} if site is not None else {})}
            attendance_params=dict(scoped)
            if start is not None and finish is not None:
                attendance_filter+=" and a.START_AT<:finish_at and a.FINISH_AT>:start_at"
                attendance_params.update(start_at=start.astimezone(timezone.utc),finish_at=finish.astimezone(timezone.utc))
            else:
                attendance_filter+=" and a.FINISH_AT>systimestamp-interval '1'day"
            cur.execute("""select n.WARE_ID,n.SITE_CODE,n.ARTICLE,n.BASE_UOM,n.VERSION_NO,n.ACTIVE,
                to_char(n.BASE_PER_HOUR,'TM9','NLS_NUMERIC_CHARACTERS=''.,''')BASE_PER_HOUR,n.REASON,n.OPERATION_ID
                from RRL_WORKLOAD_NORM n where n.WARE_ID=:ware and n.VERSION_NO=(select max(x.VERSION_NO)from RRL_WORKLOAD_NORM x
                 where x.WARE_ID=n.WARE_ID and x.SITE_CODE=n.SITE_CODE and x.ARTICLE=n.ARTICLE and x.BASE_UOM=n.BASE_UOM)
                """+norm_filter+" order by n.SITE_CODE,n.ARTICLE,n.BASE_UOM fetch first 501 rows only",scoped)
            norms=workload_rows(cur)
            cur.execute("select s.WORK_SCOPE,s.SITE_CODE,s.VERSION_NO,s.ACTIVE,s.REASON,s.OPERATION_ID from RRL_WORKLOAD_SCOPE_SITE s where s.WARE_ID=:ware and s.VERSION_NO=(select max(x.VERSION_NO)from RRL_WORKLOAD_SCOPE_SITE x where x.WARE_ID=s.WARE_ID and x.WORK_SCOPE=s.WORK_SCOPE)order by s.WORK_SCOPE",ware=ware)
            forecast_scopes=workload_rows(cur)
            cur.execute("""select r.RESOURCE_ID,r.RESOURCE_NAME,r.USER_ID PERSON_ID from RRL_RESOURCE r
                join RUSERS u on u.ID=r.USER_ID join RRL_RESOURCE_TYPE t on t.RESOURCE_TYPE=r.RESOURCE_TYPE
                where r.WARE_ID=:ware and r.ACTIVE=1 and t.ACTIVE=1 and u.WARE_ID=r.WARE_ID and nvl(u.DELETED,0)=0
                 and RRL_HAS_WRIGHT(u.ID,'case_pick_execute')=1
                 and instr(','||replace(t.DEFAULT_TASK_TYPES,' ','')||',',',CASE_PICK,')>0
                 and exists(select 1 from RRL_RESOURCE_TASK_QUAL q where q.RESOURCE_ID=r.RESOURCE_ID and q.TASK_TYPE='CASE_PICK'
                  and q.ACTIVE=1 and q.VALID_FROM<=systimestamp and q.VALID_UNTIL is null)
                order by r.RESOURCE_ID fetch first 501 rows only""",ware=ware)
            people=workload_rows(cur)
            cur.execute("""select a.PLAN_OPERATION_ID,a.WARE_ID,a.SITE_CODE,a.RESOURCE_ID,a.PERSON_ID,
                to_char(a.START_AT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM')START_AT,
                to_char(a.FINISH_AT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM')FINISH_AT,a.REASON,
                json_value(o.RESULT_JSON,'$.replaced_plan_operation_id')REPLACED_PLAN_OPERATION_ID
                from RRL_WORKLOAD_ATTENDANCE a join RRL_WORKLOAD_OPERATION o on o.OPERATION_ID=a.PLAN_OPERATION_ID where a.WARE_ID=:ware
                and not exists(select 1 from RRL_WORKLOAD_ATTEND_CANCEL c where c.PLAN_OPERATION_ID=a.PLAN_OPERATION_ID)
                """+attendance_filter+" order by a.START_AT,a.PLAN_OPERATION_ID fetch first 501 rows only",attendance_params)
            attendance=workload_rows(cur)
            if len(norms)>500 or len(attendance)>500 or len(people)>500:
                raise WorkloadError("WORKLOAD_CONFIG_BOUND_500","Более 500 записей: выберите подсклад и период; список сотрудников ограничен складом")
        return {"warehouse_id":ware,"selection":{"site_code":site,"start_at":start.isoformat() if start else None,"finish_at":finish.isoformat() if finish else None},"norms":norms,"forecast_scopes":forecast_scopes,"planned_attendance":attendance,"eligible_case_resources":people,"stock_changed":False,"actual_presence_created":False}
