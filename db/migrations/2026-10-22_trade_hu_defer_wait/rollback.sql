whenever sqlerror exit failure rollback
declare s clob;begin
 if user<>'RABAEV'or sys_context('USERENV','SERVICE_NAME')<>'orcl'then raise_application_error(-20999,'WRONG_TARGET');end if;
 dbms_lob.createtemporary(s,true);for r in(select TEXT from USER_SOURCE where NAME='RRL_TRADE_STOCK_GUARD'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
 if rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>'3B35292E0E15690F42ED557AF91A615590BF2A3BA9E62D1AC16C03F21893B1BA'then raise_application_error(-20999,'GUARD_SOURCE_DRIFT');end if;dbms_lob.freetemporary(s);
 dbms_lob.createtemporary(s,true);for r in(select TEXT from USER_SOURCE where NAME='RRL_ST_DEFER_HU_WAIT'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
 if rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>'52A8D5AC0833FD6EFC42BF52E0C3E49F350F3F5E8AC5FBE782CC068AE0F97940'then raise_application_error(-20999,'ACCESS_SOURCE_DRIFT');end if;dbms_lob.freetemporary(s);
end;
/
@@before_access.sql
@@before_guard.sql
begin dbms_utility.compile_schema(user,false);end;
/
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-22-trade-hu-defer-wait' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set STATUS='ROLLED_BACK',APPLIED_AT=sysdate,APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(x.MIGRATION_ID,'Allow exact registered deferred HU case tree with trade order bindings',sysdate,user,'apply.sql','rollback.sql','ROLLED_BACK');
commit;
