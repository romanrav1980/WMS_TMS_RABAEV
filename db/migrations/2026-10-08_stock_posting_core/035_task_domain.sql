create or replace package RRL_STOCK_TASK_DOMAIN authid definer
 accessible by(package RRL_STOCK_TASK_CORE) as
 procedure sync_fact(p_task RRL_WAREHOUSE_TASK%rowtype,p_qty number,p_target_uid varchar2,p_residual number,p_actor varchar2);
end;
/
create or replace package body RRL_STOCK_TASK_DOMAIN as
 procedure sync_fact(p_task RRL_WAREHOUSE_TASK%rowtype,p_qty number,p_target_uid varchar2,p_residual number,p_actor varchar2) is
  v_n number;v_status varchar2(40);v_pick number;
 begin
  if p_task.TASK_SOURCE='WAVE' then
   select count(*) into v_n from RRL_WAREHOUSE_TASK where TASK_SOURCE='WAVE' and TASK_TYPE=p_task.TASK_TYPE
    and SOURCE_TASK_ID=p_task.SOURCE_TASK_ID and STATUS not in('DONE','CANCELLED');
   v_status:=case when v_n=0 then 'DONE' else 'IN_PROGRESS' end;
   if p_task.TASK_TYPE='REPLENISHMENT' then
    update RRL_PICK_WAVE_REPLENISH_TASK set STATUS=v_status,UPDATED_AT=sysdate,UPDATED_BY=p_actor
     where PICK_WAVE_REPLENISH_TASK_ID=p_task.SOURCE_TASK_ID;
    -- HARD coverage is now at the target. Do not mark it CONSUMED by placement.
   elsif p_task.TASK_TYPE='PICKING_MOVE' then
    select PICK_TASK_ID into v_pick from RRL_PICK_WAVE_TASK where PICK_WAVE_TASK_ID=p_task.SOURCE_TASK_ID;
    update RRL_PICK_WAVE_TASK set STATUS=v_status,FACT_QTY=p_qty,
     DONE_AT=case when v_status='DONE' then sysdate else DONE_AT end,
     DONE_BY=case when v_status='DONE' then p_actor else DONE_BY end,
     TARGET_CELL_CODE=p_task.TO_CELL,UPDATED_AT=sysdate,UPDATED_BY=p_actor where PICK_WAVE_TASK_ID=p_task.SOURCE_TASK_ID;
    update RRL_PICK_TASK set STATUS=v_status,FACT_QTY=p_qty,
     DONE_AT=case when v_status='DONE' then sysdate else DONE_AT end,
     DONE_BY=case when v_status='DONE' then p_actor else DONE_BY end,
     TARGET_CELL_CODE=p_task.TO_CELL,UPDATED_AT=sysdate,UPDATED_BY=p_actor where PICK_TASK_ID=v_pick;
    -- Physical relocation preserves HARD until ISSUE/SHIP, even if the picking task is DONE.
   else raise_application_error(-20888,'WAVE_TASK_HANDLER_REQUIRED');end if;
  elsif p_task.TASK_SOURCE='SAP_RECEIPT' then
   update RRL_RECEIPT_SLOT_CLAIM set STATUS='OCCUPIED' where TASK_ID=p_task.TASK_ID and STATUS='RESERVED';
   select count(*) into v_n from RRL_WAREHOUSE_TASK where TASK_SOURCE='SAP_RECEIPT' and SOURCE_DOC_ID=p_task.SOURCE_DOC_ID and STATUS not in('DONE','CANCELLED');
   if v_n=0 then update RRL_PRIHOD_NAKLAD set CONDITION=2 where ID=p_task.SOURCE_DOC_ID and CONDITION=1;end if;
  elsif p_task.TASK_SOURCE in('MES_RAW_SUPPLY','MES_COMPLETION') then
   RRL_STOCK_MES_CORE.sync_warehouse_fact(p_task,p_qty,p_target_uid,p_residual,p_actor);
  else raise_application_error(-20888,'TASK_DOMAIN_HANDLER_REQUIRED');end if;
 end;
end;
/
