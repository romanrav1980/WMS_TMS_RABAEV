from pathlib import Path
import json
d=Path("db/migrations/2026-10-14_ni053_driver_workspace");files={}
spec=(d/"000_before_spec.sql").read_text(encoding="utf-8").replace("end;"," procedure assert_driver(p_driver number,p_actor varchar2);\n procedure mark_driver_fact(p_operation number,p_driver number,p_actor varchar2,p_action varchar2,p_result out clob);\nend;",1)
body=(d/"000_before_body.sql").read_text(encoding="utf-8")
helper=""" procedure store_fact(p_operation number,p_start date,p_finish date,p_note varchar2)is
 begin
  if p_start is not null and p_finish is not null and p_finish<p_start then raise_application_error(-20886,'OP_FACT_FINISH_BEFORE_START');end if;
  update RRL_TT_OPERATIONS set FACT_START=p_start,FACT_END=p_finish,NOTE=p_note where ID=p_operation;
 end;
 procedure assert_driver(p_driver number,p_actor varchar2)is n number;
 begin
  select count(*)into n from RRL_TRANSPORT_DRIVER_USER b join RUSERS u on u.ID=b.USER_ID
   join RRL_TR_VODITEL d on d.ID=b.DRIVER_ID
   where b.DRIVER_ID=p_driver and b.USER_ID=p_actor and b.ACTIVE=1 and nvl(u.DELETED,0)=0 and nvl(d.DELETED,0)=0;
  if n!=1 then raise_application_error(-20882,'DRIVER_CURRENT_ACCOUNT_BINDING_REQUIRED');end if;
 end;
"""
body=body.replace(" procedure actor_allowed",helper+" procedure actor_allowed",1)
needle="update RRL_TT_OPERATIONS set FACT_START=v_start,FACT_END=v_finish,NOTE=v_note where ID=p_operation;"
assert body.count(needle)==1;body=body.replace(needle,"store_fact(p_operation,v_start,v_finish,v_note);")
procedure=""" procedure mark_driver_fact(p_operation number,p_driver number,p_actor varchar2,p_action varchar2,p_result out clob)is
  before_trip number;b_user varchar2(50);b_active number;w RRL_TRANSPORT_TASK%rowtype;o RRL_TT_OPERATIONS%rowtype;
  v_now date:=sysdate;v_start date;v_finish date;changed boolean:=false;result json_object_t:=json_object_t();
 begin
  savepoint RRL_DRIVER_FACT1302;
  if p_action is null or p_action not in('START','DONE')then raise_application_error(-20886,'DRIVER_FACT_ACTION_INVALID');end if;
  assert_driver(p_driver,p_actor);
  select USER_ID,ACTIVE into b_user,b_active from RRL_TRANSPORT_DRIVER_USER where DRIVER_ID=p_driver for update nowait;
  assert_driver(p_driver,p_actor);
  select TT_ID into before_trip from RRL_TT_OPERATIONS where ID=p_operation;
  select *into w from RRL_TRANSPORT_TASK where ID=before_trip for update nowait;
  if w.VODITEL_ID is null or w.VODITEL_ID!=p_driver or nvl(w.DELETED,0)!=0 then raise_application_error(-20882,'DRIVER_TRIP_ASSIGNMENT_REQUIRED');end if;
  if nvl(w.PAY_ORDER_ID,0)>0 then raise_application_error(-20886,'DRIVER_INVOICED_TRIP_FROZEN');end if;
  select *into o from RRL_TT_OPERATIONS where ID=p_operation for update nowait;
  if o.TT_ID!=before_trip then raise_application_error(-20886,'DRIVER_OPERATION_TRIP_CHANGED');end if;
  v_start:=o.FACT_START;v_finish:=o.FACT_END;
  if p_action='START'and v_start is null then
   if v_finish is not null then raise_application_error(-20886,'DRIVER_FACT_STATE_CONFLICT');end if;
   v_start:=v_now;changed:=true;
  elsif p_action='DONE'and v_finish is null then
   if v_start is null then raise_application_error(-20886,'DRIVER_FACT_START_REQUIRED');end if;
   v_finish:=v_now;changed:=true;
  end if;
  assert_driver(p_driver,p_actor);
  if changed then store_fact(p_operation,v_start,v_finish,o.NOTE);end if;
  result.put('op_id',p_operation);result.put('trip_id',before_trip);result.put('driver_id',p_driver);
  if v_finish is not null then result.put('status','done');elsif v_start is not null then result.put('status','in_progress');else result.put('status','pending');end if;
  result.put('fact_start',to_char(v_start,'YYYY-MM-DD HH24:MI:SS'));result.put('fact_end',to_char(v_finish,'YYYY-MM-DD HH24:MI:SS'));
  result.put('changed',changed);result.put('clock_basis','EXISTING_DATABASE_LOCAL_DATE');
  result.put('stock_changed',false);p_result:=result.to_clob;
 exception when others then rollback to RRL_DRIVER_FACT1302;raise;
 end;
"""
idx=body.rfind("end;");assert idx>0;body=body[:idx]+procedure+body[idx:]
files[str(d/"001_api.sql")]=spec+"\n"+body
files[str(d/"002_ledger.sql")]=(Path("db/migrations/2026-10-14_ni022_prepared_row_move/005_ledger.sql").read_text(encoding="utf-8").replace("2026-10-14-1265-prepared-row-move","2026-10-14-1302-driver-workspace").replace("Explicit conserved prepared ST row transfer through existing writer and zero-stock Root journal","Authenticated driver current binding and idempotent existing transport operation facts"))
files[str(d/"apply.sql")]="@@001_api.sql\n@@002_ledger.sql\n"
files[str(d/"rollback.sql")]="-- Disable new driver UI/API first. Existing operation timestamps remain intact.\n@@000_before_spec.sql\n@@000_before_body.sql\n"
files[str(d/"verify.sql")]="select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME='RRL_TT_OPERATION_PLAN_API'order by SEQUENCE;\nselect OBJECT_NAME,OBJECT_TYPE,STATUS from USER_OBJECTS where OBJECT_NAME='RRL_TT_OPERATION_PLAN_API';\n"
files["wiki/database/nicora_ni053_driver_workspace_20261014.md"]="# NI05.3: текущий водитель и существующий журнал времени\n\nМиграция2026-10-14-1302-driver-workspace PREPARED. Владелец transport; существующий RRL_TT_OPERATION_PLAN_API/RRL_TT_OPERATIONS, без второго транспортного или товарного реестра. Driver workspace использует существующую RRL_TRANSPORT_DRIVER_USER и активного RUSERS. ID не является аутентификацией.\n\nДобавлены assert_driver и mark_driver_fact START/DONE: короткая транзакция, блокировкиNOWAIT в порядке binding→trip→operation; повтор текущего факта не меняет первоначальное время. DONE безSTART отвергается. Удалённый/чужой/включённый в счёт рейс недоступен. Dispatcher и driver используют один private store_fact существующего пакета. Товар/резервы не изменяются. Время сохраняет прежнюю DATABASE_LOCAL_DATE семантику; промышленная синхронизация часов не заявлена.\n\nCheckpoint000spec/body/INVALID=[], rollback восстанавливает код без удаления истории. Полный snapshot базы не нужен. Применение и actual evidence ещё ожидаются.\n"
p=Path("wiki/index.md");files[str(p)]="- [Driver workspace1302](database/nicora_ni053_driver_workspace_20261014.md): подготовлен текущий account binding и повтор временных отметок через прежний пакет.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");files[str(p)]=p.read_text(encoding="utf-8")+"\n- 2026-10-14 ·1302–1303: captured current RRL_TT_OPERATION_PLAN_API/spec+body/INVALID; prepared driver binding/native bounded locks/current facts. Live apply pending.\n"
print(json.dumps(files,ensure_ascii=True))
