set define off
set sqlblanklines on

prompt TRIGGER RRL_COMPL_RESERVE_TGR

  CREATE OR REPLACE EDITIONABLE TRIGGER "RABAEV"."RRL_COMPL_RESERVE_TGR" 
BEFORE INSERT
ON RABAEV.RRL_COMPL_RESERVE 
REFERENCING NEW AS New OLD AS Old
FOR EACH ROW
BEGIN
  -- your code here 
  -- (Trigger template "Default" could not be loaded.)     
  if :New.ID is null then 
     
     select RRL_COMPL_RESERVE_SQ.NEXTVAL into  :New.ID from dual;    
  
  end if;                        
  
END; 
/
ALTER TRIGGER "RABAEV"."RRL_COMPL_RESERVE_TGR" ENABLE;

prompt TRIGGER RRL_CROSS_DOCKING_ZONES_TRG

  CREATE OR REPLACE EDITIONABLE TRIGGER "RABAEV"."RRL_CROSS_DOCKING_ZONES_TRG" 
BEFORE INSERT
ON RABAEV.RRL_CROSS_DOCKING_ZONES 
REFERENCING NEW AS New OLD AS Old
FOR EACH ROW
BEGIN
  -- your code here 
  -- (Trigger template "Default" could not be loaded.)      

if :New.ID is null then
  select RRL_CROSS_DOCKING_ZONES_SQ.NEXTVAL into  :New.ID from dual;
end if;

END;

/
ALTER TRIGGER "RABAEV"."RRL_CROSS_DOCKING_ZONES_TRG" ENABLE;

prompt TRIGGER RRL_LOGIN_HISTORY_TRG

  CREATE OR REPLACE EDITIONABLE TRIGGER "RABAEV"."RRL_LOGIN_HISTORY_TRG" 
before insert on RABAEV.RRL_LOGIN_HISTORY
for each row
begin
  if :new.id is null then
    select RABAEV.RRL_LOGIN_HISTORY_SQ.nextval into :new.id from dual;
  end if;
end;
/
ALTER TRIGGER "RABAEV"."RRL_LOGIN_HISTORY_TRG" ENABLE;

prompt TRIGGER RRL_OBJECT_TRG

  CREATE OR REPLACE EDITIONABLE TRIGGER "RABAEV"."RRL_OBJECT_TRG" 
BEFORE UPDATE
ON RABAEV.RRL_OBJECT 
REFERENCING NEW AS NEW OLD AS OLD
FOR EACH ROW
BEGIN
  -- your code here 
  -- (Trigger template "Default" could not be loaded.)            
  if( :New.parent_object = :new.object_name ) then 
       
   RAISE_APPLICATION_ERROR(-21000 , 'РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…');
  end if;
  
END;

/
ALTER TRIGGER "RABAEV"."RRL_OBJECT_TRG" ENABLE;

prompt TRIGGER RRL_ORDER_PALLET_ROWS_TRG

  CREATE OR REPLACE EDITIONABLE TRIGGER "RABAEV"."RRL_ORDER_PALLET_ROWS_TRG" 
BEFORE INSERT
ON RABAEV.RRL_ORDER_PALLET_ROWS 
REFERENCING NEW AS New OLD AS Old
FOR EACH ROW
BEGIN
  -- your code here 
  -- (Trigger template "Default" could not be loaded.)      

  if :New.ID is null then
  select RRL_ORDER_PALLET_ROWS_SQ.NEXTVAL into  :New.ID from dual;
end if;

END;

/
ALTER TRIGGER "RABAEV"."RRL_ORDER_PALLET_ROWS_TRG" ENABLE;

prompt TRIGGER RRL_ORDER_ROWS_TRG

  CREATE OR REPLACE EDITIONABLE TRIGGER "RABAEV"."RRL_ORDER_ROWS_TRG" 
before insert on RRL_ORDER_ROWS
for each row
begin
  if :new.ID is null then
    select RRL_ORDER_ROWS_SQ.nextval into :new.ID from dual;
  end if;
end;

/
ALTER TRIGGER "RABAEV"."RRL_ORDER_ROWS_TRG" ENABLE;

prompt TRIGGER RRL_ORDERS_DELETE

  CREATE OR REPLACE EDITIONABLE TRIGGER "RABAEV"."RRL_ORDERS_DELETE" 
BEFORE DELETE
ON RABAEV.RRL_ORDERS 
REFERENCING NEW AS NEW OLD AS OLD
FOR EACH ROW
BEGIN


delete from  RABAEV.RRL_ORDER_ROWS where ORDER_ID=  :Old.ID;
delete from  RABAEV.RRL_ORDER_PALLET_ROWS   where ORDER_ID=  :Old.ID;


  -- your code here 
  -- (Trigger template "Default" could not be loaded.) 
