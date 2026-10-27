whenever sqlerror exit failure rollback
declare begin if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;
end;
/
-- Restore only over the exact candidate sources (no drift). Rolling back re-applies the stricter exact-version check: lines bound to an
-- older recipient version become stale again; no stock, reservation or posting is changed by this kit or its rollback.
declare s clob;n number;
 procedure same(p_name varchar2,p_type varchar2,p_hash varchar2,p_code varchar2)is begin
  dbms_lob.createtemporary(s,true);
  for r in(select TEXT from USER_SOURCE where NAME=p_name and TYPE=p_type order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
  if dbms_lob.getlength(s)=0 or rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>p_hash then raise_application_error(-20999,p_code||':'||p_name||':'||p_type);end if;
  dbms_lob.freetemporary(s);
 end;
begin
 same('RRL_TRADE_RECIPIENT_VERSION','FUNCTION','9974A571E9513B93C5E7C2AE1DA237F92A3E50EA5B1CF5607B45E1AE84B80200','AFTER_SOURCE_DRIFT_REFUSED');
 same('RRL_TRADE_PICK_CONTEXT','PACKAGE BODY','0938CD82B38B630B3C00C1C98059E2D204243CC5346CEC41EE2AFDF2DD789DAD','AFTER_SOURCE_DRIFT_REFUSED');
 same('RRL_TRADE_TRANSPORT_CORE','PACKAGE BODY','40D1EFA088E6A8170050B42ADB2CDE3FF3D16D665122D59FEB0EA3F4C05C2F34','AFTER_SOURCE_DRIFT_REFUSED');
 same('RRL_TRADE_PICK_CONTEXT','PACKAGE','229656B24904B16A276E29F8C86609549A4F87BC7242556C258C89BD38500991','DEPENDENCY_DRIFT_REFUSED');
 same('RRL_TRADE_TRANSPORT_CORE','PACKAGE','5AE5D8EF7D7C2D990DA51A1C05888FA46B936A6C2B8CE69B5C9F3A961B7A9E4F','DEPENDENCY_DRIFT_REFUSED');
 same('RRL_TRADE_TOPUP_ADOPT','PACKAGE','F6B49EA58218A622A2C77CFF9E958258AA5E8B007048055137730260D2CF6C8B','DEPENDENCY_DRIFT_REFUSED');
 same('RRL_TRADE_STOCK_GUARD','PACKAGE','555A92C50609C9198308AE1E4129AECCB34E891ADC14170F016B739596B447AA','DEPENDENCY_DRIFT_REFUSED');
end;
/
@@before_pick_context_body.sql
@@before_transport_core_body.sql
drop function RRL_TRADE_RECIPIENT_VERSION;
@@rollback_verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-27-trade-recipient-version' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set STATUS='ROLLED_BACK',APPLIED_AT=sysdate,APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'Pick context and trip demand accept a later recipient version differing only in top-up settings',sysdate,user,'apply.sql','rollback.sql','ROLLED_BACK');
commit;
