from pathlib import Path
p=Path(__file__).resolve().parents[1]/"api/wms_api_server/app/modules/resources/infrastructure/case_read_model.py"
s=p.read_text(encoding="utf-8")
s=s.replace('            with task_route as (','''            with selected_tasks as (
              select CASE_PICK_TASK_ID,PICK_WAVE_ID from (
                select t.CASE_PICK_TASK_ID,t.PICK_WAVE_ID
                  from RRL_CASE_PICK_TASK t
                  join RRL_PICK_WAVE w on w.PICK_WAVE_ID=t.PICK_WAVE_ID
                  join RRL_CUSTOMER_ORDER co on co.CUSTOMER_ORDER_ID=t.CUSTOMER_ORDER_ID
                 where {where_sql}
                 order by t.STATUS,t.CREATED_AT,t.CASE_PICK_TASK_ID
              )where rownum<=:limit
            ),task_route as (''',1)
s=s.replace('               group by l.CASE_PICK_TASK_ID','               where l.CASE_PICK_TASK_ID in(select CASE_PICK_TASK_ID from selected_tasks)\n               group by l.CASE_PICK_TASK_ID',1)
s=s.replace("               where STATUS in ('CREATED', 'PENDING_APPROVAL')","               where STATUS in ('CREATED', 'PENDING_APPROVAL')\n                 and CASE_PICK_TASK_ID in(select CASE_PICK_TASK_ID from selected_tasks)",1)
s=s.replace('               where CASE_PICK_TASK_ID is not null','               where CASE_PICK_TASK_ID in(select CASE_PICK_TASK_ID from selected_tasks)',1)
s=s.replace("               where STATUS not in ('CANCELLED', 'FAILED')","               where STATUS not in ('CANCELLED', 'FAILED')\n                 and PICK_WAVE_ID in(select PICK_WAVE_ID from selected_tasks)",1)
s=s.replace('                  from RRL_CASE_PICK_TASK t','                  from RRL_CASE_PICK_TASK t\n                  join selected_tasks st on st.CASE_PICK_TASK_ID=t.CASE_PICK_TASK_ID',1)
# The first occurrence above might be selected_tasks itself due indentation! Assert no recursion.
if 'join selected_tasks st' in s[s.index('with selected_tasks'):s.index('),task_route')]:
 s=s.replace('                  join selected_tasks st on st.CASE_PICK_TASK_ID=t.CASE_PICK_TASK_ID\n','',1)
 pos=s.index('                  from RRL_CASE_PICK_TASK t',s.index('            select *'))
 s=s[:pos]+s[pos:].replace('                  from RRL_CASE_PICK_TASK t','                  from RRL_CASE_PICK_TASK t\n                  join selected_tasks st on st.CASE_PICK_TASK_ID=t.CASE_PICK_TASK_ID',1)
p.write_text(s,encoding="utf-8")
