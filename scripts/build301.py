from pathlib import Path
import json,re
d=Path("db/migrations/2026-10-11_ni061_recovery_placement");out={}
def put(name,s):out[(d/name).as_posix()]=s
put("001_schema.sql","""declare n number;begin
 select count(*)into n from USER_TABLES where TABLE_NAME='RRL_IW_RECOVERY_PUT_PLAN';
 if n=0 then execute immediate 'create table RRL_IW_RECOVERY_PUT_PLAN(
 OPERATION_ID varchar2(100)primary key,RECOVERY_OPERATION_ID varchar2(100)not null references RRL_INTERWARE_RECOVERY_RECEIPT(OPERATION_ID),
 TASK_ID number not null unique references RRL_WAREHOUSE_TASK(TASK_ID),TARGET_CELL varchar2(60)not null,ACTOR varchar2(100)not null,
 TEMP_DECISION_OPERATION_ID varchar2(100),TASK_TEMP_MIN number,TASK_TEMP_MAX number,
 CREATED_AT timestamp with time zone default systimestamp not null)';end if;
 select count(*)into n from USER_TABLES where TABLE_NAME='RRL_IW_RECOVERY_PLACEMENT';
 if n=0 then execute immediate 'create table RRL_IW_RECOVERY_PLACEMENT(
 TASK_ID number primary key references RRL_IW_RECOVERY_PUT_PLAN(TASK_ID),
 RECOVERY_OPERATION_ID varchar2(100)not null unique references RRL_INTERWARE_RECOVERY_RECEIPT(OPERATION_ID),
 OPERATION_ID varchar2(100)not null unique,ROOT_UID varchar2(200)not null,WARE_ID number not null,
 TARGET_CELL varchar2(60)not null,BASE_QTY number not null check(BASE_QTY>0),BASE_UOM varchar2(20)not null,
 ACTOR varchar2(100)not null,CREATED_AT timestamp with time zone default systimestamp not null)';end if;
end;
/
""")
# Share the current ordinary put-away target checks, without changing their policy.
old=Path("db/migrations/2026-10-11_ni061_marked_partial/005_put_body.sql").read_text(encoding="utf-8")
start=old.index(" select LIMIT_WEIGHT,LIMIT_HEIGHT into v_capacity")
end=old.index(" select count(*)into n from RRL_INTERWARE_PLACEMENT",start)
cell_checks=old[start:end]
weight_start=old.index(" if nvl(v_capacity,0)>0 then")
weight_end=old.index(" p_domain:=json_object_t()",weight_start)
weight_checks=old[weight_start:weight_end]
for before,after in [
("receipt.WARE_ID","p_ware"),("receipt.RECEIVE_CELL","p_from"),("receipt.ROOT_UID","p_uid"),
("v_target","p_target"),("p_task","p_task_id"),("v_gross","p_gross")]:
 cell_checks=cell_checks.replace(before,after);weight_checks=weight_checks.replace(before,after)
