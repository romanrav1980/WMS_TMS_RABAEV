from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni062_marked_receiving");out={}
s=(f/"000_before_rrl_stock_unit_core.sql").read_text(encoding="utf-8").replace("accessible by(package RRL_STOCK_INTERWARE_REC","accessible by(package RRL_STOCK_STORE_RETURN_REC_CMD,package RRL_STOCK_INTERWARE_REC",1)
s=s.replace(" procedure receive_issued"," procedure receive_return(p_old_uid varchar2,p_source_cell varchar2,p_uid varchar2,p_target_cell varchar2,p_qty number,p_units clob);\n procedure receive_issued",1)
method=""" procedure receive_return(p_old_uid varchar2,p_source_cell varchar2,p_uid varchar2,p_target_cell varchar2,p_qty number,p_units clob)is
  op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');n number;expected_count number;actual_count number:=0;total number:=0;locked_version number;
 begin
  require_context;RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_old_uid));RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_uid));
  select count(*)into n from RRL_STOCK_OPERATION o join json_table(o.RESOLVED_PLAN_JSON,'$.domain'columns(O varchar2(150)path '$.original_lot_uid',U varchar2(150)path '$.uid',S varchar2(60)path '$.return_source_cell',T varchar2(60)path '$.receive_cell',Q varchar2(60)path '$.quantity',A clob format json path '$.return_unit_proof.units'))d
   on d.O=p_old_uid and d.U=p_uid and d.S=p_source_cell and d.T=p_target_cell and d.Q=RRL_STOCK_PLAN_HELPER.decimal_text(p_qty)and dbms_lob.compare(d.A,p_units)=0
   where o.OPERATION_ID=op and o.COMMAND_TYPE='STORE_RETURN_RECEIVE'and o.STATE='IN_FLIGHT';
  if n!=1 then raise_application_error(-20863,'STORE_RETURN_EXACT_UNIT_RECEIPT_PLAN_REQUIRED');end if;
  select count(*),count(distinct K)into expected_count,n from json_table(p_units,'$[*]'columns(K varchar2(64)path '$.key'));
  if expected_count<1 or expected_count>10000 or n!=expected_count then raise_application_error(-20884,'STORE_RETURN_EXACT_UNIT_SET_REQUIRED');end if;
  for x in(select u.PHYSICAL_UNIT_KEY,u.UNIT_VERSION,u.STOCK_STATUS,u.HARD_RESERVATION_ID,u.BASE_QTY,u.BASE_UOM,j.V,j.Q,j.B
   from RRL_WMS_RECEIPT_UNIT u join json_table(p_units,'$[*]'columns(K varchar2(64)path '$.key',V number path '$.version',Q varchar2(60)path '$.quantity',B varchar2(20)path '$.base_uom'))j on j.K=u.PHYSICAL_UNIT_KEY
   where u.CURRENT_UID=p_old_uid and u.CURRENT_CELL=p_source_cell order by u.PHYSICAL_UNIT_KEY)loop
   own_unit(x.PHYSICAL_UNIT_KEY);
   select UNIT_VERSION into locked_version from RRL_WMS_RECEIPT_UNIT where PHYSICAL_UNIT_KEY=x.PHYSICAL_UNIT_KEY for update;
   if locked_version!=x.V or x.UNIT_VERSION!=x.V or x.STOCK_STATUS!='ISSUED'or x.HARD_RESERVATION_ID is not null or x.BASE_QTY!=RRL_STOCK_MATH.quantity(x.Q)or x.BASE_UOM!=x.B then raise_application_error(-20890,'CLOSURE_CHANGED: original return unit');end if;
   actual_count:=actual_count+1;total:=total+x.BASE_QTY;
  end loop;
  if actual_count!=expected_count or total!=p_qty then raise_application_error(-20884,'STORE_RETURN_ORIGINAL_UNIT_QUANTITY_CONFLICT');end if;
  RRL_STOCK_CTX_API.begin_effect('UNIT',p_old_uid,p_source_cell);
  update RRL_WMS_RECEIPT_UNIT u set CURRENT_UID=p_uid,CURRENT_CELL=p_target_cell,STOCK_STATUS='AVAILABLE',HARD_RESERVATION_ID=null,UNIT_VERSION=UNIT_VERSION+1
   where CURRENT_UID=p_old_uid and CURRENT_CELL=p_source_cell and STOCK_STATUS='ISSUED'and exists(select 1 from json_table(p_units,'$[*]'columns(K varchar2(64)path '$.key'))j where j.K=u.PHYSICAL_UNIT_KEY);
  if sql%rowcount!=expected_count then raise_application_error(-20890,'CLOSURE_CHANGED: original returned unit count');end if;
  RRL_STOCK_CTX_API.end_effect;assert_composition(p_uid,p_target_cell);assert_composition(p_old_uid,p_source_cell);
 exception when others then RRL_STOCK_CTX_API.end_effect;raise;
 end;
"""
i=s.rindex("end;");s=s[:i]+method+s[i:];out[str(f/"001_unit_core.sql")]=s
s=(f/"000_before_rrl_stock_store_return_rec_cmd.sql").read_text(encoding="utf-8").replace(" procedure compile_command"," procedure assert_scope(p_pickup varchar2,p_actor varchar2);\n procedure compile_command",1)
i=s.index(" function actual_date")
scope=""" procedure assert_scope(p_pickup varchar2,p_actor varchar2)is n number;
 begin
  select count(*)into n from RRL_STORE_RETURN_PICKUP p join RRL_STORE_RETURN_HANDOVER h on h.OPERATION_ID=p.HANDOVER_OPERATION_ID join RRL_STORE_RETURN_TRANSPORT t on t.OPERATION_ID=h.TRANSPORT_OPERATION_ID join RUSERS u on u.ID=p_actor
   where p.OPERATION_ID=p_pickup and nvl(u.DELETED,0)=0 and RRL_HAS_WRIGHT(p_actor,'warehouse_return_receive')=1 and(u.WARE_ID=t.RECEIVING_WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN');
  if n!=1 then raise_application_error(-20882,'STORE_RETURN_CURRENT_RECEIVING_WAREHOUSE_ACTOR_REQUIRED');end if;
 end;
"""
s=s[:i]+scope+s[i:]
s=s.replace("v_proof json_object_t;","v_proof json_object_t;return_proof clob;source_cell varchar2(60);source_max varchar2(60);",1)
s=s.replace(" if n!=0 then raise_application_error(-20886,'STORE_RETURN_MARKED_UNIT_REGULATORY_FLOW_REQUIRED');end if;", """ return_proof:=RRL_STORE_RETURN_UNIT_CORE.custody_proof(approved.OPERATION_ID,m);
 if n!=0 and return_proof is null then raise_application_error(-20886,'STORE_RETURN_MARKED_EXACT_APPROVAL_REQUIRED');end if;
 if return_proof is not null then
  select min(SOURCE_CELL),max(SOURCE_CELL)into source_cell,source_max from RRL_STORE_RETURN_UNIT where APPROVAL_OPERATION_ID=approved.OPERATION_ID;
  if source_cell is null or source_cell!=source_max then raise_application_error(-20886,'STORE_RETURN_UNIT_SOURCE_CELL_REQUIRED');end if;
 end if;""",1)
