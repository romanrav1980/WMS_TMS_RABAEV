whenever sqlerror exit failure rollback
declare s clob;begin
 if user<>'RABAEV'or sys_context('USERENV','SERVICE_NAME')<>'orcl'then raise_application_error(-20999,'WRONG_TARGET');end if;
 dbms_lob.createtemporary(s,true);for r in(select TEXT from USER_SOURCE where NAME='RRL_HU_EXEC_ACCESS'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
 if rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>'49293B548270EB0DB3C3F8509A7E2DCBC406307C0450B7DE0F4524ABD0A69C91'then raise_application_error(-20999,'ACCESS_SOURCE_DRIFT');end if;dbms_lob.freetemporary(s);
 dbms_lob.createtemporary(s,true);for r in(select TEXT from USER_SOURCE where NAME='RRL_ST_DEFER_WAIT_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
 if rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>'FC9F695CD6F4304EFE09A7E742D3A1C71CD678B92E626118824B3E61F935B213'then raise_application_error(-20999,'WAITING_SOURCE_DRIFT');end if;dbms_lob.freetemporary(s);
end;
/
@@before_access.sql
@@before_waiting.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-22-trade-hu-wait-replay' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set STATUS='ROLLED_BACK',APPLIED_AT=sysdate,APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(x.MIGRATION_ID,'Check current owners on original HU waiting plan and completion replay',sysdate,user,'apply.sql','rollback.sql','ROLLED_BACK');
commit;
