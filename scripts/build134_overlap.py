from pathlib import Path
import json
p=Path('db/migrations/2026-10-10_ni081_workload_config/002_api.sql');s=p.read_text(encoding='utf-8-sig')
old="  insert into RRL_WORKLOAD_ATTENDANCE values(g_operation,p_ware,site,v_resource,person,start_at,finish_at,'CASE_PICK',reason_text);"
new="""  select count(*)into n from RRL_WORKLOAD_ATTENDANCE a where a.PERSON_ID=person
   and(a.WARE_ID!=p_ware or a.SITE_CODE!=site)and a.START_AT<finish_at and a.FINISH_AT>start_at
   and not exists(select 1 from RRL_WORKLOAD_ATTEND_CANCEL c where c.PLAN_OPERATION_ID=a.PLAN_OPERATION_ID);
  if n>0 then raise_application_error(-20886,'WORKLOAD_PERSON_OVERLAPPING_OTHER_SITE');end if;
"""+old
assert old in s;s=s.replace(old,new)
print(json.dumps({str(p):s},ensure_ascii=True))
