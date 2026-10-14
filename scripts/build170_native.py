import json
from pathlib import Path
r=Path(__file__).resolve().parents[1];f=r/"db/migrations/2026-10-10_ni033_empty_case";out={}
s=(f/"000_before_return.sql").read_text(encoding="utf-8")
pos=s.index(" procedure compile_command(",s.index("create or replace package body"))
s=s[:pos]+""" procedure assert_empty_cancel(p_task number,p_metadata json_object_t)is
  n number;qty number;
 begin
  if trim(p_metadata.get_string('reason')) is null or length(p_metadata.get_string('reason'))>1000 then
   raise_application_error(-20881,'CASE_EMPTY_CANCEL_REASON_REQUIRED');end if;
  select nvl(PICKED_QTY,0)into qty from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=p_task;
  if qty!=0 then raise_application_error(-20886,'CASE_EMPTY_CANCEL_HISTORICAL_PICK_EXISTS');end if;
  select count(*)into n from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=p_task and nvl(PICKED_QTY,0)!=0;
  if n>0 then raise_application_error(-20886,'CASE_EMPTY_CANCEL_LINE_PICK_EXISTS');end if;
  select count(*)into n from RRL_CASE_CARRIER_LOT where CASE_PICK_TASK_ID=p_task;
  if n>0 then raise_application_error(-20886,'CASE_EMPTY_CANCEL_COMPOSITION_EXISTS');end if;
  select count(*)into n from RRL_WMS_HU_LINK where CHILD_CASE_TASK_ID=p_task and ACTIVE_FLAG=1;
  if n>0 then raise_application_error(-20886,'CASE_EMPTY_CANCEL_DETACH_PARENT_REQUIRED');end if;
  select count(*)into n from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=p_task;
  if n<1 or n>200 then raise_application_error(-20881,'CASE_EMPTY_CANCEL_LINE_BOUND_1_200');end if;
 end;
"""+s[pos:]
needle="  if a.get_size=0 then raise_application_error(-20886,'CASE_RETURN_EMPTY_CARRIER');end if;"
assert s.count(needle)==1
s=s.replace(needle,"""  if m.has('allow_empty') and m.get_boolean('allow_empty')then
   assert_empty_cancel(tid,m);
   if a.get_size!=0 then raise_application_error(-20886,'CASE_EMPTY_CANCEL_COMPOSITION_EXISTS');end if;
   v.put('empty_cancel',true);
  elsif a.get_size=0 then raise_application_error(-20886,'CASE_RETURN_EMPTY_CARRIER');end if;""")
needle="  current_rows:=RRL_STOCK_CASE_PICK_CMD.carrier_rows(tid);"
assert s.count(needle)==1
s=s.replace(needle,"  if m.has('allow_empty')and m.get_boolean('allow_empty')then assert_empty_cancel(tid,m);end if;\n"+needle)
needle="v.put('operation_id',op);v.put('status','RETURNED');p_result:=v.to_clob;"
assert s.count(needle)==1
s=s.replace(needle,"""v.put('operation_id',op);
  if m.has('allow_empty')and m.get_boolean('allow_empty')then
   v.put('status','CANCELLED_EMPTY');v.put('physical_quantity_changed',false);
   v.put('next_action','RELEASE_HELD_TARE_BOOK_THEN_WAVE_DECISION');
  else v.put('status','RETURNED');end if;p_result:=v.to_clob;""")
out[str(f.relative_to(r)/"001_return_contract.sql")]=s
out[str(f.relative_to(r)/"001_return_body.sql")]=s[s.lower().index("create or replace package body"):]
s=(f/"000_before_wave_access.sql").read_text(encoding="utf-8")
needle="  select count(*)into n from RRL_WAREHOUSE_TASK where TASK_SOURCE='WAVE'and SOURCE_DOC_ID=p_wave"
assert s.count(needle)==1
s=s.replace(needle,"""  select count(*)into n from RRL_TARE_BOOK b where b.STATUS='HELD'and b.PLACE_KIND='CASE'
   and exists(select 1 from RRL_CASE_PICK_TASK ct where ct.PICK_WAVE_ID=p_wave and to_char(ct.CASE_PICK_TASK_ID,'TM9')=b.PLACE_ID);
  if n>0 then deny('WAVE_DEFER_TARE_BOOK_REMAINS');end if;
"""+needle)
out[str(f.relative_to(r)/"002_wave_access_contract.sql")]=s
out[str(f.relative_to(r)/"002_wave_access_body.sql")]=s[s.lower().index("create or replace package body"):]
out[str(f.relative_to(r)/"apply.sql")]="-- MIGRATION_ID:2026-10-10-170-case-empty-cancel\n@@001_return_body.sql\n@@002_wave_access_body.sql\n"
out[str(f.relative_to(r)/"rollback.sql")]="@@000_before_wave_access.sql\n@@000_before_return.sql\n-- Restores package sources only; all posted cancellation/stock history stays.\n"
out[str(f.relative_to(r)/"verify.sql")]="select OBJECT_NAME,OBJECT_TYPE,STATUS from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_CASE_RETURN_CMD','RRL_WAVE_EXEC_ACCESS');\nselect NAME,LINE,TEXT from USER_ERRORS where NAME in('RRL_STOCK_CASE_RETURN_CMD','RRL_WAVE_EXEC_ACCESS');\n"
print(json.dumps(out))
