create or replace trigger RRL_TRAN_COST_CLAIM_GUARD before insert or update or delete on RRL_TRANSPORT_COST_CLAIM for each row
begin
 if not inserting then raise_application_error(-20863,'TRANSPORT_COST_CLAIM_IMMUTABLE');end if;
 RRL_TRANSPORT_COST_API.assert_writing;
end;
/
create or replace trigger RRL_TRAN_COST_DETAIL_GUARD before insert or update or delete on RRL_TRANSPORT_COST_DETAIL for each row
begin
 if not inserting then raise_application_error(-20863,'TRANSPORT_COST_DETAIL_IMMUTABLE');end if;
 RRL_TRANSPORT_COST_API.assert_writing;
end;
/
