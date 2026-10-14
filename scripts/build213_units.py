from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni052_unload_units");out={}
out["wiki/database/retailcase_ni052_unload_units_design_20261011.md"]="""# NI05.2: возврат тех же единиц при выгрузке
Ticket213 extends212/NS45 source dispatch unload before vehicle reassignment. No new database family, transaction owner unchanged. Private existing UNIT owner receives restore_issued: same original frozen leaf set reconstructed from retained issued units at UID/cell. Canonical key/quantity/base-UOM hash must equal original physical_before signature and sum equal original journal quantity. Current issued status/null HARD/current unit versions captured; sorted UNIT60 locks declared before execution. Under locks recheck original fingerprint/current versions; restore AVAILABLE/new original-owner HARD, increment versions, keep identities and immutable codes. Missing original proof, changed composition, moved/reused unit, duplicate key/quantity mismatch refuses atomically. Ordinary empty set remains supported; marking now enabled requires original captured set. No government state reversal inferred: predeparture only/no accepted tare custody, original sender legal facts stay history and existing marking QC gates reapply. P/H/units/CASE/FF/load/outbox one native TX. Fresh checkpoints, inverse only without recovery history, otherwise forward repair.
"""
s=(f/"000_before_unit.sql").read_text(encoding="utf-8")
s=s.replace("accessible by(","accessible by(package RRL_STOCK_UNLOAD_CMD,",1)
sig=" procedure restore_issued(p_uid varchar2,p_cell varchar2,p_new_reservation number,p_qty number,p_units clob);"
s=s.replace(" function automatic_units",sig+"\n function automatic_units",1)
body=""" procedure restore_issued(p_uid varchar2,p_cell varchar2,p_new_reservation number,p_qty number,p_units clob)is
  op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');n number;v_count number;v_sum number;v_expected number;v_distinct number;locked_version number;
 begin
  require_context;
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_uid));
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(p_new_reservation)));
  select count(*)into n from RRL_STOCK_OPERATION o join json_table(o.RESOLVED_PLAN_JSON,'$.domain.legs[*]'columns(UID_TEXT varchar2(150)path '$.uid',CELL_TEXT varchar2(60)path '$.cell',NEW_RES number path '$.new_reservation',QTY_TEXT varchar2(60)path '$.quantity',UNITS clob format json path '$.restored_units'))leg
   on leg.UID_TEXT=p_uid and leg.CELL_TEXT=p_cell and leg.NEW_RES=p_new_reservation and leg.QTY_TEXT=RRL_STOCK_PLAN_HELPER.decimal_text(p_qty) and dbms_lob.compare(leg.UNITS,p_units)=0
   where o.OPERATION_ID=op and o.COMMAND_TYPE='UNLOAD_SHIPMENT'and o.STATE='IN_FLIGHT';
  if n!=1 then raise_application_error(-20863,'UNLOAD_UNIT_RECOVERY_PLAN_REQUIRED');end if;
  select count(*),count(distinct K)into v_expected,v_distinct from json_table(p_units,'$[*]'columns(K varchar2(64)path '$.key'));
  if v_expected<1 or v_expected>10000 or v_expected!=v_distinct then raise_application_error(-20884,'UNLOAD_UNIT_SET_REQUIRED');end if;
  v_count:=0;v_sum:=0;
  for u in(select u.PHYSICAL_UNIT_KEY,u.BASE_QTY,u.BASE_UOM,u.STOCK_STATUS,u.HARD_RESERVATION_ID,u.UNIT_VERSION,j.V,j.Q,j.UOM
   from RRL_WMS_RECEIPT_UNIT u join json_table(p_units,'$[*]'columns(K varchar2(64)path '$.key',V number path '$.version',Q varchar2(60)path '$.quantity',UOM varchar2(20)path '$.base_uom'))j on j.K=u.PHYSICAL_UNIT_KEY
   where u.CURRENT_UID=p_uid and u.CURRENT_CELL=p_cell order by u.PHYSICAL_UNIT_KEY)loop
   own_unit(u.PHYSICAL_UNIT_KEY);
   select UNIT_VERSION into locked_version from RRL_WMS_RECEIPT_UNIT where PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY for update;
   if locked_version!=u.UNIT_VERSION then raise_application_error(-20890,'CLOSURE_CHANGED: unload unit physical row');end if;
   if u.STOCK_STATUS!='ISSUED'or u.HARD_RESERVATION_ID is not null or u.UNIT_VERSION!=u.V or u.BASE_QTY!=RRL_STOCK_MATH.quantity(u.Q)or u.BASE_UOM!=u.UOM then raise_application_error(-20890,'CLOSURE_CHANGED: unload exact issued unit');end if;
   v_count:=v_count+1;v_sum:=v_sum+u.BASE_QTY;
  end loop;
  if v_count!=v_expected or v_sum!=p_qty then raise_application_error(-20884,'UNLOAD_UNIT_QUANTITY_CONFLICT');end if;
  RRL_STOCK_CTX_API.begin_effect('UNIT',p_uid,p_cell);
  update RRL_WMS_RECEIPT_UNIT u set STOCK_STATUS='AVAILABLE',HARD_RESERVATION_ID=p_new_reservation,UNIT_VERSION=UNIT_VERSION+1
   where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and exists(select 1 from json_table(p_units,'$[*]'columns(K varchar2(64)path '$.key'))j where j.K=u.PHYSICAL_UNIT_KEY);
  if sql%rowcount!=v_expected then raise_application_error(-20890,'CLOSURE_CHANGED: unload unit count');end if;
  RRL_STOCK_CTX_API.end_effect;assert_composition(p_uid,p_cell);
 exception when others then RRL_STOCK_CTX_API.end_effect;raise;
 end;
"""
idx=s.rfind("end;\n/");assert idx>0;s=s[:idx]+body+s[idx:];out[str(f/"001_unit.sql")]=s
s=(f/"000_before_unload.sql").read_text(encoding="utf-8")
helper=""" function issued_units(p_load varchar2,p_uid varchar2,p_cell varchar2,p_qty number)return clob is
  wire clob;expected_sig varchar2(64);sig varchar2(64);a json_array_t:=json_array_t();plain json_array_t:=json_array_t();x json_object_t;j json_object_t:=json_object_t();n number:=0;total number:=0;original_count number;
 begin
  select RESOLVED_PLAN_JSON into wire from RRL_STOCK_OPERATION where OPERATION_ID=p_load;
  select count(*),max(S)into original_count,expected_sig from json_table(wire,'$.physical_before[*]'columns(U varchar2(150)path '$.uid',S varchar2(64)path '$.unit_signature'))where U=p_uid;
  if original_count!=1 or expected_sig is null then raise_application_error(-20884,'UNLOAD_ORIGINAL_UNIT_PROOF_REQUIRED');end if;
  for u in(select PHYSICAL_UNIT_KEY,BASE_QTY,BASE_UOM,UNIT_VERSION,STOCK_STATUS,HARD_RESERVATION_ID from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=p_uid and CURRENT_CELL=p_cell order by PHYSICAL_UNIT_KEY fetch first 10001 rows only)loop
   n:=n+1;if n>10000 or u.PHYSICAL_UNIT_KEY is null or u.BASE_QTY<=0 or u.BASE_UOM is null or u.UNIT_VERSION is null or u.STOCK_STATUS!='ISSUED'or u.HARD_RESERVATION_ID is not null then raise_application_error(-20884,'UNLOAD_EXACT_ORIGINAL_ISSUED_SET_REQUIRED');end if;
   x:=json_object_t();x.put('key',u.PHYSICAL_UNIT_KEY);x.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(u.BASE_QTY));x.put('base_uom',u.BASE_UOM);plain.append(x.clone());x.put('version',u.UNIT_VERSION);a.append(x);total:=total+u.BASE_QTY;
  end loop;
  j.put('units',plain);sig:=rawtohex(sys.dbms_crypto.hash(j.to_clob,sys.dbms_crypto.hash_sh256));
  if sig!=expected_sig or(n>0 and total!=p_qty)then raise_application_error(-20884,'UNLOAD_ORIGINAL_UNIT_FINGERPRINT_CONFLICT');end if;
  if n=0 then
   select count(*)into n from RRL_PALLETS p where p.UID_PALLET=p_uid and(exists(select 1 from RRL_SKU_RECEIPT_POLICY sp where sp.ARTICUL=p.ARTICUL and(sp.MARKING_REQUIRED=1 or sp.SERIALIZED_WEIGHT_BOXES=1))or exists(select 1 from RRL_SKU_RECEIPT_PROFILE profile where profile.ARTICUL=p.ARTICUL)or exists(select 1 from RRL_FINISHED_GOODS_SKU fg where fg.ARTICUL=p.ARTICUL and fg.CRPT_REQUIRED=1));
   if n>0 then raise_application_error(-20884,'UNLOAD_ORIGINAL_MARKED_CAPTURE_REQUIRED');end if;
  end if;
  return a.to_clob;
 end;
"""
s=s.replace(" procedure source_state",helper+" procedure source_state",1)
s=s.replace("case_id number;\n begin","case_id number;unit_wire clob;unit_array json_array_t;unit_obj json_object_t;\n begin",1)
start=s.index("   select count(*)into n from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=uid_text;")
end=s.index("   select nvl(sum(BASE_QTY),0)into signed_total",start)
s=s[:start]+"""   unit_wire:=issued_units(load_id,uid_text,cell_text,qty);unit_array:=json_array_t.parse(unit_wire);
   if unit_array.get_size>0 then
    for unit_index in 0..unit_array.get_size-1 loop
     unit_obj:=treat(unit_array.get(unit_index)as json_object_t);RRL_STOCK_PLAN_HELPER.anchor(r,60,'UNIT',unit_obj.get_string('key'));
    end loop;
   end if;
"""+s[end:]
s=s.replace("y:=x.clone();y.put('new_reservation',new_res);","y:=x.clone();y.put('restored_units',unit_array);y.put('new_reservation',new_res);",1)
s=s.replace("uom_text varchar2(20);j json_object_t", "uom_text varchar2(20);unit_wire clob;fresh_units clob;j json_object_t",1)
s=s.replace("   RRL_STOCK_BALANCE_CORE.apply_delta(uid_text,cell_text,qty,0,uom_text,uom_version,version_no);","""   unit_wire:=x.get_array('restored_units').to_clob;fresh_units:=issued_units(load_id,uid_text,cell_text,qty);
   if dbms_lob.compare(unit_wire,fresh_units)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: unload original units');end if;
   RRL_STOCK_BALANCE_CORE.apply_delta(uid_text,cell_text,qty,0,uom_text,uom_version,version_no);""",1)
s=s.replace("   RRL_STOCK_RESERVE_CORE.restore_consumed(history.RESERVATION_ID,new_id,qty,uom_version,p_actor);","""   RRL_STOCK_RESERVE_CORE.restore_consumed(history.RESERVATION_ID,new_id,qty,uom_version,p_actor);
   if x.get_array('restored_units').get_size>0 then RRL_STOCK_UNIT_CORE.restore_issued(uid_text,cell_text,new_id,qty,unit_wire);end if;""",1)
out[str(f/"002_unload.sql")]=s
out[str(f/"apply.sql")]="@@001_unit.sql\n@@002_unload.sql\n"
out[str(f/"rollback.sql")]="""declare n number;begin
 select count(*)into n from RRL_TT_UNLOAD_FACT u join RRL_STOCK_OPERATION o on o.OPERATION_ID=u.OPERATION_ID where json_exists(o.RESOLVED_PLAN_JSON,'$.domain.legs[*].restored_units[*]');
 if n>0 then raise_application_error(-20863,'UNLOAD_UNIT_HISTORY_RETAIN_FORWARD_REPAIR');end if;
end;
/
@@000_before_unload.sql
@@000_before_unit.sql
"""
print(json.dumps(out,ensure_ascii=True))

