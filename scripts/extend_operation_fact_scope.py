from pathlib import Path
import json
p=Path("db/migrations/2026-10-10_ni081_operation_plan/001_api.sql")
s=p.read_text(encoding="utf-8-sig")
s=s.replace(" procedure generate(p_trip number,p_actor varchar2,p_result out clob);"," procedure generate(p_trip number,p_actor varchar2,p_result out clob);\n procedure write_fact(p_operation number,p_actor varchar2,p_body clob,p_result out clob);")
start=s.rindex("end;\n/")
body=''' procedure write_fact(p_operation number,p_actor varchar2,p_body clob,p_result out clob)is
  b json_object_t:=json_object_t.parse(p_body);before_trip number;w RRL_TRANSPORT_TASK%rowtype;o RRL_TT_OPERATIONS%rowtype;
  v_start date;v_finish date;v_note RRL_TT_OPERATIONS.NOTE%type;n number:=0;v_global number;result json_object_t:=json_object_t();
 begin
  savepoint RRL_OP_FACT141;actor_allowed(p_actor);
  select TT_ID into before_trip from RRL_TT_OPERATIONS where ID=p_operation;
  select *into w from RRL_TRANSPORT_TASK where ID=before_trip for update;
  if nvl(w.DELETED,0)!=0 then raise_application_error(-20886,'OP_FACT_ACTIVE_TRIP_REQUIRED');end if;
  for source in(select ID,WARE_ID from RRL_SBORKA_PALLETS where TRANSTASK_ID=before_trip order by ID fetch first 201 rows only)loop
   n:=n+1;if n>200 then raise_application_error(-20886,'OP_FACT_SOURCE_BOUND_200');end if;
   RRL_TRANSPORT_PLAN_RULES.assert_actor(p_actor,source.WARE_ID);
  end loop;
  if n=0 and nvl(w.USER_ID,'~')!=p_actor then
   select count(*)into v_global from RUSERS where ID=p_actor and upper(trim(USER_GROUP))='GLOBAL_ADMIN';
   if v_global!=1 then raise_application_error(-20882,'OP_FACT_EMPTY_TRIP_OWNER_REQUIRED');end if;
  end if;
  select *into o from RRL_TT_OPERATIONS where ID=p_operation for update;
  if o.TT_ID!=before_trip then raise_application_error(-20886,'OP_FACT_SOURCE_CHANGED_RETRY');end if;
  v_start:=o.FACT_START;v_finish:=o.FACT_END;v_note:=o.NOTE;
  if b.has('fact_start')then v_start:=to_date(b.get_string('fact_start'),'FXYYYY-MM-DD HH24:MI');end if;
  if b.has('fact_end')then v_finish:=to_date(b.get_string('fact_end'),'FXYYYY-MM-DD HH24:MI');end if;
  if v_start is not null and v_finish is not null and v_finish<v_start then raise_application_error(-20886,'OP_FACT_FINISH_BEFORE_START');end if;
  if b.has('note')then v_note:=b.get_string('note');end if;
  update RRL_TT_OPERATIONS set FACT_START=v_start,FACT_END=v_finish,NOTE=v_note where ID=p_operation;
  result.put('op_id',p_operation);result.put('updated',true);p_result:=result.to_clob;
 exception when others then rollback to RRL_OP_FACT141;raise;
 end;
'''
s=s[:start]+body+s[start:];print(json.dumps({str(p):s},ensure_ascii=True))
