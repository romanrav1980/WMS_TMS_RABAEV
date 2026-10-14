create or replace trigger RRL_TARE_LOAD_RECOVERY_GUARD before insert or update or delete on RRL_TARE_LOAD_RECOVERY for each row
declare wire clob;v json_object_t;n number;
begin
 if not inserting then raise_application_error(-20863,'TARE_LOAD_RECOVERY_IMMUTABLE');end if;
 if :new.OPERATION_ID!=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')then raise_application_error(-20863,'TARE_LOAD_RECOVERY_ROOT_REQUIRED');end if;
 RRL_TARE_ASSERT_WRITE('RRL_TARE_LOAD_RECOVERY',:new.OPERATION_ID,'TARE_BOOK');
 select RESOLVED_PLAN_JSON into wire from RRL_STOCK_OPERATION where OPERATION_ID=:new.OPERATION_ID;
 v:=json_object_t.parse(wire).get_object('domain').get_object('load_recovery');
 if v.get_string('load_operation_id')!=:new.LOAD_OPERATION_ID or v.get_string('original_booking_operation_id')!=:new.ORIGINAL_BOOK_OPERATION_ID or v.get_string('return_offer_operation_id')!=:new.RETURN_OFFER_OPERATION_ID or v.get_string('return_accept_operation_id')!=:new.RETURN_ACCEPT_OPERATION_ID or v.get_number('warehouse_id')!=:new.WARE_ID or v.get_number('pallet_type_id')!=:new.PALLET_TYPE_ID or nvl(v.get_number('case_id'),-1)!=nvl(:new.CASE_PICK_TASK_ID,-1) or nvl(v.get_string('root_uid'),'-')!=nvl(:new.ROOT_UID,'-') or :new.CREATED_BY!=sys_context('RRL_STOCK_WRITE_CTX','ACTOR')then raise_application_error(-20863,'TARE_LOAD_RECOVERY_EXACT_PLAN_REQUIRED');end if;
 select count(*)into n from RRL_TARE_BOOK where OPERATION_ID=:new.OPERATION_ID and STATUS='HELD'and((PLACE_KIND='CASE'and :new.CASE_PICK_TASK_ID is not null and PLACE_ID=RRL_STOCK_PLAN_HELPER.decimal_text(:new.CASE_PICK_TASK_ID))or(PLACE_KIND='HU'and :new.ROOT_UID is not null and PLACE_ID=:new.ROOT_UID))and OWNER_WARE_ID=:new.WARE_ID and PALLET_TYPE_ID=:new.PALLET_TYPE_ID;
 if n!=1 then raise_application_error(-20863,'TARE_LOAD_RECOVERY_NEW_BOOK_REQUIRED');end if;
end;
/
