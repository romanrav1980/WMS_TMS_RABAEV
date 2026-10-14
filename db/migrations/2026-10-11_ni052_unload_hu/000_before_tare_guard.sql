create or replace trigger RRL_HU_TARE_LINK_GUARD before insert or update on RRL_WMS_HU_LINK for each row
declare n number;book RRL_TARE_BOOK%rowtype;op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');
 command_kind varchar2(80);command_state varchar2(20);request clob;plan clob;d json_object_t;m json_object_t;domain_json json_object_t;book_id varchar2(100);
begin
 if :new.ACTIVE_FLAG!=1 then return;end if;
 if updating and :old.ACTIVE_FLAG=1 and :old.PARENT_UID=:new.PARENT_UID and nvl(:old.CHILD_PALLET_UID,'~')=nvl(:new.CHILD_PALLET_UID,'~') and nvl(:old.CHILD_CASE_TASK_ID,-1)=nvl(:new.CHILD_CASE_TASK_ID,-1)then return;end if;
 select count(*)into n from RRL_TARE_BOOK where STATUS='HELD'and((PLACE_KIND='HU'and PLACE_ID=:new.CHILD_PALLET_UID)or(PLACE_KIND='CASE'and PLACE_ID=to_char(:new.CHILD_CASE_TASK_ID,'TM9')));
 if n=0 then return;end if;
 if n!=1 or :new.CHILD_CASE_TASK_ID is null or op is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)then raise_application_error(-20886,'TARE_BOOKED_CHILD_REPACK_PROOF_REQUIRED');end if;
 select COMMAND_TYPE,STATE,CANONICAL_REQUEST,RESOLVED_PLAN_JSON into command_kind,command_state,request,plan from RRL_STOCK_OPERATION where OPERATION_ID=op;
 if command_kind not in('HU_ATTACH','HU_REPACK_SLOT')or command_state!='IN_FLIGHT'then raise_application_error(-20886,'TARE_BOOKED_CHILD_REPACK_PROOF_REQUIRED');end if;
 d:=json_object_t.parse(request);m:=d.get_object('metadata');domain_json:=json_object_t.parse(plan).get_object('domain');
 if d.get_object('source').get_string('uid')!=:new.PARENT_UID or m.get_number('child_case_task_id')!=:new.CHILD_CASE_TASK_ID or m.get_string('retained_tare_booking_operation_id')is null
  or domain_json.get_string('retained_tare_booking_operation_id')is null or domain_json.get_string('retained_tare_booking_operation_id')!=m.get_string('retained_tare_booking_operation_id')then raise_application_error(-20886,'NESTED_TARE_DECLARED_PROOF_REQUIRED');end if;
 book_id:=m.get_string('retained_tare_booking_operation_id');
 select *into book from RRL_TARE_BOOK where OPERATION_ID=book_id and STATUS='HELD'and PLACE_KIND='CASE'and PLACE_ID=to_char(:new.CHILD_CASE_TASK_ID,'TM9');
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_TARE_BOOK',book.OPERATION_ID));
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_TARE_BALANCE',rawtohex(book.BALANCE_KEY)));
 if book.OWNER_WARE_ID!=domain_json.get_object('parent_snapshot').get_number('warehouse')then raise_application_error(-20886,'NESTED_TARE_WARE_CONFLICT');end if;
exception when no_data_found then raise_application_error(-20886,'NESTED_TARE_ACTIVE_BOOK_REQUIRED');
end;
/
