whenever sqlerror exit failure rollback
-- The downgrade is safe only when no ST has more than one CASE child.
declare
  v_duplicates number;
  v_index number;
  v_constraint number;
begin
  select count(*) into v_duplicates from (
    select LEGACY_SBORKA_PALLET_ID
      from RRL_CASE_PICK_TASK
     where LEGACY_SBORKA_PALLET_ID is not null
     group by LEGACY_SBORKA_PALLET_ID
    having count(*)>1
  );
  if v_duplicates<>0 then
    raise_application_error(-20991,'ROOT_HU_SHIPMENT_BIND_ROLLBACK_REFUSED_BOUND_MULTI_CASES');
  end if;
  select count(*) into v_constraint from user_constraints where table_name='RRL_CASE_PICK_TASK' and constraint_name='RRL_CASE_SHIPMENT_UK';
  if v_constraint=0 then
    select count(*) into v_index from user_indexes where table_name='RRL_CASE_PICK_TASK' and index_name='RRL_CASE_SHIPMENT_IX';
    if v_index=1 then execute immediate 'drop index RRL_CASE_SHIPMENT_IX'; end if;
    execute immediate 'alter table RRL_CASE_PICK_TASK add constraint RRL_CASE_SHIPMENT_UK unique (LEGACY_SBORKA_PALLET_ID)';
  end if;
end;
/
@@verify.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK',APPLIED_AT=sysdate,APPLIED_BY=user where MIGRATION_ID='2026-10-29-root-hu-shipment-bind';
commit;
