from pathlib import Path
import json
out={}
p=Path('api/wms_api_server/app/modules/resources/infrastructure/workload_config.py');s=p.read_text(encoding='utf-8-sig')
needle='            norms=workload_rows(cur)'
replacement=needle+"""
            cur.execute(\"\"\"select r.RESOURCE_ID,r.RESOURCE_NAME,r.USER_ID PERSON_ID from RRL_RESOURCE r
                join RUSERS u on u.ID=r.USER_ID join RRL_RESOURCE_TYPE t on t.RESOURCE_TYPE=r.RESOURCE_TYPE
                where r.WARE_ID=:ware and r.ACTIVE=1 and t.ACTIVE=1 and u.WARE_ID=r.WARE_ID and nvl(u.DELETED,0)=0
                 and RRL_HAS_WRIGHT(u.ID,'case_pick_execute')=1
                 and instr(','||replace(t.DEFAULT_TASK_TYPES,' ','')||',',',CASE_PICK,')>0
                 and exists(select 1 from RRL_RESOURCE_TASK_QUAL q where q.RESOURCE_ID=r.RESOURCE_ID and q.TASK_TYPE='CASE_PICK'
                  and q.ACTIVE=1 and q.VALID_FROM<=systimestamp and(q.VALID_UNTIL is null or q.VALID_UNTIL>systimestamp))
                order by r.RESOURCE_ID fetch first 501 rows only\"\"\",ware=ware)
            people=workload_rows(cur)"""
assert needle in s;s=s.replace(needle,replacement).replace('if len(norms)>500 or len(attendance)>500:','if len(norms)>500 or len(attendance)>500 or len(people)>500:').replace('"planned_attendance":attendance,','"planned_attendance":attendance,"eligible_case_resources":people,')
out[str(p)]=s
p=Path('api/wms_api_server/app/modules/resources/infrastructure/workload_monitor.py');s=p.read_text(encoding='utf-8-sig')
s=s.replace("u.WARE_ID=r.WARE_ID and s.STATUS='ACTIVE'", "u.WARE_ID=r.WARE_ID and RRL_HAS_WRIGHT(u.ID,'case_pick_execute')=1 and s.STATUS='ACTIVE'")
s=s.replace("u.WARE_ID=a.WARE_ID and nvl(u.DELETED,0)=0", "u.WARE_ID=a.WARE_ID and nvl(u.DELETED,0)=0 and RRL_HAS_WRIGHT(u.ID,'case_pick_execute')=1")
out[str(p)]=s
p=Path('wiki-raw/wms_admin_ui_reference/resource-workload.js');s=p.read_text(encoding='utf-8-sig')
start=s.index('      if (auth().hasPermission("resource_management_view")) {')
end=s.index('    } catch (error)',start)
s=s[:start]+"""      el("rwPerson").replaceChildren();
      result.eligible_case_resources.forEach(row => { const option = document.createElement("option"); option.value = row.resource_id; option.textContent = row.resource_name + " · " + row.person_id; el("rwPerson").appendChild(option); });
"""+s[end:]
out[str(p)]=s
p=Path('db/migrations/2026-10-10_ni081_workload_config/002_api.sql');s=p.read_text(encoding='utf-8-sig')
s=s.replace('and u.WARE_ID=p_ware\n   and instr', "and u.WARE_ID=p_ware and RRL_HAS_WRIGHT(u.ID,'case_pick_execute')=1\n   and instr")
out[str(p)]=s
p=Path('scripts/ni081_workload_config_case.py');s=p.read_text(encoding='utf-8-sig').replace("['resource_shift_edit','resource_shift_view']", "['resource_shift_edit','resource_shift_view','wms_admin_login','case_pick_execute']")
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
