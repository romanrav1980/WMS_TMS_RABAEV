create or replace trigger RRL_PRIHOD_RETURN_SOURCE_GUARD before insert or delete or update of ID,WARE_ID,NAKLAD_NUMBER,ZAKAZ_NUMBER,POSTAVSHIK_NAME,DOCUMENT_KIND,RETURN_APPROVAL_OPERATION_ID,RETURN_DOCUMENT_REFERENCE on RRL_PRIHOD_NAKLAD for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');v_kind varchar2(80);v_state varchar2(20);v_approval varchar2(100);v_doc number;
begin
 if inserting and :new.DOCUMENT_KIND='LEGACY_RECEIPT' and :new.RETURN_APPROVAL_OPERATION_ID is null and :new.RETURN_DOCUMENT_REFERENCE is null then return;end if;
 if updating and :old.DOCUMENT_KIND='LEGACY_RECEIPT' and :new.DOCUMENT_KIND='LEGACY_RECEIPT' and :new.RETURN_APPROVAL_OPERATION_ID is null and :new.RETURN_DOCUMENT_REFERENCE is null then return;end if;
 if deleting and :old.DOCUMENT_KIND='LEGACY_RECEIPT' then return;end if;
 if not inserting then raise_application_error(-20863,'STORE_RETURN_DOCUMENT_SOURCE_IMMUTABLE');end if;
 if op is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'STORE_RETURN_DOCUMENT_ROOT_REQUIRED');end if;
 select COMMAND_TYPE,STATE,json_value(RESOLVED_PLAN_JSON,'$.domain.approval_operation_id'),json_value(RESOLVED_PLAN_JSON,'$.domain.naklad_id' returning number) into v_kind,v_state,v_approval,v_doc from RRL_STOCK_OPERATION where OPERATION_ID=op;
 if v_kind!='STORE_RETURN_RECEIVE' or v_state!='IN_FLIGHT' or v_approval!=:new.RETURN_APPROVAL_OPERATION_ID or v_doc!=:new.ID or :new.DOCUMENT_KIND!='STORE_RETURN' then raise_application_error(-20863,'STORE_RETURN_DOCUMENT_ROOT_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_PRIHOD_NAKLAD',RRL_STOCK_PLAN_HELPER.decimal_text(v_doc)));
end;
/
