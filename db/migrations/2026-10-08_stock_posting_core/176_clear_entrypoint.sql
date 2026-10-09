create or replace function RRL_CLEAR_OTBOR_CELL(CELL1 varchar2,user_id1 varchar2) return varchar2 authid definer is
begin
 if CELL1 is null or user_id1 is null or RRL_HAS_WRIGHT(user_id1,'stock_inventory_count')!=1 then
  raise_application_error(-20882,'INVENTORY_COUNT_FORBIDDEN');
 end if;
 raise_application_error(-20886,'INVENTORY_MEASURED_COUNT_REQUIRED: inventory-count.html; no automatic lot deletion');
end;
/
