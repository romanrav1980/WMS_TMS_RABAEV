-- Run only after direct grant preflight. Dormant metadata; no stock or release activation.
declare n number;
begin
 select count(*) into n from RRL_STOCK_RELEASE where RELEASE_ID=1 and STATE='PREPARED';
 if n!=1 then raise_application_error(-20808,'INSTALL_REQUIRES_PREPARED'); end if;
 select count(*) into n from RRL_STOCK_OPERATION;
 if n!=0 then raise_application_error(-20808,'INSTALL_REQUIRES_NO_OPERATIONS'); end if;
 select count(*) into n from user_tab_columns where TABLE_NAME='RRL_STOCK_OPERATION' and COLUMN_NAME='RESOLVED_PLAN_JSON';
 if n=0 then execute immediate 'alter table RRL_STOCK_OPERATION add(RESOLVED_PLAN_JSON clob constraint RRL_STOCK_OPERATION_PLAN_CK check(RESOLVED_PLAN_JSON is json))'; end if;
end;
/
