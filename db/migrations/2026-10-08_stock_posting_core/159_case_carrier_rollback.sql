declare n number;begin
 select count(*) into n from RRL_CASE_CARRIER_LOT;
 if n>0 then raise_application_error(-20808,'CASE_CARRIER_FACTS_PREVENT_SCHEMA_ROLLBACK');end if;
 select count(*) into n from RRL_STOCK_OPERATION;
 if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_SCHEMA_ROLLBACK');end if;
end;
/
drop trigger RRL_CASE_CARRIER_LOT_GUARD;
drop table RRL_CASE_CARRIER_LOT;
alter table RRL_CASE_PICK_TASK drop column CURRENT_CELL;
alter table RRL_CASE_PICK_TASK drop column CONTENT_VERSION;