END;

/
ALTER TRIGGER "RABAEV"."RRL_ORDERS_DELETE" ENABLE;

prompt TRIGGER RRL_ORDERS_TRG

  CREATE OR REPLACE EDITIONABLE TRIGGER "RABAEV"."RRL_ORDERS_TRG" 
BEFORE INSERT
ON RABAEV.RRL_ORDERS 
REFERENCING NEW AS New OLD AS Old
FOR EACH ROW
BEGIN
  -- your code here 
  -- (Trigger template "Default" could not be loaded.)       
if :New.ID is null then
  select RRL_ORDERS_SQ.NEXTVAL into  :New.ID from dual;
end if;

END;

/
ALTER TRIGGER "RABAEV"."RRL_ORDERS_TRG" ENABLE;

prompt TRIGGER RRL_REMAIN_SNAPSHOT_ROWS_TRG

  CREATE OR REPLACE EDITIONABLE TRIGGER "RABAEV"."RRL_REMAIN_SNAPSHOT_ROWS_TRG" 
      before insert on RRL_REMAIN_SNAPSHOT_ROWS
      for each row
      begin
        if :new.ID is null then
          select RRL_REMAIN_SNAPSHOT_ROWS_SQ.nextval into :new.ID from dual;
        end if;
      end;
    
/
ALTER TRIGGER "RABAEV"."RRL_REMAIN_SNAPSHOT_ROWS_TRG" ENABLE;

prompt TRIGGER RRL_REVISION_ROW_TRG

  CREATE OR REPLACE EDITIONABLE TRIGGER "RABAEV"."RRL_REVISION_ROW_TRG" 
BEFORE INSERT
ON RABAEV.RRL_REVISION_ROW 
REFERENCING NEW AS New OLD AS Old
FOR EACH ROW
BEGIN
  -- your code here 
  -- (Trigger template "Default" could not be loaded.)      


  if :New.ID is null then
  select RRL_REVISION_ROW_SQ.NEXTVAL into  :New.ID from dual;
end if;

END;

/
ALTER TRIGGER "RABAEV"."RRL_REVISION_ROW_TRG" ENABLE;

prompt TRIGGER RRL_REVIZION_TRG

  CREATE OR REPLACE EDITIONABLE TRIGGER "RABAEV"."RRL_REVIZION_TRG" 
BEFORE INSERT
ON RABAEV.RRL_REVIZION 
REFERENCING NEW AS New OLD AS Old
FOR EACH ROW
BEGIN
  -- your code here 
  -- (Trigger template "Default" could not be loaded.)      

if :New.ID is null then
  select RRL_REVISION_SQ.NEXTVAL into  :New.ID from dual;
end if;

END;

/
ALTER TRIGGER "RABAEV"."RRL_REVIZION_TRG" ENABLE;

prompt TRIGGER RRL_SUMMARY_PICK_LIST_DELETE

  CREATE OR REPLACE EDITIONABLE TRIGGER "RABAEV"."RRL_SUMMARY_PICK_LIST_DELETE" 
BEFORE DELETE
ON RABAEV.RRL_SUMMARY_PICK_LIST 
REFERENCING NEW AS New OLD AS Old
FOR EACH ROW
/* Formatted on 2011/06/21 17:54 (Formatter Plus v4.8.8) */
BEGIN
   -- your code here
   -- (Trigger template "Default" could not be loaded.)
   UPDATE rrl_sborka_pallets ppp
      SET ppp.summary_task_id = NULL
    WHERE summary_task_id = :OLD.ID;

   DELETE FROM rabaev.rrl_summary_pick_list_rows rws
         WHERE rws.spl_id = :OLD.ID;

   DELETE FROM rabaev.rrl_wt
         WHERE parent_id = :OLD.ID;
END;

/
ALTER TRIGGER "RABAEV"."RRL_SUMMARY_PICK_LIST_DELETE" ENABLE;

prompt TRIGGER RRL_SUMMARY_PICK_LIST_ROWS_TRG

  CREATE OR REPLACE EDITIONABLE TRIGGER "RABAEV"."RRL_SUMMARY_PICK_LIST_ROWS_TRG" 
BEFORE INSERT
ON RABAEV.RRL_SUMMARY_PICK_LIST_ROWS 
REFERENCING NEW AS New OLD AS Old
FOR EACH ROW
BEGIN
  -- your code here 
  -- (Trigger template "Default" could not be loaded.)           

  if :New.ID is null then
  select RRL_SUMMARY_PICK_LIST_ROWS_SQ.NEXTVAL into  :New.ID from dual;
end if;

END;

/
ALTER TRIGGER "RABAEV"."RRL_SUMMARY_PICK_LIST_ROWS_TRG" ENABLE;

