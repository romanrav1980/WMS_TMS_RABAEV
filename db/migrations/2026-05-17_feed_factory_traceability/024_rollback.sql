prompt [migration 2026-05-17-024] MES raw supply planning and transfer tasks - rollback

delete from RIGHTS
 where USER_GROUP = 'GLOBAL_ADMIN'
   and upper(RIGHT1) in (
     'MES_RAW_SUPPLY_VIEW',
     'MES_RAW_SUPPLY_CALCULATE',
     'MES_RAW_TRANSFER_CREATE',
     'MES_RAW_TRANSFER_CONFIRM',
     'MES_RAW_TRANSFER_CANCEL'
   );

delete from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-17-024-mes-raw-supply';

commit;

prompt RRL_MES_RAW_DEMAND, RRL_MES_RAW_SUPPLY_CANDIDATE, RRL_MES_RAW_SHORTAGE and RRL_MES_RAW_TRANSFER_TASK are intentionally preserved.
prompt Drop them only after explicit operator approval.
prompt [migration 2026-05-17-024] rollback done
