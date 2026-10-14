create or replace trigger RRL_TARE_OFFER_CANCEL_GUARD before insert or update or delete on RRL_TARE_OFFER_CANCEL for each row
declare wire clob;v json_object_t;
begin
 if not inserting then raise_application_error(-20863,'TARE_OFFER_CANCEL_IMMUTABLE');end if;
 if :new.OPERATION_ID!=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')then raise_application_error(-20863,'TARE_OFFER_CANCEL_ROOT_REQUIRED');end if;
 RRL_TARE_ASSERT_WRITE('RRL_TARE_OFFER_CANCEL',:new.OPERATION_ID,'TARE_OFFER_CANCEL');
 select RESOLVED_PLAN_JSON into wire from RRL_STOCK_OPERATION where OPERATION_ID=:new.OPERATION_ID;v:=json_object_t.parse(wire).get_object('domain');
 if v.get_string('offer_operation_id')!=:new.OFFER_OPERATION_ID or v.get_string('reason')!=:new.REASON or :new.CANCELLED_BY!=sys_context('RRL_STOCK_WRITE_CTX','ACTOR')then raise_application_error(-20863,'TARE_OFFER_CANCEL_EXACT_PLAN_REQUIRED');end if;
end;
/
