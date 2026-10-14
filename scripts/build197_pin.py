from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni042_weight_unit_pin");out={}
out[str(f/"001_reader.sql")]="""create or replace package RRL_WEIGHT_CHOICE_UNIT_READ authid definer
 accessible by(package RRL_STOCK_WAVE_LAUNCH_CMD,package RRL_STOCK_WAVE_CMD) as
 function selected_units(p_task number,p_uid varchar2,p_cell varchar2,p_qty number)return clob;
end;
/
create or replace package body RRL_WEIGHT_CHOICE_UNIT_READ as
 function selected_units(p_task number,p_uid varchar2,p_cell varchar2,p_qty number)return clob is
  c RRL_PICK_WEIGHT_CHOICE%rowtype;u RRL_WMS_RECEIPT_UNIT%rowtype;
  n number;line_id number;policy_version number;serialized number;available_qty number;a json_array_t:=json_array_t();
 begin
  if p_task is null then return null;end if;
  select PICK_PLAN_LINE_ID into line_id from RRL_PICK_TASK where PICK_TASK_ID=p_task;
  select count(*)into n from RRL_PICK_WEIGHT_CHOICE where PICK_PLAN_LINE_ID=line_id and STATUS='USED';
  if n=0 then return null;end if;
  if n!=1 then raise_application_error(-20886,'WEIGHT_CHOICE_SINGLE_BOUND_UNIT_REQUIRED');end if;
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')is null
   or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)
   then raise_application_error(-20863,'WEIGHT_CHOICE_NATIVE_POSTING_CONTEXT_REQUIRED');end if;
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_uid));
  select *into c from RRL_PICK_WEIGHT_CHOICE where PICK_PLAN_LINE_ID=line_id and STATUS='USED';
  select POLICY_VERSION,SERIALIZED_WEIGHT_BOXES into policy_version,serialized from RRL_SKU_RECEIPT_POLICY where ARTICUL=c.ARTICLE;
  if serialized!=1 or policy_version!=c.POLICY_VERSION then raise_application_error(-20886,'WEIGHT_CHOICE_CURRENT_SKU_POLICY_CHANGED');end if;
  select *into u from RRL_WMS_RECEIPT_UNIT where PHYSICAL_UNIT_KEY=c.PHYSICAL_UNIT_KEY;
  if u.CURRENT_UID!=p_uid or u.CURRENT_CELL!=p_cell or u.STOCK_STATUS!='AVAILABLE'or u.HARD_RESERVATION_ID is not null
   or u.BASE_QTY!=c.NET_WEIGHT_KG then raise_application_error(-20886,'WEIGHT_CHOICE_SELECTED_UNIT_UNAVAILABLE');end if;
  if p_qty=c.NET_WEIGHT_KG then a.append(c.PHYSICAL_UNIT_KEY);return a.to_clob;end if;
  -- A source full-pallet reservation may include the chosen box together with every other free box.
  -- Smaller partial substitutions must never silently replace the approved physical key.
  select nvl(sum(BASE_QTY),0)into available_qty from RRL_WMS_RECEIPT_UNIT
   where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS='AVAILABLE'and HARD_RESERVATION_ID is null;
  if p_qty>c.NET_WEIGHT_KG and p_qty=available_qty then return null;end if;
  raise_application_error(-20886,'WEIGHT_CHOICE_EXACT_BOX_OR_WHOLE_SOURCE_REQUIRED');
 end;
end;
/
"""
s=(f/"000_before_launch.sql").read_text(encoding="utf-8")
old="   units:=RRL_STOCK_UNIT_CORE.automatic_units(pr.PALLET_UID,pr.SOURCE_CELL_CODE,pr.RESERVED_QTY);"
new="""   units:=RRL_WEIGHT_CHOICE_UNIT_READ.selected_units(pr.PICK_TASK_ID,pr.PALLET_UID,pr.SOURCE_CELL_CODE,pr.RESERVED_QTY);
   if units is null then units:=RRL_STOCK_UNIT_CORE.automatic_units(pr.PALLET_UID,pr.SOURCE_CELL_CODE,pr.RESERVED_QTY);end if;"""
assert old in s;out[str(f/"002_launch.sql")]=s.replace(old,new)
s=(f/"000_before_replenish.sql").read_text(encoding="utf-8")
old="   v_units:=RRL_STOCK_UNIT_CORE.automatic_units(v_uid,v_cell,v_qty);"
new="""   v_units:=RRL_WEIGHT_CHOICE_UNIT_READ.selected_units(rt.PICK_TASK_ID,v_uid,v_cell,v_qty);
   if v_units is null then v_units:=RRL_STOCK_UNIT_CORE.automatic_units(v_uid,v_cell,v_qty);end if;"""
assert s.count(old)==1;s=s.replace(old,new)
old="    v_units:=RRL_STOCK_UNIT_CORE.automatic_units(x.get_string('uid'),x.get_string('cell'),v_qty);"
new="""    v_units:=RRL_WEIGHT_CHOICE_UNIT_READ.selected_units(rt.PICK_TASK_ID,x.get_string('uid'),x.get_string('cell'),v_qty);
    if v_units is null then v_units:=RRL_STOCK_UNIT_CORE.automatic_units(x.get_string('uid'),x.get_string('cell'),v_qty);end if;"""
assert s.count(old)==1;out[str(f/"003_replenish.sql")]=s.replace(old,new)
out[str(f/"004_index.sql")]="create index RRL_WEIGHT_CHOICE_PLAN_I on RRL_PICK_WEIGHT_CHOICE(PICK_PLAN_LINE_ID,STATUS);\n"
out[str(f/"apply.sql")]="@@001_reader.sql\n@@002_launch.sql\n@@003_replenish.sql\n@@004_index.sql\n"
out[str(f/"rollback.sql")]="@@000_before_launch.sql\n@@000_before_replenish.sql\ndrop package RRL_WEIGHT_CHOICE_UNIT_READ;\ndrop index RRL_WEIGHT_CHOICE_PLAN_I;\n"
out["wiki/database/nicora_ni042_weight_unit_pin_design_20261011.md"]="""# NI04.2: физическая коробка утверждённого плана
197 planned exact selected physical key supplied to existing native WAVE_LAUNCH and replenishment HARD owners. Read-only accessible-by helper/current native TX/sourceUID50 locks checks linked USED choice/current SKU policy/current AVAILABLE unit and exact net. Ordinary nochoice returns null then old allocator. Full source supply may include all free boxes; partial substitution refuses. Existing UNIT_CORE.reserve_units and single posting root remain sole effect executor. Original frozen source identifiers retain history; current legal relocation identified by physical key.
"""
p=Path("wiki/index.md");out[str(p)]=p.read_text(encoding="utf-8")+"\n- [Проект закрепления коробки](database/nicora_ni042_weight_unit_pin_design_20261011.md):197 existing native HARD owners/exact physical key/no new writer.\n"
p=Path("wiki/log.md");out[str(p)]=p.read_text(encoding="utf-8")+"\n2026-10-11:197 design exact approved physical unit/current native HARD owner/current source lock; original all-free full source allowed, partial substitution refused.\n"
print(json.dumps(out,ensure_ascii=True))
