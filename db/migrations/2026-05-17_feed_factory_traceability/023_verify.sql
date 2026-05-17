prompt [migration 2026-05-17-023] Common stock reservation model - verify

select table_name
  from user_tables
 where table_name = 'RRL_STOCK_RESERVATION';

select sequence_name
  from user_sequences
 where sequence_name = 'RRL_STOCK_RESERVATION_SQ';

select count(*) STOCK_RESERVATION_INDEX_COUNT
  from user_indexes
 where index_name in (
   'RRL_STOCK_RESERVATION_I1',
   'RRL_STOCK_RESERVATION_I2',
   'RRL_STOCK_RESERVATION_I3',
   'RRL_STOCK_RESERVATION_I4',
   'RRL_STOCK_RESERVATION_I5',
   'RRL_STOCK_RESERVATION_I6',
   'RRL_STOCK_RESERVATION_I7',
   'RRL_STOCK_RESERVATION_I8',
   'RRL_STOCK_RESERVATION_U1'
 );

select count(*) STOCK_RESERVATION_CONSTRAINT_COUNT
  from user_constraints
 where table_name = 'RRL_STOCK_RESERVATION'
   and constraint_name in (
     'RRL_STOCK_RESERVATION_PK',
     'RRL_STOCK_RES_KIND_CHK',
     'RRL_STOCK_RES_SCOPE_CHK',
     'RRL_STOCK_RES_STATUS_CHK',
     'RRL_STOCK_RES_DOMAIN_CHK',
     'RRL_STOCK_RES_QTY_CHK',
     'RRL_STOCK_RES_SOFT_CHK',
     'RRL_STOCK_RES_HARD_CHK'
   );

select count(*) STOCK_RESERVATION_RIGHT_COUNT
  from RIGHTS
 where USER_GROUP = 'GLOBAL_ADMIN'
   and upper(RIGHT1) in ('STOCK_RESERVATION_VIEW', 'STOCK_RESERVATION_EDIT');

select count(*) STOCK_RESERVATION_MIGRATION_COUNT
  from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-17-023-common-stock-reservation';

select count(*) INVALID_CNT
  from user_objects
 where status <> 'VALID'
   and object_type in ('PACKAGE', 'PACKAGE BODY', 'PROCEDURE', 'FUNCTION', 'TRIGGER', 'VIEW');

prompt [migration 2026-05-17-023] verify done
