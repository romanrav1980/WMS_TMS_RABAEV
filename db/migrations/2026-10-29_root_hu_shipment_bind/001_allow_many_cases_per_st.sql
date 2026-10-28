-- A root HU may contain several CASE children assigned to the same ST.
-- Each CASE remains linked to no more than one ST through its nullable column.
declare
  v_count number;
begin
  select count(*) into v_count
    from user_constraints
   where table_name='RRL_CASE_PICK_TASK'
     and constraint_name='RRL_CASE_SHIPMENT_UK';
  if v_count=1 then
    execute immediate 'alter table RRL_CASE_PICK_TASK drop constraint RRL_CASE_SHIPMENT_UK';
  end if;

  select count(*) into v_count
    from user_indexes
   where table_name='RRL_CASE_PICK_TASK'
     and index_name='RRL_CASE_SHIPMENT_IX';
  if v_count=0 then
    execute immediate 'create index RRL_CASE_SHIPMENT_IX on RRL_CASE_PICK_TASK(LEGACY_SBORKA_PALLET_ID)';
  end if;
end;
/
