from pathlib import Path
import json
out={};d=Path("db/migrations/2026-10-11_ni061_recurrent_loss")
def put(n,s):out[(d/n).as_posix()]=s
put("001_event_unit_keys.sql","""declare n number;fk_count number;pk_name varchar2(128);begin
 for item in(select 'RRL_INTERWARE_SHORTAGE_UNIT'TAB,'FACT_OPERATION_ID'EVENT_COL,'RRL_IW_LOSS_EVENT_UNIT_PK'PK_NAME,'RRL_IW_LOSS_EVENT_UNIT_UK'IX_NAME from dual
 union all select 'RRL_INTERWARE_RECOVERY_UNIT','RECOVERY_OPERATION_ID','RRL_IW_REC_EVENT_UNIT_PK','RRL_IW_REC_EVENT_UNIT_UK'from dual)loop
 select count(*)into n from USER_CONSTRAINTS where TABLE_NAME=item.TAB and CONSTRAINT_NAME=item.PK_NAME and CONSTRAINT_TYPE='P';
 if n=0 then
  select CONSTRAINT_NAME into pk_name from USER_CONSTRAINTS where TABLE_NAME=item.TAB and CONSTRAINT_TYPE='P';
  select count(*)into fk_count from USER_CONSTRAINTS where R_CONSTRAINT_NAME=pk_name;
  if fk_count>0 then raise_application_error(-20886,'EVENT_UNIT_PK_REFERENCED_REQUIRES_EXPLICIT_MIGRATION');end if;
  select count(*)into n from USER_INDEXES where INDEX_NAME=item.IX_NAME;
  if n=0 then execute immediate 'create unique index '||item.IX_NAME||' on '||item.TAB||'(PHYSICAL_UNIT_KEY,'||item.EVENT_COL||')';end if;
  execute immediate 'alter table '||item.TAB||' drop primary key';
  execute immediate 'alter table '||item.TAB||' add constraint '||item.PK_NAME||' primary key(PHYSICAL_UNIT_KEY,'||item.EVENT_COL||') using index '||item.IX_NAME;
 end if;
 end loop;
end;
/
""")
spec=(d/"000_before_rrl_stock_interware_short_cmd_package.sql").read_text(encoding="utf-8")
body=(d/"000_before_rrl_stock_interware_short_cmd_package_body.sql").read_text(encoding="utf-8")
needle="and not exists(select 1 from RRL_INTERWARE_SHORTAGE_UNIT booked where booked.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY);"
assert needle in body
body=body.replace(needle,"""and not exists(select 1 from RRL_INTERWARE_SHORTAGE_UNIT booked where booked.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY
    and not exists(select 1 from RRL_INTERWARE_RECOVERY_UNIT recovered join RRL_STOCK_OPERATION restored on restored.OPERATION_ID=recovered.RECOVERY_OPERATION_ID
     where recovered.PHYSICAL_UNIT_KEY=booked.PHYSICAL_UNIT_KEY and recovered.LOSS_OPERATION_ID=booked.FACT_OPERATION_ID
     and restored.STATE='APPLIED'and restored.COMMAND_TYPE='INTERWARE_SHORTAGE_RECOVER'));""",1)
