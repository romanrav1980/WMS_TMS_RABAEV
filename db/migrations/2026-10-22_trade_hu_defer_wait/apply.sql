whenever sqlerror exit failure rollback
declare s clob;begin
 if user<>'RABAEV'or sys_context('USERENV','SERVICE_NAME')<>'orcl'then raise_application_error(-20999,'WRONG_TARGET');end if;
 dbms_lob.createtemporary(s,true);for r in(select TEXT from USER_SOURCE where NAME='RRL_TRADE_STOCK_GUARD'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
 if rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>'531E9D26FC5D99428E6D21C7646A13E94A8ACDDA38E54AD69A3B8DDCB02964F0'then raise_application_error(-20999,'GUARD_SOURCE_DRIFT');end if;dbms_lob.freetemporary(s);
 dbms_lob.createtemporary(s,true);for r in(select TEXT from USER_SOURCE where NAME='RRL_ST_DEFER_HU_WAIT'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
 if rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>'97CC5206AE69B5F114F3F70233ACA00D16E0CBCFA50FA8010EFF96C65999BEF1'then raise_application_error(-20999,'ACCESS_SOURCE_DRIFT');end if;dbms_lob.freetemporary(s);
end;
/
@@after_access.sql
@@after_guard.sql
begin dbms_utility.compile_schema(user,false);end;
/
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-22-trade-hu-defer-wait' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set STATUS='APPLIED',APPLIED_AT=sysdate,APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(x.MIGRATION_ID,'Allow exact registered deferred HU case tree with trade order bindings',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