s=s.replace(" p_domain:=json_object_t();"," p_domain:=json_object_t();if return_proof is not null then p_domain.put('return_unit_proof',json_object_t.parse(return_proof));p_domain.put('return_source_cell',source_cell);end if;",1)
s=s.replace(" RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','PALLET:'", """ if v.has('return_unit_proof')then
  RRL_STOCK_PLAN_HELPER.stock_closure(f,r,v.get_string('original_lot_uid'),v.get_string('article'),v.get_string('return_source_cell'),null);
  declare wire clob:=v.get_object('return_unit_proof').get_array('units').to_clob;begin
   for x in(select K from json_table(wire,'$[*]'columns(K varchar2(64)path '$.key')))loop RRL_STOCK_PLAN_HELPER.anchor(r,60,'UNIT',x.K);end loop;
  end;
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STORE_RETURN_APPROVAL',v.get_string('approval_operation_id'));
 end if;
 RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','PALLET:'""",1)
s=s.replace(" RRL_STOCK_BALANCE_CORE.write_leg(v_uid,null,v_cell", """ if v.has('return_unit_proof')then
  RRL_STOCK_UNIT_CORE.receive_return(v_old_uid,v.get_string('return_source_cell'),v_uid,v_cell,v_qty,v.get_object('return_unit_proof').get_array('units').to_clob);
  j.put('physical_unit_count',v.get_object('return_unit_proof').get_number('physical_unit_count'));j.put('mark_scan_confirmed',true);j.put('original_unit_codes_retained',true);
 end if;
 RRL_STOCK_BALANCE_CORE.write_leg(v_uid,null,v_cell""",1)
out[str(f/"002_receiving.sql")]=s
s=(f/"000_before_rrl_stock_posting_api.sql").read_text(encoding="utf-8");needle="  if g_kind in('STORE_RETURN_HANDOVER'"
s=s.replace(needle,"  if g_kind='STORE_RETURN_RECEIVE'then declare doc json_object_t:=json_object_t.parse(p_request);begin RRL_STOCK_STORE_RETURN_REC_CMD.assert_scope(doc.get_object('source').get_string('pickup_operation_id'),p_actor);end;end if;\n"+needle);out[str(f/"003_root.sql")]=s
out[str(f/"rollback.sql")]="@@000_before_rrl_stock_posting_api.sql\n@@000_before_rrl_stock_store_return_rec_cmd.sql\n@@000_before_rrl_stock_unit_core.sql\n"
out["wiki/database/nicora_ni062_marked_receiving_design_20261011.md"]="# NI06.2: исходные маркированные единицы возвращаются на склад\n234: existing STORE_RETURN_RECEIVE document/parent/P/H/one movement/outbox retained. Exact approved subset/all current mandatory profiles/issued units/source version. UnitCore selected return method changes only CURRENT_UID/CELL/AVAILABLE/version; birth UID/physical key/code/qty retained. New and old STOCK50 plus selected UNIT60, same native transaction. Quarantine remains blocked receiving cell, no unit quarantine flag. Original ordinary REUSE boxes branch retained. Current receiving actor/WARE before cached replay/after locks.\n"
print(json.dumps(out,ensure_ascii=True))
