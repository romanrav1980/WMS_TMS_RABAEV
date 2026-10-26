whenever sqlerror exit failure rollback
whenever sqlerror exit failure rollback
declare begin if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;end;
/
declare s clob;
 procedure same(n varchar2,t varchar2,h varchar2)is begin
  dbms_lob.createtemporary(s,true);
  for r in(select TEXT from USER_SOURCE where NAME=n and TYPE=t order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
  if dbms_lob.getlength(s)=0 or rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>h then raise_application_error(-20999,'SOURCE_OR_DEPENDENCY_DRIFT'||':'||n||':'||t);end if;
  dbms_lob.freetemporary(s);
 end;
 begin
 same('RRL_STOCK_LOCK_API','PACKAGE BODY','47C7F2AEED9241558C7B192C0F4C5B54CBCAE4CF2E7E95AA35E19EA12457958E');
 same('RRL_STOCK_LOCK_API','PACKAGE','5E65D9B3D4B3FB367EE698B72709BF4FD396EDF2177156D73A7EB7ECF787ACD4');
 same('RRL_STOCK_POSTING_API','PACKAGE BODY','EB97721019B0177F4077C6DF224F3707D10F51DAFCD104EF0EE78D83FE56FA48');
 same('RRL_STOCK_WAVE_LAUNCH_CMD','PACKAGE BODY','BFD53F02A7B8EC4A031546A880006CCB83CC524BD34CD082535122BF3DE14E52');
end;
/
@@before_body.sql
@@rollback_verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-26-carton-lock-budget' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)when matched then update set STATUS='ROLLED_BACK',APPLIED_AT=sysdate,APPLIED_BY=user when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(x.MIGRATION_ID,'Eight-second native lock attempt for 660-place resource closure; overall HTTP deadline remains 30 seconds',sysdate,user,'apply.sql','rollback.sql','ROLLED_BACK');
commit;