put("002_put_cell.sql","""create or replace package RRL_STOCK_IW_PUT_CELL authid definer
 accessible by(package RRL_STOCK_INTERWARE_PUT,package RRL_STOCK_IW_RECOVERY_PUT)as
 procedure assert_target(p_ware number,p_uid varchar2,p_from varchar2,p_target varchar2,p_gross number,p_task_id number);
end;
/
create or replace package body RRL_STOCK_IW_PUT_CELL as
 procedure assert_target(p_ware number,p_uid varchar2,p_from varchar2,p_target varchar2,p_gross number,p_task_id number)is
 v_capacity number;v_height number;v_weight number;v_unknown number;n number;
 begin
"""+cell_checks+weight_checks+""" exception when no_data_found then raise_application_error(-20886,'INTERWARE_AVAILABLE_TARGET_CELL_REQUIRED');end;
end;
/
""")
old=old[:weight_start]+old[weight_end:]
old=old[:start]+old[end:]
needle=" p_domain:=json_object_t();"
old=old.replace(needle," RRL_STOCK_IW_PUT_CELL.assert_target(receipt.WARE_ID,receipt.ROOT_UID,receipt.RECEIVE_CELL,v_target,v_gross,p_task);\n"+needle,1)
put("003_original_put_body.sql",old)
spec=Path("db/migrations/2026-10-11_ni061_partial_receiving/000_before_rrl_stock_interware_put_spec.sql").read_text(encoding="utf-8")
put("004_recovery_put.sql",spec.replace("RRL_STOCK_INTERWARE_PUT","RRL_STOCK_IW_RECOVERY_PUT").replace(",p_superseded number default null","")+"""create or replace package body RRL_STOCK_IW_RECOVERY_PUT as
 procedure assert_scope(p_receipt varchar2,p_actor varchar2)is n number;begin
 select count(*)into n from RRL_INTERWARE_RECOVERY_RECEIPT r join RRL_STOCK_OPERATION o on o.OPERATION_ID=r.OPERATION_ID
 join RUSERS u on u.ID=p_actor where r.OPERATION_ID=p_receipt and o.STATE='APPLIED'and o.COMMAND_TYPE='INTERWARE_SHORTAGE_RECOVER'
 and nvl(u.DELETED,0)=0 and RRL_HAS_WRIGHT(u.ID,'interwarehouse_receive')=1
 and(u.WARE_ID=r.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN');
 if n!=1 then raise_application_error(-20882,'RECOVERY_PLACEMENT_ACTOR_REQUIRED');end if;end;
 procedure describe_current(p_receipt varchar2,p_actor varchar2,p_task number,p_domain out json_object_t)is
 r RRL_INTERWARE_RECOVERY_RECEIPT%rowtype;original_receipt RRL_INTERWARE_RECEIPT%rowtype;plan RRL_INTERWARE_PLAN%rowtype;
 target_cell varchar2(60);v_p number;v_h number;v_uom varchar2(20);v_version number;v_gross number;n number;unit_count number;unit_total number;
 unit_snapshot clob;thermal json_object_t;stored_lo number;stored_hi number;stored_decision varchar2(100);
 begin
 assert_scope(p_receipt,p_actor);
 select *into r from RRL_INTERWARE_RECOVERY_RECEIPT where OPERATION_ID=p_receipt;
 select receipt.*into original_receipt from RRL_INTERWARE_RECEIPT receipt join RRL_INTERWARE_SHORTAGE_REQUEST req on req.RECEIPT_OPERATION_ID=receipt.OPERATION_ID
 join RRL_INTERWARE_SHORTAGE_FACT fact on fact.REQUEST_OPERATION_ID=req.OPERATION_ID where fact.OPERATION_ID=r.LOSS_OPERATION_ID;
 select *into plan from RRL_INTERWARE_PLAN where OPERATION_ID=original_receipt.PLAN_OPERATION_ID;
 plan:=RRL_INTERWARE_ROUTING.resolved(plan);target_cell:=plan.OUTBOUND_DOCK;
 RRL_INTERWARE_THERMAL.assert_release(plan.OPERATION_ID);thermal:=json_object_t.parse(RRL_INTERWARE_THERMAL.mode_json(plan.OPERATION_ID));
 if p_task is not null then
 select TASK_TEMP_MIN,TASK_TEMP_MAX,TEMP_DECISION_OPERATION_ID into stored_lo,stored_hi,stored_decision from RRL_IW_RECOVERY_PUT_PLAN where TASK_ID=p_task;
 if nvl(stored_lo,-1000)!=nvl(thermal.get_number('task_temp_min'),-1000)or nvl(stored_hi,-1000)!=nvl(thermal.get_number('task_temp_max'),-1000)then raise_application_error(-20886,'RECOVERY_TEMPERATURE_REPLAN_REQUIRED');end if;
 thermal.put('task_decision_operation_id',stored_decision);
 end if;
 RRL_INTERWARE_THERMAL.assert_cell(thermal.to_clob,r.WARE_ID,target_cell);
 select count(*)into n from RRL_TT_DOCK where DOCK=target_cell and WARE_ID=r.WARE_ID and nvl(DOCK_IS_BLOCKED,0)=0;
 if n!=1 then raise_application_error(-20886,'RECOVERY_ORIGINAL_OUTBOUND_BUFFER_REQUIRED');end if;
 select count(*)into n from RRL_IW_RECOVERY_PLACEMENT where RECOVERY_OPERATION_ID=p_receipt;
 if n!=0 then raise_application_error(-20886,'RECOVERY_ALREADY_PLACED');end if;
 select count(*)into n from RRL_IW_RECOVERY_PUT_PLAN pp join RRL_WAREHOUSE_TASK t on t.TASK_ID=pp.TASK_ID
 where pp.RECOVERY_OPERATION_ID=p_receipt and t.STATUS!='CANCELLED'and(p_task is null or t.TASK_ID!=p_task);
 if n!=0 then raise_application_error(-20886,'RECOVERY_ACTIVE_PLACEMENT_EXISTS');end if;
 select REMAIN,HARD_RESERVED_BASE,BASE_UOM,STOCK_VERSION into v_p,v_h,v_uom,v_version from RRL_REMAINS where UID_POLETA=r.ROOT_UID and CELL=r.RECEIVE_CELL;
 if v_p!=r.BASE_QTY or v_h!=0 or v_uom!=r.BASE_UOM then raise_application_error(-20886,'RECOVERY_WHOLE_UNRESERVED_RECEIPT_REQUIRED');end if;
 select count(*)into n from RRL_REMAINS where UID_POLETA=r.ROOT_UID and CELL!=r.RECEIVE_CELL and(REMAIN!=0 or HARD_RESERVED_BASE!=0);
 if n!=0 then raise_application_error(-20886,'RECOVERY_MULTIPLE_STOCK_CELLS_DENIED');end if;
 select count(*)into unit_count from RRL_INTERWARE_RECOVERY_UNIT where RECOVERY_OPERATION_ID=p_receipt;
 select count(*)into n from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=r.ROOT_UID;
 if n!=unit_count or unit_count>10000 then raise_application_error(-20884,'RECOVERY_UNIT_COMPOSITION_CHANGED');end if;
 if unit_count>0 then
 select count(*),sum(u.BASE_QTY),json_arrayagg(json_object('key'value u.PHYSICAL_UNIT_KEY,'quantity'value RRL_STOCK_PLAN_HELPER.decimal_text(u.BASE_QTY),
 'base_uom'value u.BASE_UOM,'version'value u.UNIT_VERSION)order by u.PHYSICAL_UNIT_KEY returning clob)
 into n,unit_total,unit_snapshot from RRL_INTERWARE_RECOVERY_UNIT recovered join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=recovered.PHYSICAL_UNIT_KEY
 where recovered.RECOVERY_OPERATION_ID=p_receipt and u.CURRENT_UID=r.ROOT_UID and u.CURRENT_CELL=r.RECEIVE_CELL
 and u.STOCK_STATUS='AVAILABLE'and u.HARD_RESERVATION_ID is null and u.BASE_QTY=recovered.BASE_QTY and u.BASE_UOM=recovered.BASE_UOM and u.BASE_UOM=r.BASE_UOM;
 if n!=unit_count or unit_total!=r.BASE_QTY then raise_application_error(-20884,'RECOVERY_ORIGINAL_AVAILABLE_UNITS_REQUIRED');end if;
 else
 select count(*)into n from dual where exists(select 1 from RRL_SKU_RECEIPT_PROFILE where ARTICUL=r.ARTICLE)
 or exists(select 1 from RRL_SKU_RECEIPT_POLICY where ARTICUL=r.ARTICLE and MARKING_REQUIRED=1);
 if n>0 then raise_application_error(-20884,'RECOVERY_MARKED_UNITS_REQUIRED');end if;
 end if;
 select WEIGHT_BRUTTO into v_gross from RRL_PALLETS where UID_PALLET=r.ROOT_UID;
 RRL_STOCK_IW_PUT_CELL.assert_target(r.WARE_ID,r.ROOT_UID,r.RECEIVE_CELL,target_cell,v_gross,p_task);
 p_domain:=json_object_t();p_domain.put('temperature',thermal);
 if unit_snapshot is not null then p_domain.put('physical_units',json_array_t.parse(unit_snapshot));end if;
 p_domain.put('recovery_operation_id',p_receipt);p_domain.put('loss_operation_id',r.LOSS_OPERATION_ID);p_domain.put('plan_operation_id',plan.OPERATION_ID);
 p_domain.put('warehouse_id',r.WARE_ID);p_domain.put('uid',r.ROOT_UID);p_domain.put('article',r.ARTICLE);p_domain.put('from_cell',r.RECEIVE_CELL);
 p_domain.put('target_cell',target_cell);p_domain.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(r.BASE_QTY));p_domain.put('base_uom',r.BASE_UOM);p_domain.put('stock_version',v_version);
 exception when no_data_found then raise_application_error(-20886,'RECOVERY_PLACEMENT_SOURCE_REQUIRED');end;
 procedure declare_rows(v json_object_t,r in out nocopy json_array_t)is begin
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_INTERWARE_RECOVERY_RECEIPT',v.get_string('recovery_operation_id'));
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_INTERWARE_PLAN',v.get_string('plan_operation_id'));end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob)is
 d json_object_t:=json_object_t.parse(p_request);v json_object_t;f json_array_t:=json_array_t();r json_array_t:=json_array_t();task_id number;
 begin
 describe_current(d.get_object('source').get_string('recovery_operation_id'),d.get_string('actor'),null,v);
 select RRL_WAREHOUSE_TASK_SQ.nextval into task_id from dual;v.put('task_id',task_id);
 RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
 RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
 declare_rows(v,r);RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_IW_RECOVERY_PUT_PLAN',p_operation);
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(task_id));
 RRL_STOCK_PLAN_HELPER.stock_closure(f,r,v.get_string('uid'),v.get_string('article'),v.get_string('from_cell'),v.get_string('target_cell'));
 p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob)is
 d json_object_t:=json_object_t.parse(p_request);op varchar2(100):=d.get_string('operation_id');wire clob;v json_object_t;fresh json_object_t;j json_object_t:=json_object_t();
 task_id number;ware number;lot varchar2(200);sku varchar2(160);origin_cell varchar2(60);target_cell varchar2(60);uom varchar2(20);qty number;receipt_id varchar2(100);temp_id varchar2(100);lo number;hi number;
 begin
 select RESOLVED_PLAN_JSON into wire from RRL_STOCK_OPERATION where OPERATION_ID=op;v:=json_object_t.parse(wire).get_object('domain');task_id:=v.get_number('task_id');
 receipt_id:=v.get_string('recovery_operation_id');describe_current(receipt_id,p_actor,null,fresh);fresh.put('task_id',task_id);
 if dbms_lob.compare(v.to_clob,fresh.to_clob)!=0 then raise_application_error(-20886,'RECOVERY_PLACEMENT_PLAN_CHANGED');end if;
 ware:=v.get_number('warehouse_id');lot:=v.get_string('uid');sku:=v.get_string('article');origin_cell:=v.get_string('from_cell');target_cell:=v.get_string('target_cell');
 uom:=v.get_string('base_uom');qty:=RRL_STOCK_MATH.quantity(v.get_string('quantity'));
 insert into RRL_WAREHOUSE_TASK(TASK_ID,TASK_TYPE,TASK_SOURCE,SOURCE_TASK_ID,SOURCE_DOC_TYPE,SOURCE_DOC_ID,UID_PALLET,TARGET_ARTICUL,FROM_CELL,TO_CELL,FROM_WARE_ID,TO_WARE_ID,QTY,UNIT_CODE,QTY_MODE,STATUS,CREATED_BY)
 values(task_id,'PUTAWAY','MANUAL',task_id,'RECOVERY',task_id,lot,sku,origin_cell,target_cell,ware,ware,qty,uom,'PALLET','PLANNED',p_actor);
 temp_id:=v.get_object('temperature').get_string('decision_operation_id');lo:=v.get_object('temperature').get_number('task_temp_min');hi:=v.get_object('temperature').get_number('task_temp_max');
 insert into RRL_IW_RECOVERY_PUT_PLAN(OPERATION_ID,RECOVERY_OPERATION_ID,TASK_ID,TARGET_CELL,ACTOR,TEMP_DECISION_OPERATION_ID,TASK_TEMP_MIN,TASK_TEMP_MAX)
 values(op,receipt_id,task_id,target_cell,p_actor,temp_id,lo,hi);
 j.put('operation_id',op);j.put('task_id',task_id);j.put('recovery_operation_id',receipt_id);j.put('from_cell',origin_cell);j.put('to_cell',target_cell);
 j.put('quantity',v.get_string('quantity'));j.put('base_uom',uom);j.put('stock_changed',false);p_result:=j.to_clob;end;
 procedure plan_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_actor varchar2,p_resources in out nocopy json_array_t,p_domain in out nocopy json_object_t)is
 receipt_id varchar2(100);target_cell varchar2(60);v json_object_t;begin
 select RECOVERY_OPERATION_ID,TARGET_CELL into receipt_id,target_cell from RRL_IW_RECOVERY_PUT_PLAN where TASK_ID=p_task.TASK_ID;
 describe_current(receipt_id,p_actor,p_task.TASK_ID,v);
 if p_task.TASK_SOURCE!='MANUAL'or p_task.TASK_TYPE!='PUTAWAY'or p_task.SOURCE_DOC_TYPE!='RECOVERY'or p_task.SOURCE_DOC_ID!=p_task.TASK_ID
 or p_task.UID_PALLET!=v.get_string('uid')or p_task.FROM_CELL!=v.get_string('from_cell')or p_task.TO_CELL!=v.get_string('target_cell')
 or p_task.UNIT_CODE!=v.get_string('base_uom')or p_task.QTY!=RRL_STOCK_MATH.quantity(v.get_string('quantity'))or p_task.QTY_MODE!='PALLET'or target_cell!=p_task.TO_CELL
 then raise_application_error(-20886,'RECOVERY_ORIGINAL_TASK_REQUIRED');end if;
 declare_rows(v,p_resources);RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_IW_RECOVERY_PLACEMENT',RRL_STOCK_PLAN_HELPER.decimal_text(p_task.TASK_ID));
 p_domain.put('recovery_placement',v);end;
 procedure validate_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_actor varchar2,p_frozen json_object_t)is
 resources json_array_t:=json_array_t();domain json_object_t:=json_object_t();begin
 plan_task(p_task,p_actor,resources,domain);
 if dbms_lob.compare(p_frozen.to_clob,domain.get_object('recovery_placement').to_clob)!=0 then raise_application_error(-20886,'RECOVERY_TASK_SOURCE_CHANGED');end if;end;
 procedure complete_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_quantity number,p_target_uid varchar2,p_actor varchar2)is
 r RRL_INTERWARE_RECOVERY_RECEIPT%rowtype;receipt_id varchar2(100);op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');begin
 select RECOVERY_OPERATION_ID into receipt_id from RRL_IW_RECOVERY_PUT_PLAN where TASK_ID=p_task.TASK_ID;
 select *into r from RRL_INTERWARE_RECOVERY_RECEIPT where OPERATION_ID=receipt_id;
 if p_quantity!=r.BASE_QTY or p_target_uid!=r.ROOT_UID then raise_application_error(-20886,'RECOVERY_WHOLE_PLACEMENT_REQUIRED');end if;
 insert into RRL_IW_RECOVERY_PLACEMENT(TASK_ID,RECOVERY_OPERATION_ID,OPERATION_ID,ROOT_UID,WARE_ID,TARGET_CELL,BASE_QTY,BASE_UOM,ACTOR)
 values(p_task.TASK_ID,receipt_id,op,r.ROOT_UID,r.WARE_ID,p_task.TO_CELL,r.BASE_QTY,r.BASE_UOM,p_actor);end;
end;
/
""")
for name,body in [("plan","005_task_plan.sql"),("core","006_task_core.sql"),("domain","007_task_domain.sql")]:
 s=(d/("000_before_rrl_stock_task_"+name+".sql")).read_text(encoding="utf-8")
 if name=="plan":
  needle="  if v_task.TASK_SOURCE='MANUAL' and v_task.SOURCE_DOC_TYPE='INTERWARE' then RRL_STOCK_INTERWARE_PUT.plan_task"
  pos=s.index(needle);s=s[:pos]+"  if v_task.TASK_SOURCE='MANUAL'and v_task.SOURCE_DOC_TYPE='RECOVERY'then RRL_STOCK_IW_RECOVERY_PUT.plan_task(v_task,v_doc.get_string('actor'),v_r,v_domain);end if;\n"+s[pos:]
 elif name=="core":
  needle="  if v_task.TASK_SOURCE='MANUAL' and v_task.SOURCE_DOC_TYPE='INTERWARE' then RRL_STOCK_INTERWARE_PUT.validate_task"
  pos=s.index(needle);s=s[:pos]+"  if v_task.TASK_SOURCE='MANUAL'and v_task.SOURCE_DOC_TYPE='RECOVERY'then RRL_STOCK_IW_RECOVERY_PUT.validate_task(v_task,p_actor,v_domain.get_object('recovery_placement'));end if;\n"+s[pos:]
  needle="  elsif v_task.TASK_SOURCE='MANUAL' and v_task.SOURCE_DOC_TYPE='INTERWARE' then"
  s=s.replace(needle,"  elsif v_task.TASK_SOURCE='MANUAL'and v_task.SOURCE_DOC_TYPE='RECOVERY'then\n   if v_qty!=v_original or v_target!=v_pallet.UID_PALLET then raise_application_error(-20886,'RECOVERY_WHOLE_PLACEMENT_REQUIRED');end if;\n"+needle,1)
  s=s.replace("SOURCE_DOC_TYPE='INTERWARE' then 'PUTAWAY'","SOURCE_DOC_TYPE in('INTERWARE','RECOVERY') then 'PUTAWAY'",1)
 else:
  s=s.replace("  elsif p_task.TASK_SOURCE='MANUAL' and p_task.SOURCE_DOC_TYPE='STORE_RETURN' then","  elsif p_task.TASK_SOURCE='MANUAL'and p_task.SOURCE_DOC_TYPE='RECOVERY'then\n   RRL_STOCK_IW_RECOVERY_PUT.complete_task(p_task,p_qty,p_target_uid,p_actor);\n  elsif p_task.TASK_SOURCE='MANUAL' and p_task.SOURCE_DOC_TYPE='STORE_RETURN' then",1)
 put(body,s)
