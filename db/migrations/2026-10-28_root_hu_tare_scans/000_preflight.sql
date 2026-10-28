whenever sqlerror exit failure rollback
declare n number;begin
 if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;
 select count(*) into n from user_objects where object_name='RRL_STOCK_TARE_BOOK_CMD' and object_type='PACKAGE BODY' and status<>'VALID';if n<>0 then raise_application_error(-20999,'PREEXISTING_INVALID_TARE_BOOK_COMMAND');end if;
 select count(*) into n from user_source where name='RRL_STOCK_TARE_BOOK_CMD' and type='PACKAGE BODY';if n=0 then raise_application_error(-20999,'TARE_BOOK_COMMAND_SOURCE_MISSING');end if;
end;
/
