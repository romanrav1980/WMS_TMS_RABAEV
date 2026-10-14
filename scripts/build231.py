from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni062_marked_approval");out={}
out[str(f/"001_schema.sql")]="""create table RRL_STORE_RETURN_UNIT(
 APPROVAL_OPERATION_ID varchar2(100)not null,
 RECEIPT_OPERATION_ID varchar2(100)not null,
 PHYSICAL_UNIT_KEY varchar2(64)not null,
 ORIGINAL_UID varchar2(150)not null,
 SOURCE_CELL varchar2(60)not null,
 BASE_QTY number(27,9)not null,
 BASE_UOM varchar2(20)not null,
 SOURCE_UNIT_VERSION number not null,
 constraint RRL_STORE_RETUNIT_PK primary key(APPROVAL_OPERATION_ID,PHYSICAL_UNIT_KEY),
 constraint RRL_STORE_RETUNIT_SOURCE_UK unique(RECEIPT_OPERATION_ID,PHYSICAL_UNIT_KEY),
 constraint RRL_STORE_RETUNIT_APP_FK foreign key(APPROVAL_OPERATION_ID)references RRL_STORE_RETURN_APPROVAL(OPERATION_ID),
 constraint RRL_STORE_RETUNIT_FACT_FK foreign key(RECEIPT_OPERATION_ID)references RRL_STORE_RECEIPT_FACT(OPERATION_ID),
 constraint RRL_STORE_RETUNIT_UNIT_FK foreign key(PHYSICAL_UNIT_KEY)references RRL_WMS_RECEIPT_UNIT(PHYSICAL_UNIT_KEY),
 constraint RRL_STORE_RETUNIT_QTY_CK check(BASE_QTY>0 and SOURCE_UNIT_VERSION>=0)
);
"""
out[str(f/"002_unit_source.sql")]="""create or replace package RRL_STORE_RETURN_UNIT_CORE authid definer as
 function accepted_units(p_receipt varchar2,p_uid varchar2,p_uom varchar2)return clob;
 function select_units(p_receipt varchar2,p_uid varchar2,p_uom varchar2,p_qty number,p_keys clob)return clob;
 procedure persist(p_approval varchar2,p_receipt varchar2,p_uid varchar2,p_cell varchar2,p_units clob);
end;
/
create or replace package body RRL_STORE_RETURN_UNIT_CORE as
 function accepted_units(p_receipt varchar2,p_uid varchar2,p_uom varchar2)return clob is
  proof clob;cell_text varchar2(60);state_text varchar2(30);fact_count number;wire clob;
 begin
  select json_value(COMPOSITION_JSON,'$.cell'),RECEIPT_STATE into cell_text,state_text from RRL_STORE_RECEIPT_FACT where OPERATION_ID=p_receipt;
  select RESOLVED_PLAN_JSON into proof from RRL_STOCK_OPERATION where OPERATION_ID=p_receipt and COMMAND_TYPE='STORE_RECEIPT'and STATE='APPLIED';
  select count(*)into fact_count from RRL_STORE_RECEIPT_UNIT where OPERATION_ID=p_receipt;
  if fact_count=0 and state_text!='ACCEPTED'then raise_application_error(-20886,'STORE_RETURN_ACCEPTED_UNIT_EVIDENCE_REQUIRED');end if;
  select json_arrayagg(json_object('key'value u.PHYSICAL_UNIT_KEY,'quantity'value RRL_STOCK_PLAN_HELPER.decimal_text(u.BASE_QTY),'base_uom'value u.BASE_UOM,'version'value u.UNIT_VERSION)order by u.PHYSICAL_UNIT_KEY returning clob)into wire
   from RRL_WMS_RECEIPT_UNIT u join(
    select PHYSICAL_UNIT_KEY K,BASE_QTY Q,BASE_UOM B,SOURCE_UNIT_VERSION V from RRL_STORE_RECEIPT_UNIT where OPERATION_ID=p_receipt and UNIT_DISPOSITION='ACCEPTED'
    union all
    select j.K,RRL_STOCK_MATH.quantity(j.Q),j.B,j.V from json_table(proof,'$.domain.marked_unit_proof.units[*]'columns(K varchar2(64)path '$.key',Q varchar2(60)path '$.quantity',B varchar2(20)path '$.base_uom',V number path '$.version'))j where fact_count=0 and state_text='ACCEPTED'
   )source on source.K=u.PHYSICAL_UNIT_KEY and source.Q=u.BASE_QTY and source.B=u.BASE_UOM and source.V=u.UNIT_VERSION
   where u.CURRENT_UID=p_uid and u.CURRENT_CELL=cell_text and u.BASE_UOM=p_uom and u.STOCK_STATUS='ISSUED'and u.HARD_RESERVATION_ID is null
   and not exists(select 1 from RRL_STORE_RETURN_UNIT b where b.RECEIPT_OPERATION_ID=p_receipt and b.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY);
  return nvl(wire,to_clob('[]'));
 end;
 function select_units(p_receipt varchar2,p_uid varchar2,p_uom varchar2,p_qty number,p_keys clob)return clob is
  wire clob:=accepted_units(p_receipt,p_uid,p_uom);n number;distinct_count number;chosen number;total number;result_wire clob;
 begin
  select count(*),count(distinct K)into n,distinct_count from json_table(p_keys,'$[*]'columns(K varchar2(64)path '$'));
  if n<1 or n>10000 or n!=distinct_count then raise_application_error(-20886,'STORE_RETURN_EXACT_UNIT_SELECTION_REQUIRED');end if;
  select count(*),sum(RRL_STOCK_MATH.quantity(j.Q)),
   json_arrayagg(json_object('key'value j.K,'quantity'value j.Q,'base_uom'value j.B,'version'value j.V)order by j.K returning clob)
   into chosen,total,result_wire from json_table(wire,'$[*]'columns(K varchar2(64)path '$.key',Q varchar2(60)path '$.quantity',B varchar2(20)path '$.base_uom',V number path '$.version'))j
   where j.K in(select K from json_table(p_keys,'$[*]'columns(K varchar2(64)path '$')));
  if chosen!=n or total!=p_qty then raise_application_error(-20886,'STORE_RETURN_ACCEPTED_SELECTED_UNIT_QUANTITY_REQUIRED');end if;
  return result_wire;
 end;
 procedure persist(p_approval varchar2,p_receipt varchar2,p_uid varchar2,p_cell varchar2,p_units clob)is
  a json_array_t:=json_array_t.parse(p_units);x json_object_t;k varchar2(64);qty number;uom varchar2(20);v number;
 begin
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i)as json_object_t);k:=x.get_string('key');qty:=RRL_STOCK_MATH.quantity(x.get_string('quantity'));uom:=x.get_string('base_uom');v:=x.get_number('version');
   insert into RRL_STORE_RETURN_UNIT(APPROVAL_OPERATION_ID,RECEIPT_OPERATION_ID,PHYSICAL_UNIT_KEY,ORIGINAL_UID,SOURCE_CELL,BASE_QTY,BASE_UOM,SOURCE_UNIT_VERSION)
    values(p_approval,p_receipt,k,p_uid,p_cell,qty,uom,v);
  end loop;
 end;
end;
/
"""
s=(f/"000_before_rrl_stock_store_return_cmd.sql").read_text(encoding="utf-8")
s=s.replace(" procedure compile_command("," procedure assert_actor(p_actor varchar2);\n procedure compile_command(",1)
s=s.replace("package body RRL_STOCK_STORE_RETURN_CMD as","""package body RRL_STOCK_STORE_RETURN_CMD as
 procedure assert_actor(p_actor varchar2)is n number;
 begin select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0 and RRL_HAS_WRIGHT(ID,'store_return_approve')=1;if n!=1 then raise_application_error(-20882,'STORE_RETURN_CURRENT_APPROVER_REQUIRED');end if;end;""")