put("002_command_current.sql",spec+"\n"+body)
put("003_unit_guard.sql","""create or replace trigger RRL_IW_SHORT_UNIT_G before insert or update or delete on RRL_INTERWARE_SHORTAGE_UNIT for each row
declare n number;begin
 if updating or deleting then raise_application_error(-20863,'INTERWARE_SHORTAGE_HISTORY_IMMUTABLE');end if;
 RRL_IW_SHORTAGE_GUARD.require_command(:new.FACT_OPERATION_ID,'INTERWARE_SHORTAGE_CONFIRM');
 RRL_STOCK_LOCK_API.assert_held(60,RRL_STOCK_LOCK_API.resource_key('UNIT',:new.PHYSICAL_UNIT_KEY));
 select count(*)into n from RRL_STOCK_OPERATION operation,
 json_table(operation.RESOLVED_PLAN_JSON,'$.domain.missing_units[*]'columns(K varchar2(64)path '$.key',Q varchar2(60)path '$.quantity',B varchar2(20)path '$.base_uom',V number path '$.version'))frozen,
 RRL_WMS_RECEIPT_UNIT unit_row
 where operation.OPERATION_ID=:new.FACT_OPERATION_ID and operation.STATE='IN_FLIGHT'and operation.COMMAND_TYPE='INTERWARE_SHORTAGE_CONFIRM'
 and frozen.K=:new.PHYSICAL_UNIT_KEY and RRL_STOCK_MATH.quantity(frozen.Q)=:new.BASE_QTY and frozen.B=:new.BASE_UOM and frozen.V=:new.UNIT_VERSION
 and unit_row.PHYSICAL_UNIT_KEY=frozen.K and unit_row.CURRENT_UID=:new.ORIGINAL_UID and unit_row.STOCK_STATUS='ISSUED'
 and unit_row.UNIT_VERSION=:new.UNIT_VERSION and unit_row.BASE_QTY=:new.BASE_QTY and unit_row.BASE_UOM=:new.BASE_UOM and unit_row.HARD_RESERVATION_ID is null;
 if n!=1 then raise_application_error(-20886,'INTERWARE_LOSS_EXACT_CAPTURED_CURRENT_UNIT_REQUIRED');end if;
end;
/
""")
put("apply.sql","@@001_event_unit_keys.sql\n@@002_command_current.sql\n@@003_unit_guard.sql\n@@../2026-10-08_stock_posting_core/014b_recompile.sql\n")
put("rollback.sql","""declare n number;begin
 select count(*)into n from(select PHYSICAL_UNIT_KEY from RRL_INTERWARE_SHORTAGE_UNIT group by PHYSICAL_UNIT_KEY having count(*)>1);
 if n>0 then raise_application_error(-20878,'RETAINED_RECURRENT_LOSS_CANNOT_ROLL_BACK_SINGLE_KEY');end if;
 select count(*)into n from(select PHYSICAL_UNIT_KEY from RRL_INTERWARE_RECOVERY_UNIT group by PHYSICAL_UNIT_KEY having count(*)>1);
 if n>0 then raise_application_error(-20878,'RETAINED_RECURRENT_RECOVERY_CANNOT_ROLL_BACK_SINGLE_KEY');end if;
end;
/
@@000_before_rrl_stock_interware_short_cmd_package_body.sql
@@../2026-10-11_ni061_shortage_disposition/003_guards.sql
alter table RRL_INTERWARE_SHORTAGE_UNIT drop primary key;
alter table RRL_INTERWARE_SHORTAGE_UNIT add constraint RRL_IW_LOSS_SINGLE_UNIT_PK primary key(PHYSICAL_UNIT_KEY);
alter table RRL_INTERWARE_RECOVERY_UNIT drop primary key;
alter table RRL_INTERWARE_RECOVERY_UNIT add constraint RRL_IW_REC_SINGLE_UNIT_PK primary key(PHYSICAL_UNIT_KEY);
@@../2026-10-08_stock_posting_core/014b_recompile.sql
""")
put("verify.sql","select CONSTRAINT_NAME,TABLE_NAME,STATUS from USER_CONSTRAINTS where CONSTRAINT_NAME in('RRL_IW_LOSS_EVENT_UNIT_PK','RRL_IW_REC_EVENT_UNIT_PK');\nselect NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME in('RRL_STOCK_INTERWARE_SHORT_CMD','RRL_IW_SHORT_UNIT_G');\n")
out["wiki/database/nicora_ni061_recurrent_loss_20261011.md"]="""# NI06.1: повторные события недостачи — 304
Вход: новый настоящий межскладской partialreceipt с теми же физическими единицами после полного предыдущего восстановления. Права/currentWARE/независимое подтверждение, SOURCE/UNIT versions и UOW принадлежат прежнему RRL_STOCK_INTERWARE_SHORT_CMD/RRL_STOCK_POSTING_API. Нет нового quantitywriter.

Проблема: оба журнала 295/300 имели единственный PHYSICAL_UNIT_KEY PK и запрет любого старого lossbook. Это запрещало последующую настоящую недостачу после найденного товара.
Изменение: PK (PHYSICAL_UNIT_KEY, FACT_OPERATION_ID) для loss и (PHYSICAL_UNIT_KEY, RECOVERY_OPERATION_ID) для recovery. Все прежние факты сохраняются; индекс сохраняет hot prefix physicalkey. Новый уникальный индекс создаётся до удаления прежнего PK; реальные FK dependencies проверены (0), ничего не удаляется из журналов. Новый акт разрешён только когда для каждого прежнего loss существует точная APPLIED recovery samekey+sameLOSS; актуальная нетронутая недостача по-прежнему блокирует. Native UNIT locks серийно защищают проверку и INSERT нового факта, afterwait execute повторно описывает источник.

INSERT lossguard теперь дополнительно проверяет точный key/qty/UOM/version исходного missing_units frozen domain и currentISSUED/currentoriginalUID/unreserved. Прямой INSERT без текущего native command/unitmutex запрещён. История immutable. Guard ordinaryunit уже считает каждую не восстановленную pair key+loss, поэтому позже появившийся акт не маскируется старой APPLIED recovery.

Бounded scope: журнал и допуск повторного события. Whole recovery пока сохранён; частичная находка — следующий отдельный ticket. Полный физический второй цикл на одной единице должен использовать настоящий возврат/новую отгрузку, а не ручную подмену текущего UID/status. Не выдавать изменение PK за независимую end-to-end приёмку.
"""
p=Path("wiki/index.md");out[p.as_posix()]="- [Повторные события недостачи](database/nicora_ni061_recurrent_loss_20261011.md):304 event+unit journal keys/current active-loss admission; physical secondcycle pending.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");out[p.as_posix()]=p.read_text(encoding="utf-8")+"\n- 11.10.2026 304 design/checkpoint: actualloss/recovery2rows2qty each, PK externalFK0; event+physicalunit keys and active-loss guarded admission designed. Same native writer/UNITmutex, immutable old history; no physical secondcycle claimed.\n"
print(json.dumps(out))
