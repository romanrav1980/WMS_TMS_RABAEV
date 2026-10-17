create or replace trigger RRL_WTASK_ASSIGN_DERIVE after insert or update on RRL_WAREHOUSE_TASK for each row
 declare
 function changed(a varchar2,b varchar2)return boolean is begin return a!=b or(a is null and b is not null)or(a is not null and b is null);end;
 function changed_number(a number,b number)return boolean is begin return a!=b or(a is null and b is not null)or(a is not null and b is null);end;
 function changed_time(a timestamp with time zone,b timestamp with time zone)return boolean is begin return a!=b or(a is null and b is not null)or(a is not null and b is null);end;
 begin
 if inserting then RRL_WTASK_VERSION_API.derive(:new.TASK_ID,true);
 elsif changed(:old.TASK_TYPE,:new.TASK_TYPE)
 or changed(:old.TASK_SOURCE,:new.TASK_SOURCE)
 or changed(:old.SOURCE_DOC_TYPE,:new.SOURCE_DOC_TYPE)
 or changed(:old.RAW_ARTICUL,:new.RAW_ARTICUL)
 or changed(:old.TARGET_ARTICUL,:new.TARGET_ARTICUL)
 or changed(:old.UID_PALLET,:new.UID_PALLET)
 or changed(:old.SSCC,:new.SSCC)
 or changed(:old.FROM_CELL,:new.FROM_CELL)
 or changed(:old.TO_CELL,:new.TO_CELL)
 or changed(:old.UNIT_CODE,:new.UNIT_CODE)
 or changed(:old.STATUS,:new.STATUS)
 or changed(:old.ASSIGNED_TO,:new.ASSIGNED_TO)
 or changed(:old.QTY_MODE,:new.QTY_MODE)
 or changed(:old.TARGET_UID_PALLET,:new.TARGET_UID_PALLET)
 or changed(:old.STARTED_SHIFT_TIME_ZONE,:new.STARTED_SHIFT_TIME_ZONE)
 or changed_number(:old.TASK_ID,:new.TASK_ID)
 or changed_number(:old.SOURCE_TASK_ID,:new.SOURCE_TASK_ID)
 or changed_number(:old.SOURCE_MOVEMENT_ID,:new.SOURCE_MOVEMENT_ID)
 or changed_number(:old.SOURCE_DOC_ID,:new.SOURCE_DOC_ID)
 or changed_number(:old.PRODUCTION_ORDER_ID,:new.PRODUCTION_ORDER_ID)
 or changed_number(:old.PROD_BATCH_ID,:new.PROD_BATCH_ID)
 or changed_number(:old.FROM_WARE_ID,:new.FROM_WARE_ID)
 or changed_number(:old.TO_WARE_ID,:new.TO_WARE_ID)
 or changed_number(:old.QTY,:new.QTY)
 or changed_number(:old.FACT_QTY,:new.FACT_QTY)
 or changed_number(:old.PARENT_TASK_ID,:new.PARENT_TASK_ID)
 or changed_number(:old.RESOURCE_ID,:new.RESOURCE_ID)
 or changed_number(:old.RESOURCE_SESSION_ID,:new.RESOURCE_SESSION_ID)
 or changed_number(:old.EQUIPMENT_ID,:new.EQUIPMENT_ID)
 or changed_number(:old.FROM_CELL_SLOT_ID,:new.FROM_CELL_SLOT_ID)
 or changed_number(:old.TO_CELL_SLOT_ID,:new.TO_CELL_SLOT_ID)
 or changed_number(:old.HU_CONTENT_VERSION,:new.HU_CONTENT_VERSION)
 or changed_time(:old.STARTED_AT,:new.STARTED_AT)
 or changed_time(:old.STARTED_AT_INSTANT,:new.STARTED_AT_INSTANT)
 or changed_time(:old.FINISHED_AT,:new.FINISHED_AT)
 or changed_time(:old.FINISHED_AT_INSTANT,:new.FINISHED_AT_INSTANT)
 or changed_time(:old.CANCELLED_AT,:new.CANCELLED_AT) then RRL_WTASK_VERSION_API.derive(:new.TASK_ID,false);end if;
 end;
/