s=s.replace("v_load varchar2(100);","v_load varchar2(100);selected_units clob;source_cell varchar2(60);",1)
s=s.replace(" if v_units!=0 then raise_application_error(-20886,'STORE_RETURN_MARKED_UNIT_ALLOCATION_REQUIRED');end if;","")
s=s.replace(" p_domain:=json_object_t();",""" p_domain:=json_object_t();
 if v_units>0 then
  if not m.has('unit_keys')then raise_application_error(-20886,'STORE_RETURN_EXACT_UNIT_SELECTION_REQUIRED');end if;
  selected_units:=RRL_STORE_RETURN_UNIT_CORE.select_units(v_receipt,original.LOT_UID,original.BASE_UOM,v_qty,m.get_array('unit_keys').to_clob);
  select json_value(COMPOSITION_JSON,'$.cell')into source_cell from RRL_STORE_RECEIPT_FACT where OPERATION_ID=v_receipt;
  p_domain.put('return_units',json_array_t.parse(selected_units));p_domain.put('source_cell',source_cell);
 elsif m.has('unit_keys')and m.get_array('unit_keys').get_size>0 then raise_application_error(-20886,'STORE_RETURN_UNEXPECTED_UNIT_SELECTION');end if;
""",1)
s=s.replace("r json_array_t:=json_array_t();","r json_array_t:=json_array_t();units json_array_t;x json_object_t;",1)
s=s.replace(" p_policies:=f.to_clob;",""" if v.has('return_units')then
  RRL_STOCK_PLAN_HELPER.stock_closure(f,r,v.get_string('lot_uid'),v.get_string('article'),v.get_string('source_cell'),null);
  units:=v.get_array('return_units');for i in 0..units.get_size-1 loop x:=treat(units.get(i)as json_object_t);RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STORE_RETURN_UNIT',p_operation||':'||x.get_string('key'));end loop;
 end if;
 p_policies:=f.to_clob;""",1)
