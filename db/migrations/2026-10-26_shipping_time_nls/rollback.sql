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
 same('FTIME_SHIPPING_PLAN','FUNCTION','7E9E1AEDD9B4DC067619D19A86CC51F206C5B871257F2D023E24DE4715B33F8C');
 same('RRL_TT_PLAN_SHIPPPING_HOUR','FUNCTION','2A80C7CEDC04F87D644C40B360CE4CB5F49F52ADEF45921E5AFB71A0B21DB3B9');
 same('RRL_TT_REORDER_ADR','FUNCTION','18FEE408BC12BCB31CFB07AE2C26232C07F83C0C13498A73262657F904D81A01');
 same('RRL_ST_DEFER_API','PACKAGE BODY','2D4D8DD945079C2879FF50560717302EDF115681EBD0BC515F169166FDBD179A');
 same('RRL_TRANSPORT_PLAN_API','PACKAGE BODY','D754AD9D752FEB6C8A59399E426AA93C01F0B2A3CC7F0CFFF5910D6EC58890CA');
 same('TRANSPORT_TASK','PACKAGE BODY','57910F31B0D35DB03554D984EEDEF8EF158676737CED18D5C09AD08CFDE217ED');
 same('RRL_ST_DEFER_API','PACKAGE','C83B37A20F536A64A5707DA55B513BA1421746F047A826EC9B22474E58F6C992');
 same('RRL_TRANSPORT_PLAN_API','PACKAGE','CA927E2E73071EB85D3F18F77E53FCCDB241C79E87F5D5B413628820BB5D4C66');
 same('TRANSPORT_TASK','PACKAGE','733B704D15280CB6818724B8639164541E488404FDDA5B5E00E3D95E49FD8C42');
end;
/
@@before_function.sql
@@002_compile_callers.sql
@@rollback_verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-26-shipping-time-nls' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)when matched then update set STATUS='ROLLED_BACK',APPLIED_AT=sysdate,APPLIED_BY=user when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(x.MIGRATION_ID,'Make existing shipping-hour date conversion independent of session NLS format',sysdate,user,'apply.sql','rollback.sql','ROLLED_BACK');
commit;
