create or replace package RRL_STOCK_MES_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_TASK_CORE,package RRL_STOCK_TASK_DOMAIN) as
 procedure sync_warehouse_fact(p_task RRL_WAREHOUSE_TASK%rowtype,p_qty number,p_target_uid varchar2,p_residual number,p_actor varchar2);
end;
/
create or replace package body RRL_STOCK_MES_CORE as
 procedure sync_warehouse_fact(p_task RRL_WAREHOUSE_TASK%rowtype,p_qty number,p_target_uid varchar2,p_residual number,p_actor varchar2) is
  v_raw RRL_MES_RAW_TRANSFER_TASK%rowtype;v_movement RRL_MES_MOVEMENT%rowtype;
  v_n number;v_done number;v_id number;v_plan clob;v_domain json_object_t;
 begin
  select RESOLVED_PLAN_JSON into v_plan from RRL_STOCK_OPERATION
   where OPERATION_ID=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');
  v_domain:=json_object_t.parse(v_plan).get_object('domain');
  if p_task.TASK_SOURCE='MES_RAW_SUPPLY' then
   RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_MES_RAW_TRANSFER_TASK',
    RRL_STOCK_PLAN_HELPER.decimal_text(p_task.SOURCE_TASK_ID)));
   select * into v_raw from RRL_MES_RAW_TRANSFER_TASK where TASK_ID=p_task.SOURCE_TASK_ID for update;
   if v_raw.TASK_STATUS='CANCELLED' or v_raw.PRODUCTION_ORDER_ID!=nvl(p_task.PRODUCTION_ORDER_ID,p_task.SOURCE_DOC_ID)
    then raise_application_error(-20886,'MES_TASK_SOURCE_CONFLICT');end if;
   select nvl(sum(case when STATUS='DONE' then nvl(FACT_QTY,QTY) else 0 end),0),
    sum(case when STATUS not in('DONE','CANCELLED') then 1 else 0 end)
    into v_done,v_n from RRL_WAREHOUSE_TASK where TASK_SOURCE='MES_RAW_SUPPLY' and SOURCE_TASK_ID=p_task.SOURCE_TASK_ID;
   if v_done>v_raw.TASK_QTY then raise_application_error(-20886,'MES_DELIVERY_EXCEEDS_TASK');end if;
   v_id:=v_domain.get_number('new_movement_id');
   RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_MES_MOVEMENT',RRL_STOCK_PLAN_HELPER.decimal_text(v_id)));
   insert into RRL_MES_MOVEMENT(MOVEMENT_ID,MOVEMENT_TYPE,PRODUCTION_ORDER_ID,BOM_ID,BOM_LINE_ID,
    RAW_BATCH_ID,RAW_ARTICUL,UID_PALLET,QUANTITY,UNIT_CODE,SOURCE_LOCATION,TARGET_LOCATION,STATUS,
    WMS_APPLIED_AT,WMS_APPLIED_BY,CREATED_AT,CREATED_BY,UPDATED_AT,UPDATED_BY,PAYLOAD_JSON)
    values(v_id,'RAW_ISSUE_TO_PRODUCTION',v_raw.PRODUCTION_ORDER_ID,v_raw.BOM_ID,v_raw.BOM_LINE_ID,
     v_raw.RAW_BATCH_ID,v_raw.RAW_ARTICUL,p_target_uid,p_qty,p_task.UNIT_CODE,p_task.FROM_CELL,p_task.TO_CELL,
     'APPLIED_TO_WMS',sysdate,p_actor,sysdate,p_actor,sysdate,p_actor,v_plan);
   update RRL_MES_RAW_TRANSFER_TASK set TASK_STATUS=case when nvl(v_n,0)=0 then 'DONE' else 'IN_PROGRESS' end,
    FACT_QTY=v_done,FINISHED_AT=case when nvl(v_n,0)=0 then sysdate else FINISHED_AT end,LAST_ERROR=null
    where TASK_ID=p_task.SOURCE_TASK_ID;
  elsif p_task.TASK_SOURCE='MES_COMPLETION' then
   RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_MES_MOVEMENT',RRL_STOCK_PLAN_HELPER.decimal_text(p_task.SOURCE_MOVEMENT_ID)));
   select * into v_movement from RRL_MES_MOVEMENT where MOVEMENT_ID=p_task.SOURCE_MOVEMENT_ID for update;
   if v_movement.MOVEMENT_TYPE!='FG_PALLET_RELEASE' or v_movement.STATUS='CANCELLED'
    or v_movement.UID_PALLET!=nvl(p_task.UID_PALLET,p_task.SSCC) then raise_application_error(-20886,'MES_FINISHED_GOODS_CONFLICT');end if;
   update RRL_MES_MOVEMENT set STATUS='APPLIED_TO_WMS',TARGET_LOCATION=p_task.TO_CELL,
    WMS_APPLIED_AT=nvl(WMS_APPLIED_AT,sysdate),WMS_APPLIED_BY=nvl(WMS_APPLIED_BY,p_actor),
    UPDATED_AT=sysdate,UPDATED_BY=p_actor,LAST_ERROR=null where MOVEMENT_ID=p_task.SOURCE_MOVEMENT_ID;
  else raise_application_error(-20888,'MES_TASK_DOMAIN_REQUIRED');end if;
 end;
end;
/
