from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni081_time_resource_gate")
p=Path("db/migrations/2026-10-11_ni081_trip_time/002_api.sql")
s=p.read_text(encoding="utf-8")
out={str(f/"000_before_rrl_tt_time_api.sql"):s}
block=""" procedure assert_published_resources(p_trip RRL_TRANSPORT_TASK%rowtype,p_start date,p_finish date,p_zone varchar2)is
  v_start timestamp with time zone;v_finish timestamp with time zone;
  v_other_start timestamp with time zone;v_other_finish timestamp with time zone;v_a timestamp with time zone;v_b timestamp with time zone;
  v_source clob;v_hash varchar2(64);v_n number:=0;v_ops number:=0;b json_object_t;ops json_array_t;o json_object_t;
 begin
  select from_tz(cast(p_start as timestamp),p_zone),from_tz(cast(p_finish as timestamp),p_zone)into v_start,v_finish from dual;
  for other in(select t.ID,a.SOURCE_HASH,a.RESULT_JSON
   from RRL_TRANSPORT_TASK t join RRL_TT_TIME_APPROVAL a on a.TT_ID=t.ID
   where t.ID!=p_trip.ID and nvl(t.DELETED,0)=0 and t.CONDITION='Спланирован'and nvl(t.PAY_ORDER_ID,0)=0
   and(t.TRANSPORT=p_trip.TRANSPORT or t.VODITEL_ID=p_trip.VODITEL_ID)
   and a.VERSION_NO=(select max(latest.VERSION_NO)from RRL_TT_TIME_APPROVAL latest where latest.TT_ID=t.ID)
   order by t.ID fetch first 201 rows only)loop
   v_n:=v_n+1;if v_n>200 then raise_application_error(-20886,'TT_TIME_RESOURCE_PLAN_BOUND_200');end if;
   snapshot(other.ID,v_source,v_hash);
   if v_hash=other.SOURCE_HASH then
    b:=json_object_t.parse(other.RESULT_JSON);ops:=b.get_array('operations');v_other_start:=null;v_other_finish:=null;
    if ops is null or ops.get_size not between 1 and 200 then raise_application_error(-20886,'TT_TIME_RESOURCE_PLAN_OPERATIONS_INVALID');end if;
    v_ops:=v_ops+ops.get_size;if v_ops>2000 then raise_application_error(-20886,'TT_TIME_RESOURCE_OPERATION_BOUND_2000');end if;
    for i in 0..ops.get_size-1 loop
     o:=treat(ops.get(i)as json_object_t);
     v_a:=to_timestamp_tz(o.get_string('start_at'),'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM');
     v_b:=to_timestamp_tz(o.get_string('finish_at'),'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM');
     if v_a is null or v_b is null or v_b<v_a then raise_application_error(-20886,'TT_TIME_RESOURCE_PLAN_INTERVAL_INVALID');end if;
     if v_other_start is null or v_a<v_other_start then v_other_start:=v_a;end if;
     if v_other_finish is null or v_b>v_other_finish then v_other_finish:=v_b;end if;
    end loop;
    if v_start<v_other_finish and v_finish>v_other_start then raise_application_error(-20886,'TT_TIME_APPROVED_RESOURCE_OVERLAP');end if;
   end if;
  end loop;
 end;
"""
needle=" procedure context(p_trip number,p_actor varchar2,p_result out clob)is"
assert s.count(needle)==1;s=s.replace(needle,block+needle)
needle="  select json_arrayagg(json_object("
assert s.count(needle)==1;s=s.replace(needle,"  assert_published_resources(w,v_start,v_finish,v_zone);\n"+needle)
out[str(f/"001_api.sql")]=s
out[str(f/"apply.sql")]="@001_api.sql\n"
out[str(f/"rollback.sql")]="@000_before_rrl_tt_time_api.sql\n"
out["wiki/database/retailcase_ni081_time_resource_design_20261011.md"]="# NI08.1: запрет пересечения опубликованных временных планов —250\nOriginal RRL_TT_TIME_API approval same metadata CFG6 X/TT lock. Before journal insert compare other current source-valid latest approval for same vehicle OR driver by absolute aware envelope, half-open. One publication winner; changed source/history doesnotreserve falsely. Current active planned unbilled TT only;200 plan/2000operation bounds fail. No new calendar/quantity/stock writer. Direct TT/OPS edit invalidates approval by sourcehash; doesnotrevoke historical decision, operational admission remains false. Full actual driver/legal/warehouse departure still separate. No foreign plan IDs or source returned on refusal. Implementation in progress, no APPLIED claim yet.\n"
for path,line in [
("wiki/index.md","- [Ограничение опубликованной занятости: проект250](database/retailcase_ni081_time_resource_design_20261011.md): same native approval/CFG-X absolute envelopes/bounds; implementation pending."),
("wiki/log.md","2026-10-11:250 design and incremental native source for current approved original TT vehicle-driver overlap rejection within same metadata publication transaction. No second calendar/stock writer; no APPLIED claim before targeted proof.")
]:out[path]=Path(path).read_text(encoding="utf-8")+"\n"+line+"\n"
print(json.dumps(out,ensure_ascii=True))
