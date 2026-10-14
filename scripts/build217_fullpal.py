from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni052_unload_fullpal");out={}
out["wiki/database/nicora_ni052_unload_fullpal_design_20261011.md"]="""# NI05.2: исходная FULLPAL выгружается через прежнее исполнение
217 extends same UNLOAD_SHIPMENT with original bound FULLPAL member, standalone STOCK root or stock leaves in whole CASE/FULLPAL matryoshka. No new binding/allocator/task executor. Original archived bound UID/current shipped fulfillment/actual completed picking-move task/current original wave required; original whole UID P/H zero across all cells and current article/UOM unchanged. Original signed negative journal and exact units restored as before. Existing FF owner projects current PICKED stock version after restored balance while original task/DONE and shipment history remain. All FF/task/wave/ST/HU/stock/resources declared before effects. Fresh control required; existing reload/assignment reused. Original transferred FULLPAL tare remains explicitly unsupported until its own recovery extension. Forward repair with actual unload history; old original root fact retained.
"""
s=(f/"000_before_fulfillment.sql").read_text(encoding="utf-8")
s=s.replace(" procedure project_unload(p_shipment number,p_load varchar2,p_case number,p_actor varchar2);"," procedure project_unload(p_shipment number,p_load varchar2,p_case number,p_actor varchar2);\n procedure project_unload_pallet(p_shipment number,p_load varchar2,p_uid varchar2,p_actor varchar2);",1)
body=""" procedure project_unload_pallet(p_shipment number,p_load varchar2,p_uid varchar2,p_actor varchar2)is n number:=0;version_no number;
 begin
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_uid));
  select STOCK_VERSION into version_no from RRL_REMAINS where UID_POLETA=p_uid and REMAIN>0 and HARD_RESERVED_BASE=REMAIN;
  for ff in(select FULFILLMENT_ID from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=p_shipment and PICKED_CASE_TASK_ID is null and PICKED_PALLET_UID=p_uid and PICKED_WAREHOUSE_TASK_ID is not null and STATUS='SHIPPED'and SHIPPED_OPERATION_ID=p_load order by FULFILLMENT_ID for update)loop
   n:=n+1;RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_CUSTOMER_ORDER_FULFILLMENT',RRL_STOCK_PLAN_HELPER.decimal_text(ff.FULFILLMENT_ID)));
   update RRL_CUSTOMER_ORDER_FULFILLMENT set STATUS='PICKED',SHIPPED_OPERATION_ID=null,SHIPPED_AT=null,PICKED_STOCK_VERSION=version_no,UPDATED_AT=sysdate,UPDATED_BY=p_actor where FULFILLMENT_ID=ff.FULFILLMENT_ID;
  end loop;
  if n!=1 then raise_application_error(-20886,'UNLOAD_ORIGINAL_FULLPAL_FULFILLMENT_REQUIRED');end if;
 end;
"""
idx=s.rfind("end;\n/");assert idx>0;s=s[:idx]+body+s[idx:];out[str(f/"001_fulfillment.sql")]=s
s=(f/"000_before_unload.sql").read_text(encoding="utf-8")
s=s.replace("expected_link_version number;","expected_link_version number;sid number;physical_uid varchar2(150);wave_value number;full_task number;physical_total number;held_total number;",1)
s=s.replace("root_node.get_string('kind')='CASE'then plans.append(original.get_object('shipment'));","root_node.get_string('kind')='CASE'then plans.append(original.get_object('shipment'));\n  elsif kind_name='LOAD_SHIPMENT'and p_lf.ROOT_CASE_TASK_ID is null and p_lf.ROOT_UID is not null and root_node.get_string('kind')='STOCK'then plans.append(original.get_object('shipment'));",1)
s=s.replace("or sub.get_number('case_task')is null then","then",1)
start=s.index("   case_value:=sub.get_number('case_task');")
end=s.index("   a:=sub.get_array('legs');",start)
existing=s[start:end]
existing=existing.replace("members.append(x);","x.put_null('physical_uid');members.append(x);")
full="""   else
    physical_uid:=sub.get_string('bound_physical_uid');sid:=sub.get_number('document_id');
    if physical_uid is null or sub.get_number('bound_stock_version')is null then raise_application_error(-20886,'UNLOAD_ORIGINAL_BOUND_FULLPAL_REQUIRED');end if;
    select nvl(sum(REMAIN),0),nvl(sum(HARD_RESERVED_BASE),0)into physical_total,held_total from RRL_REMAINS where UID_POLETA=physical_uid;
    if physical_total!=0 or held_total!=0 then raise_application_error(-20886,'UNLOAD_WHOLE_ORIGINAL_FULLPAL_NOT_EMPTY');end if;
    select count(*),max(PICKED_WAREHOUSE_TASK_ID)into n,full_task from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=sid and STATUS='SHIPPED'and SHIPPED_OPERATION_ID=p_load and PICKED_CASE_TASK_ID is null and PICKED_PALLET_UID=physical_uid;
    if n!=1 or full_task is null then raise_application_error(-20886,'UNLOAD_ORIGINAL_FULLPAL_FULFILLMENT_REQUIRED');end if;
    select count(*)into n from RRL_WAREHOUSE_TASK where TASK_ID=full_task and STATUS='DONE'and TASK_TYPE='PICKING_MOVE'and UID_PALLET=physical_uid and TO_WARE_ID=p_lf.WARE_ID;
    if n!=1 then raise_application_error(-20886,'UNLOAD_ORIGINAL_FULLPAL_COMPLETED_TASK_REQUIRED');end if;
    a:=sub.get_array('legs');
    if a.get_size!=1 then raise_application_error(-20886,'UNLOAD_WHOLE_SINGLE_FULLPAL_LEAF_REQUIRED');end if;
    y:=treat(a.get(0)as json_object_t);wave_value:=y.get_number('owner_id');
    if y.get_string('uid')!=physical_uid or y.get_string('owner_type')!='PICK_WAVE'then raise_application_error(-20886,'UNLOAD_ORIGINAL_FULLPAL_WAVE_OWNER_REQUIRED');end if;
    select count(*)into n from RRL_PICK_WAVE where PICK_WAVE_ID=wave_value and STATUS='LAUNCHED';
    if n!=1 then raise_application_error(-20886,'UNLOAD_ACTIVE_FULLPAL_WAVE_REQUIRED');end if;
    select count(*)into n from RRL_TT_HU_LOAD_ST where LOAD_OPERATION_ID=p_load and ACTIVE_FLAG=1 and SBORKA_PALLET_ID=sid;
    if n!=1 then raise_application_error(-20886,'UNLOAD_ORIGINAL_ACTIVE_ST_REQUIRED');end if;
    x:=json_object_t();x.put_null('case_id');x.put('shipment_id',sid);x.put_null('case_version');x.put('physical_uid',physical_uid);x.put('wave_id',wave_value);x.put('fullpal_task_id',full_task);members.append(x);
   end if;
"""
s=s[:start]+"   if sub.get_number('case_task')is not null then\n"+existing+full+s[end:]
s=s.replace("new_link number;target_slot number;","new_link number;physical_uid varchar2(150);full_task number;wave_value number;actual_article varchar2(160);actual_uom varchar2(20);target_slot number;",1)
s=s.replace("case_id:=x.get_number('case_id');\n   RRL_STOCK_PLAN_HELPER","case_id:=x.get_number('case_id');physical_uid:=x.get_string('physical_uid');\n   RRL_STOCK_PLAN_HELPER",1)
s=s.replace("   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CASE_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(case_id));","""   if case_id is not null then
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CASE_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(case_id));
    select PICK_WAVE_ID into wave_value from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=case_id;
   else
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(x.get_number('fullpal_task_id')));
    wave_value:=x.get_number('wave_id');
   end if;
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE',RRL_STOCK_PLAN_HELPER.decimal_text(wave_value));""",1)
s=s.replace("select FULFILLMENT_ID,CUSTOMER_ORDER_ID,PICKED_CASE_TASK_ID from RRL_CUSTOMER_ORDER_FULFILLMENT","select FULFILLMENT_ID,CUSTOMER_ORDER_ID,PICKED_CASE_TASK_ID,PICKED_PALLET_UID from RRL_CUSTOMER_ORDER_FULFILLMENT",1)
s=s.replace("if n>1 or ff.PICKED_CASE_TASK_ID!=case_id then","if n>1 or nvl(ff.PICKED_CASE_TASK_ID,-1)!=nvl(case_id,-1)or(case_id is null and ff.PICKED_PALLET_UID!=physical_uid)then",1)
anchor="   unit_wire:=issued_units(load_id,uid_text,cell_text,qty);"
idx=s.index(anchor)
insert="""   select p.ARTICUL,rem.BASE_UOM into actual_article,actual_uom from RRL_PALLETS p join RRL_REMAINS rem on rem.UID_POLETA=p.UID_PALLET where p.UID_PALLET=uid_text and rem.CELL=cell_text;
   if actual_article!=x.get_string('article')or actual_uom!=x.get_string('base_uom')then raise_application_error(-20886,'UNLOAD_ORIGINAL_ARTICLE_UOM_REQUIRED');end if;
"""
s=s[:idx]+insert+s[idx:]
s=s.replace("where CASE_PICK_TASK_ID=case_id;\n   RRL_STOCK_FULFILLMENT_FACT.project_unload","where CASE_PICK_TASK_ID=case_id;\n   RRL_STOCK_FULFILLMENT_FACT.project_unload",1)
start=s.index("   update RRL_CASE_PICK_TASK set STATUS='WAIT_CONTROL'")
end=s.index("   update RRL_SBORKA_PALLETS set CONDITION",start)
existing=s[start:end]
s=s[:start]+"   if case_id is not null then\n"+existing+"""   else
    RRL_STOCK_FULFILLMENT_FACT.project_unload_pallet(sid,load_id,x.get_string('physical_uid'),p_actor);
   end if;
"""+s[end:]
out[str(f/"002_unload.sql")]=s
out[str(f/"apply.sql")]="@@001_fulfillment.sql\n@@002_unload.sql\n"
out[str(f/"rollback.sql")]="""declare n number;begin
 select count(*)into n from RRL_TT_UNLOAD_FACT u join RRL_STOCK_OPERATION o on o.OPERATION_ID=u.OPERATION_ID where json_exists(o.RESOLVED_PLAN_JSON,'$.domain.members[*]?(@.physical_uid != null)');
 if n>0 then raise_application_error(-20863,'UNLOAD_FULLPAL_HISTORY_FORWARD_REPAIR_REQUIRED');end if;
end;
/
@@000_before_unload.sql
@@000_before_fulfillment.sql
"""
print(json.dumps(out,ensure_ascii=True))

