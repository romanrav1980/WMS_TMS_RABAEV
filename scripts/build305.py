from pathlib import Path
import json
out={};d=Path("db/migrations/2026-10-11_ni061_partial_recovery")
def put(n,s):out[(d/n).as_posix()]=s
put("001_multiple_recoveries.sql","""declare key_name varchar2(128);n number;fk_count number;begin
 for item in(select 'RRL_INTERWARE_RECOVERY_REQUEST'TAB,'RRL_IW_REC_REQUEST_LOSS_IX'IX from dual
 union all select 'RRL_INTERWARE_RECOVERY_RECEIPT','RRL_IW_REC_RECEIPT_LOSS_IX'from dual)loop
  select count(*)into n from USER_INDEXES where INDEX_NAME=item.IX;
  if n=0 then execute immediate 'create index '||item.IX||' on '||item.TAB||'(LOSS_OPERATION_ID,OPERATION_ID)';end if;
  for old_key in(select c.CONSTRAINT_NAME from USER_CONSTRAINTS c join USER_CONS_COLUMNS col on col.CONSTRAINT_NAME=c.CONSTRAINT_NAME
   where c.TABLE_NAME=item.TAB and c.CONSTRAINT_TYPE='U'and col.COLUMN_NAME='LOSS_OPERATION_ID'
   and(select count(*)from USER_CONS_COLUMNS same_constraint where same_constraint.CONSTRAINT_NAME=c.CONSTRAINT_NAME)=1)loop
   select count(*)into fk_count from USER_CONSTRAINTS where R_CONSTRAINT_NAME=old_key.CONSTRAINT_NAME;
   if fk_count>0 then raise_application_error(-20886,'RECOVERY_LOSS_UNIQUE_REFERENCED_REQUIRES_EXPLICIT_MIGRATION');end if;
   execute immediate 'alter table '||item.TAB||' drop constraint '||dbms_assert.simple_sql_name(old_key.CONSTRAINT_NAME);
  end loop;
 end loop;
end;
/
""")
spec=(d/"000_before_rrl_stock_iw_recovery_plan_package.sql").read_text(encoding="utf-8")
s=(d/"000_before_rrl_stock_iw_recovery_plan_package_body.sql").read_text(encoding="utf-8")
s=s.replace("expected_count number;total number;","expected_count number;total number;selected_wire clob;selected_count number;allocated_qty number;request_count number;",1)
s=s.replace("if m.get_size!=3 or","if m.get_size not in(3,4)or(m.get_size=4 and not m.has('unit_keys'))or",1)
s=s.replace("or quantity!=loss.SHORT_QTY","or quantity>loss.SHORT_QTY",1)
s=s.replace("quantity+receipt.BASE_QTY!=receipt.EXPECTED_BASE_QTY","loss.SHORT_QTY+receipt.BASE_QTY!=receipt.EXPECTED_BASE_QTY",1)
a=s.index(" select count(*)into n from RRL_INTERWARE_RECOVERY_RECEIPT where LOSS_OPERATION_ID=loss_id;");b=s.index(" if expected_count>10000",a)
s=s[:a]+""" if kind='INTERWARE_RECOVERY_REPORT'then
  select nvl(sum(BASE_QTY),0),count(*)into allocated_qty,request_count from RRL_INTERWARE_RECOVERY_REQUEST where LOSS_OPERATION_ID=loss_id;
  if request_count>=1000 or quantity>loss.SHORT_QTY-allocated_qty then raise_application_error(-20886,'INTERWARE_RECOVERY_UNREPORTED_QUANTITY_EXCEEDED');end if;
 else
  if quantity!=req.BASE_QTY then raise_application_error(-20886,'INTERWARE_RECOVERY_EXACT_REPORTED_QUANTITY_REQUIRED');end if;
  select count(*)into n from RRL_INTERWARE_RECOVERY_APPROVAL where REQUEST_OPERATION_ID=req_id;if n!=0 then raise_application_error(-20886,'INTERWARE_RECOVERY_ALREADY_APPROVED');end if;
 end if;
 source:=json_object_t.parse(loss.SOURCE_JSON);
 if kind='INTERWARE_RECOVERY_REPORT'then unit_wire:=source.get_array('missing_units').to_clob;
 else unit_wire:=json_object_t.parse(req.SOURCE_JSON).get_array('source_units').to_clob;end if;
 selected_wire:=null;selected_count:=0;
 if m.has('unit_keys')then
  if m.get('unit_keys').is_null or not m.get('unit_keys').is_array then raise_application_error(-20886,'INTERWARE_RECOVERY_UNIT_KEYS_ARRAY_REQUIRED');end if;
  if kind!='INTERWARE_RECOVERY_REPORT'or m.get_array('unit_keys').get_size>10000 then raise_application_error(-20886,'INTERWARE_RECOVERY_SELECTION_BOUND');end if;
  if m.get_array('unit_keys').get_size>0 then
   selected_wire:=m.get_array('unit_keys').to_clob;
   select count(*),count(distinct K)into n,selected_count from json_table(selected_wire,'$[*]'columns(K varchar2(64)path '$'));
   if n!=selected_count then raise_application_error(-20886,'INTERWARE_RECOVERY_DUPLICATE_SELECTED_UNIT');end if;
  end if;
 end if;
 select count(*)into expected_count from json_table(unit_wire,'$[*]'columns(K varchar2(64)path '$.key'))frozen
 where(selected_wire is null or exists(select 1 from json_table(selected_wire,'$[*]'columns(K varchar2(64)path '$'))chosen where chosen.K=frozen.K))
 and not exists(select 1 from RRL_INTERWARE_RECOVERY_REQUEST claimed,
 json_table(claimed.SOURCE_JSON,'$.source_units[*]'columns(K varchar2(64)path '$.key'))allocated
 where claimed.LOSS_OPERATION_ID=loss_id and(req_id is null or claimed.OPERATION_ID!=req_id)and allocated.K=frozen.K);
 if selected_count>0 and selected_count!=expected_count then raise_application_error(-20886,'INTERWARE_RECOVERY_SELECTED_UNIT_ALREADY_REPORTED_OR_FOREIGN');end if;
"""+s[b:]
needle="and u.UNIT_VERSION=j.V and book.UNIT_VERSION=j.V;"
assert needle in s;s=s.replace(needle,"""and u.UNIT_VERSION=j.V and book.UNIT_VERSION=j.V
 and(selected_wire is null or exists(select 1 from json_table(selected_wire,'$[*]'columns(K varchar2(64)path '$'))chosen where chosen.K=j.K))
 and not exists(select 1 from RRL_INTERWARE_RECOVERY_REQUEST claimed,
 json_table(claimed.SOURCE_JSON,'$.source_units[*]'columns(K varchar2(64)path '$.key'))allocated
 where claimed.LOSS_OPERATION_ID=loss_id and(req_id is null or claimed.OPERATION_ID!=req_id)and allocated.K=j.K);""",1)
