whenever sqlerror exit failure rollback
declare
  v_constraint number;
  v_index number;
  v_bad number;
begin
  select count(*) into v_constraint from user_constraints where table_name='RRL_CASE_PICK_TASK' and constraint_name='RRL_CASE_SHIPMENT_UK';
  if v_constraint<>0 then raise_application_error(-20992,'ROOT_HU_SHIPMENT_BIND_UNIQUE_CONSTRAINT_STILL_PRESENT'); end if;
  select count(*) into v_index from user_indexes where table_name='RRL_CASE_PICK_TASK' and index_name='RRL_CASE_SHIPMENT_IX' and uniqueness='NONUNIQUE' and status='VALID';
  if v_index<>1 then raise_application_error(-20993,'ROOT_HU_SHIPMENT_BIND_LOOKUP_INDEX_MISSING'); end if;
  select count(*) into v_bad from user_constraints c join user_cons_columns cc on cc.constraint_name=c.constraint_name and cc.table_name=c.table_name
   where c.table_name='RRL_CASE_PICK_TASK' and cc.column_name='LEGACY_SBORKA_PALLET_ID' and c.constraint_type in('U','P');
  if v_bad<>0 then raise_application_error(-20994,'ROOT_HU_SHIPMENT_BIND_UNEXPECTED_UNIQUE_CONSTRAINT'); end if;
end;
/
