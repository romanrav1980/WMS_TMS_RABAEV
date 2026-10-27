whenever sqlerror exit failure rollback
declare begin if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;
end;
/
-- Restore only over the exact candidate sources and only while no removal was journalled (empty rollback).
declare s clob;n number;
 procedure same(p_name varchar2,p_type varchar2,p_hash varchar2,p_code varchar2)is begin
  dbms_lob.createtemporary(s,true);
  for r in(select TEXT from USER_SOURCE where NAME=p_name and TYPE=p_type order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
  if dbms_lob.getlength(s)=0 or rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>p_hash then raise_application_error(-20999,p_code||':'||p_name||':'||p_type);end if;
  dbms_lob.freetemporary(s);
 end;
begin
 same('RRL_TT_ADD_PALL','FUNCTION','7F464DEA27B971D4826EC89B2B6B31A4A49EF24D5ACC699A9E4F1D7A1D95C37F','AFTER_SOURCE_DRIFT_REFUSED');
 same('RRL_TT_PLACE_REMOVAL_API','PACKAGE','182FED73E4F8391A1832047CAC75AEF6F82DBE711B20ED4072A1C81E0D110CBF','AFTER_SOURCE_DRIFT_REFUSED');
 same('RRL_TT_PLACE_REMOVAL_API','PACKAGE BODY','8508DF8354CFEDAD21B81FA848ADDF03C5B7EC52E9A8E5D1691B32AA5BD8DA8E','AFTER_SOURCE_DRIFT_REFUSED');
 same('RRL_TT_MEMBERSHIP_CTX_API','PACKAGE','B8372EDC05BE4BB472A7255329799DEFB4B3C21BA19A317781C11B7AEB9A27EA','DEPENDENCY_DRIFT_REFUSED');
 same('RRL_TT_MEMBERSHIP_CTX_API','PACKAGE BODY','ACABEA11DE11D4D1CACC9DD82543C41B9444230961892F31511FE3C49C398C05','DEPENDENCY_DRIFT_REFUSED');
 same('RRL_TRANSPORT_PLAN_API','PACKAGE BODY','6CDFAAD7F49F1770B82B79CA2F1A0042823E51310FA3B61B2422B164D324BBAA','DEPENDENCY_DRIFT_REFUSED');
 same('RRL_ST_DEFER_API','PACKAGE BODY','2D4D8DD945079C2879FF50560717302EDF115681EBD0BC515F169166FDBD179A','DEPENDENCY_DRIFT_REFUSED');
 same('RRL_TRADE_STOCK_GUARD','PACKAGE','555A92C50609C9198308AE1E4129AECCB34E891ADC14170F016B739596B447AA','DEPENDENCY_DRIFT_REFUSED');
 same('RRL_TT_MEMBERSHIP_WRITER_GUARD','TRIGGER','5CCE6D59BF02AF98A33826E4066D9C94CEF2953E5C901E3A55F508D03666F929','DEPENDENCY_DRIFT_REFUSED');
end;
/
declare n number;begin
 -- The journal is working history of performed removals: rolling back after facts would lose it, so it is refused.
 select count(*)into n from RRL_TT_PLACE_REMOVAL_CMD;
 if n<>0 then raise_application_error(-20999,'TT_PLACE_REMOVAL_HISTORY_PRESENT');end if;
end;
/
drop package RRL_TT_PLACE_REMOVAL_API;
@@before_writer.sql
alter package RRL_TRANSPORT_PLAN_API compile body;
alter package RRL_ST_DEFER_API compile body;
drop table RRL_TT_PLACE_REMOVAL_CMD purge;
@@rollback_verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-27-tt-selected-places' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set STATUS='ROLLED_BACK',APPLIED_AT=sysdate,APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'Remove selected places of one assembly from a trip through the single membership writer',sysdate,user,'apply.sql','rollback.sql','ROLLED_BACK');
commit;