# Loss contained marked keys but no selectable current key must not be treated as ordinary.
s=s.replace("else fresh_units:='[]';end if;","else\n if json_array_t.parse(unit_wire).get_size>0 or selected_count>0 then raise_application_error(-20886,'INTERWARE_RECOVERY_MARKED_SELECTION_EXHAUSTED');end if;\n fresh_units:='[]';end if;",1)
put("002_decisions_current.sql",spec+"\n"+s)
spec=(d/"000_before_rrl_stock_iw_recovery_rec_package.sql").read_text(encoding="utf-8")
s=(d/"000_before_rrl_stock_iw_recovery_rec_package_body.sql").read_text(encoding="utf-8")
s=s.replace("leg json_object_t;unit_count number;","leg json_object_t;unit_count number;chosen_keys json_array_t;chosen_unit json_object_t;",1)
needle="  legs:=json_array_t();legs.append(leg);"
assert needle in s;s=s.replace(needle,"""  chosen_keys:=json_array_t();
  for selected_index in 0..source.get_array('source_units').get_size-1 loop
   chosen_unit:=treat(source.get_array('source_units').get(selected_index)as json_object_t);chosen_keys.append(chosen_unit.get_string('key'));
  end loop;
  leg.put('selected_unit_keys',chosen_keys);
"""+needle,1)
put("003_receiving_current.sql",spec+"\n"+s)
put("apply.sql","@@001_multiple_recoveries.sql\n@@002_decisions_current.sql\n@@003_receiving_current.sql\n@@../2026-10-08_stock_posting_core/014b_recompile.sql\n")
put("rollback.sql","""declare n number;begin
 select count(*)into n from(select LOSS_OPERATION_ID from RRL_INTERWARE_RECOVERY_REQUEST group by LOSS_OPERATION_ID having count(*)>1);
 if n>0 then raise_application_error(-20878,'RETAINED_PARTIAL_RECOVERY_REQUESTS_PREVENT_SINGLE_LOSS_ROLLBACK');end if;
 select count(*)into n from(select LOSS_OPERATION_ID from RRL_INTERWARE_RECOVERY_RECEIPT group by LOSS_OPERATION_ID having count(*)>1);
 if n>0 then raise_application_error(-20878,'RETAINED_PARTIAL_RECOVERY_RECEIPTS_PREVENT_SINGLE_LOSS_ROLLBACK');end if;
end;
/
@@000_before_rrl_stock_iw_recovery_plan_package_body.sql
@@000_before_rrl_stock_iw_recovery_rec_package_body.sql
alter table RRL_INTERWARE_RECOVERY_REQUEST add constraint RRL_IW_REC_REQ_SINGLE_LOSS unique(LOSS_OPERATION_ID);
alter table RRL_INTERWARE_RECOVERY_RECEIPT add constraint RRL_IW_REC_REC_SINGLE_LOSS unique(LOSS_OPERATION_ID);
@@../2026-10-08_stock_posting_core/014b_recompile.sql
""")
put("verify.sql","select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME in('RRL_STOCK_IW_RECOVERY_PLAN','RRL_STOCK_IW_RECOVERY_REC');\n")
out["wiki/database/nicora_ni061_partial_recovery_20261011.md"]="""# NI06.1 — частичная находка подтверждённой недостачи (305)
Одна недостача может восстанавливаться несколькими явными сообщениями/независимыми согласованиями/физическими приёмками. Старые документы immutable; UNIQUE lossID в REQUEST/RECEIPT заменяется sparse nonunique lossID+opID индексами, UNIQUE request→approval и approval→receipt сохраняются. Целое восстановление300 не меняет смысл.

В report scalarqty<=не заявленная часть loss; сумма requestqty под общей ROW20LOSS не превышает confirmedloss. Для marked товаров выбрать точные frozen physicalunit keys, не выбирать SKUbarcode вместоQR. Ключи из другой недостачи/повторные/уже включённые в другой report запрещены. Native currentISSUED/oldUID/noH/qty/UOM/version и точный frozenbook обязательны. Approval фиксирует исходный selectedsubset, другойсогласующий/currentWARE, qtyexactrequest. До физической приёмки запас0; эта заявка не складской HARD.

Физическая приёмка использует старый markscanselected_unit_keys (292), exact currentSKUprofiles QR каждого выбранногоunit и samecore partialpallet/UNIT correction300. Остальные ещё потерянные единицы остаются ISSUED/blocked by active lossbook. UNIT locks +LOSS ROW mutex/underlockrecapture serialise overlappingclaims; независимые операции не берут общийstockSRX. Каждая найденная часть получает самостоятельный UID/task/ST/finalreceipt; originalFF не повторяется.

Границы: readmodel/UI должны показывать все reports и сумму found, netmissing отдельно. Cancellation заявленной, но не принятой находки нужен отдельный journal command следующим ticket. До его реализации не удалять requests ради повторного report. Max1000 recoveryreports на один loss; больше явно отклоняются.
"""
p=Path("wiki/index.md");out[p.as_posix()]="- [Частичная находка недостачи](database/nicora_ni061_partial_recovery_20261011.md):305 separate selected-unit reports/approval/receipt and bounded total; read/UI/cancellation next.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");out[p.as_posix()]=p.read_text(encoding="utf-8")+"\n- 11.10.2026 305 design/checkpoint: current recovery PLAN/REC source captured; two LOSS singleUK FK0. Partial selected-units/report-total admission +existing292scan planned; no wholecase regression or partial runtime acceptance yet.\n"
print(json.dumps(out))
