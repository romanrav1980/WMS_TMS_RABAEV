-- MIGRATION_ID:2026-10-11-181-sap-putaway-identity
-- Build replacement before dropping the old index; all non-SAP source keys unchanged.
create unique index RRL_WT_SOURCE_ID_I2 on RRL_WAREHOUSE_TASK
(TASK_SOURCE,nvl(SOURCE_TASK_ID,-1),nvl(SOURCE_MOVEMENT_ID,-1),TASK_TYPE,
 case when TASK_SOURCE='SAP_RECEIPT' then UID_PALLET else to_char(nvl(PARENT_TASK_ID,-1),'TM9','NLS_NUMERIC_CHARACTERS=''.,''')end);
drop index RRL_WAREHOUSE_TASK_U2;
alter index RRL_WT_SOURCE_ID_I2 rename to RRL_WAREHOUSE_TASK_U2;