root=Path("db/migrations/2026-10-11_ni061_loss_recovery/019_receiving_root_body.sql").read_text(encoding="utf-8")
needle="  if g_kind='INTERWARE_SHORTAGE_RECOVER'then declare req "
assert root.count(needle)==2
root=root.replace(needle,"  if g_kind='INTERWARE_RECOVERY_PUTAWAY_PLAN'then declare req json_object_t:=json_object_t.parse(p_request);begin RRL_STOCK_IW_RECOVERY_PUT.assert_scope(req.get_object('source').get_string('recovery_operation_id'),p_actor);end;end if;\n"+needle)
root=root.replace("   if g_kind='INTERWARE_SHORTAGE_RECOVER'then","   if g_kind='INTERWARE_RECOVERY_PUTAWAY_PLAN'then RRL_STOCK_IW_RECOVERY_PUT.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);\n   elsif g_kind='INTERWARE_SHORTAGE_RECOVER'then",1)
root=root.replace("  elsif g_kind='INTERWARE_SHORTAGE_RECOVER'then RRL_STOCK_IW_RECOVERY_REC.execute_command","  elsif g_kind='INTERWARE_RECOVERY_PUTAWAY_PLAN'then RRL_STOCK_IW_RECOVERY_PUT.execute_command(g_request,g_actor,p_result);\n  elsif g_kind='INTERWARE_SHORTAGE_RECOVER'then RRL_STOCK_IW_RECOVERY_REC.execute_command",1)
put("008_root_body.sql",root)
put("009_guards.sql","""create or replace trigger RRL_IW_RECOVERY_PUT_GUARD before insert or update or delete on RRL_IW_RECOVERY_PUT_PLAN for each row
begin
 if updating or deleting then raise_application_error(-20878,'RECOVERY_PUT_PLAN_IMMUTABLE');end if;
 RRL_IW_SHORTAGE_GUARD.require_command(:new.OPERATION_ID,'INTERWARE_RECOVERY_PUTAWAY_PLAN');
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_IW_RECOVERY_PUT_PLAN',:new.OPERATION_ID));
end;
/
create or replace trigger RRL_IW_RECOVERY_PLACE_GUARD before insert or update or delete on RRL_IW_RECOVERY_PLACEMENT for each row
begin
 if updating or deleting then raise_application_error(-20878,'RECOVERY_PLACEMENT_IMMUTABLE');end if;
 RRL_IW_SHORTAGE_GUARD.require_command(:new.OPERATION_ID,'TASK_COMPLETE');
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_IW_RECOVERY_PLACEMENT',RRL_STOCK_PLAN_HELPER.decimal_text(:new.TASK_ID)));
end;
/
""")
p=Path("api/wms_api_server/app/modules/inventory/contracts_stock.py");s=p.read_text(encoding="utf-8").replace('{"INTERWARE_SHORTAGE_RECOVER",','{"INTERWARE_RECOVERY_PUTAWAY_PLAN","INTERWARE_SHORTAGE_RECOVER",',1);out[p.as_posix()]=s
put("apply.sql","".join("@@"+n+"\n"for n in ["001_schema.sql","002_put_cell.sql","003_original_put_body.sql","004_recovery_put.sql","005_task_plan.sql","006_task_core.sql","007_task_domain.sql","008_root_body.sql","009_guards.sql"])+"@@../2026-10-08_stock_posting_core/014b_recompile.sql\n")
put("rollback.sql","""declare n number;begin select count(*)into n from RRL_IW_RECOVERY_PUT_PLAN;if n>0 then raise_application_error(-20878,'RETAINED_RECOVERY_TASKS_REQUIRE_FORWARD_FIX');end if;end;
/
@@000_before_rrl_stock_task_plan.sql
@@000_before_rrl_stock_task_core.sql
@@000_before_rrl_stock_task_domain.sql
@@../2026-10-11_ni061_marked_partial/005_put_body.sql
@@../2026-10-11_ni061_loss_recovery/019_receiving_root_body.sql
drop trigger RRL_IW_RECOVERY_PLACE_GUARD;
drop trigger RRL_IW_RECOVERY_PUT_GUARD;
drop package RRL_STOCK_IW_RECOVERY_PUT;
drop package RRL_STOCK_IW_PUT_CELL;
drop table RRL_IW_RECOVERY_PLACEMENT;
drop table RRL_IW_RECOVERY_PUT_PLAN;
@@../2026-10-08_stock_posting_core/014b_recompile.sql
""")
put("verify.sql","select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME in('RRL_STOCK_IW_RECOVERY_PUT','RRL_STOCK_IW_PUT_CELL','RRL_STOCK_TASK_PLAN','RRL_STOCK_TASK_CORE','RRL_STOCK_TASK_DOMAIN','RRL_STOCK_POSTING_API')order by NAME,LINE;\n")
print(json.dumps(out))
