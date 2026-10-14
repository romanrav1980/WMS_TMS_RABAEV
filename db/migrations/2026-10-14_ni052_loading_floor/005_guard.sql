create or replace trigger RRL_LOAD_FLOOR_FACT_GUARD
 before insert or update or delete on RRL_TT_LOAD_FLOOR_FACT for each row
begin
 if not inserting then raise_application_error(-20863,'LOAD_FLOOR_HISTORY_IMMUTABLE');end if;
 RRL_STOCK_LOAD_FLOOR.assert_writing(:new.LOAD_OPERATION_ID);
end;
/