s=s.replace(" j.put('operation_id',op);",""" if v.has('return_units')then
  RRL_STORE_RETURN_UNIT_CORE.persist(op,v_receipt,v_lot,v.get_string('source_cell'),v.get_array('return_units').to_clob);j.put('physical_unit_count',v.get_array('return_units').get_size);
 end if;
 j.put('operation_id',op);""",1)
out[str(f/"003_approval.sql")]=s
out[str(f/"004_guard.sql")]="""create or replace trigger RRL_STORE_RETURN_UNIT_GUARD before insert or update or delete on RRL_STORE_RETURN_UNIT for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');n number;
begin
 if not inserting then raise_application_error(-20863,'STORE_RETURN_UNIT_APPEND_ONLY');end if;
 if op is null or op!=:new.APPROVAL_OPERATION_ID or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)then raise_application_error(-20863,'STORE_RETURN_UNIT_ROOT_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STORE_RETURN_UNIT',op||':'||:new.PHYSICAL_UNIT_KEY));
 RRL_STOCK_LOCK_API.assert_held(60,RRL_STOCK_LOCK_API.resource_key('UNIT',:new.PHYSICAL_UNIT_KEY));
 select count(*)into n from RRL_STOCK_OPERATION o join json_table(o.RESOLVED_PLAN_JSON,'$.domain.return_units[*]'columns(K varchar2(64)path '$.key',Q varchar2(60)path '$.quantity',B varchar2(20)path '$.base_uom',V number path '$.version'))u
 on u.K=:new.PHYSICAL_UNIT_KEY and RRL_STOCK_MATH.quantity(u.Q)=:new.BASE_QTY and u.B=:new.BASE_UOM and u.V=:new.SOURCE_UNIT_VERSION
 where o.OPERATION_ID=op and o.COMMAND_TYPE='STORE_RETURN_APPROVE'and o.STATE='IN_FLIGHT'
 and json_value(o.RESOLVED_PLAN_JSON,'$.domain.receipt_operation_id')=:new.RECEIPT_OPERATION_ID and json_value(o.RESOLVED_PLAN_JSON,'$.domain.lot_uid')=:new.ORIGINAL_UID and json_value(o.RESOLVED_PLAN_JSON,'$.domain.source_cell')=:new.SOURCE_CELL;
 if n!=1 then raise_application_error(-20863,'STORE_RETURN_UNIT_FROZEN_SOURCE_REQUIRED');end if;
end;
/
"""
s=(f/"000_before_rrl_stock_posting_api.sql").read_text(encoding="utf-8")
s=s.replace("  if g_kind='STORE_RECEIPT'then","  if g_kind='STORE_RETURN_APPROVE'then RRL_STOCK_STORE_RETURN_CMD.assert_actor(p_actor);end if;\n  if g_kind='STORE_RECEIPT'then")
out[str(f/"005_root.sql")]=s
out[str(f/"006_recompile.sql")]="alter package RRL_STOCK_POSTING_API compile body;\n"
out[str(f/"rollback.sql")]="declare n number;begin select count(*)into n from RRL_STORE_RETURN_UNIT;if n>0 then raise_application_error(-20863,'MARKED_RETURN_APPROVAL_FORWARD_REPAIR_REQUIRED');end if;end;\n/\n@@000_before_rrl_stock_store_return_cmd.sql\n@@000_before_rrl_stock_posting_api.sql\n@@006_recompile.sql\ndrop trigger RRL_STORE_RETURN_UNIT_GUARD;\ndrop table RRL_STORE_RETURN_UNIT;\ndrop package RRL_STORE_RETURN_UNIT_CORE;\n"
out["wiki/database/nicora_ni062_marked_approval_design_20261011.md"]="# NI06.2: конкретные ранее принятые маркированные единицы в возврате\n231 retains original Supply Chain approval and accepted-only cap. Selected original ACCEPTED physical units/current issued binding/version/quantity/UOM must match, immutable unique receipt-unit allocation prevents duplicate approvals. Missing/refused/damaged at first delivery stay in original discrepancy, not accepted return pool. Legacy229 full marked acceptance uses frozen original proof without rewriting old receipt;230 receipts use explicit per-unit facts. Approval/outbox/allocation atomic, no P/H/stock event/GovACK. Fresh owner checkpoint/empty-child rollback; physical pickup/warehouse quarantine next.\n"
print(json.dumps(out,ensure_ascii=True))
