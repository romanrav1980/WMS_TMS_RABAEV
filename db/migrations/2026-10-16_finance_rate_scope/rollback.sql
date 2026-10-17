declare a clob;begin
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_LOG_RATE_HISTORY_GUARD'and TYPE='TRIGGER'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='6BDF990CF60684868B8EF5903FD510DD2DA87B9D1DDA4CE7E74C81A537344BFE'then raise_application_error(-20886,'SOURCE_GUARD_RRL_LOG_RATE_HISTORY_GUARD');end if;dbms_lob.freetemporary(a);
end;
/
declare n number;begin
 if user!='RABAEV'or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl'then raise_application_error(-20886,'RATE_SCOPE_TARGET');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'RATE_SCOPE_INVALID');end if;
 select count(*)into n from USER_ERRORS where NAME not like 'BIN$%';if n!=0 then raise_application_error(-20886,'RATE_SCOPE_ERRORS');end if;
end;
/
@@restore_history_trigger.sql
@@before.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-16-finance-rate-scope';
commit;
