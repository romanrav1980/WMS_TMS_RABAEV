whenever sqlerror exit failure rollback
declare begin if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;
end;
/
-- Restore only over the exact candidate body (no drift) and only before any trade shortage decision was posted under it.
declare s clob;n number;
 procedure same(p_name varchar2,p_type varchar2,p_hash varchar2,p_code varchar2)is begin
  dbms_lob.createtemporary(s,true);
  for r in(select TEXT from USER_SOURCE where NAME=p_name and TYPE=p_type order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
  if dbms_lob.getlength(s)=0 or rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>p_hash then raise_application_error(-20999,p_code||':'||p_name||':'||p_type);end if;
  dbms_lob.freetemporary(s);
 end;
begin
 same('RRL_TRADE_STOCK_GUARD','PACKAGE BODY','E72348D2921BA0E20908C575877AB5E0A7BF40467BF353572E94D8DFF0992AA1','AFTER_SOURCE_DRIFT_REFUSED');
 same('RRL_TRADE_STOCK_GUARD','PACKAGE','555A92C50609C9198308AE1E4129AECCB34E891ADC14170F016B739596B447AA','DEPENDENCY_DRIFT_REFUSED');
 same('RRL_TRADE_PICK_CONTEXT','PACKAGE','229656B24904B16A276E29F8C86609549A4F87BC7242556C258C89BD38500991','DEPENDENCY_DRIFT_REFUSED');
 same('RRL_STOCK_CASE_SHORT_CMD','PACKAGE BODY','52299F14EBB41C5CEB5C78B3D8EEB52726156247007D2F202D1BF017E068FAFA','DEPENDENCY_DRIFT_REFUSED');
 same('RRL_STOCK_SHORT_RECOVERY','PACKAGE BODY','F01F32A68888AB378C538E30CE4D5F7FE423ECF255B5886ACE8A78FFCF67285E','DEPENDENCY_DRIFT_REFUSED');
 same('RRL_CASE_TASK_ACCESS','PACKAGE BODY','BA928F64E945E15CAC233AAF7818F7128A64A860DA2B6328C3ABC400CF7654B2','DEPENDENCY_DRIFT_REFUSED');
 same('RRL_TRADE_CASE_ACCESS','PACKAGE BODY','134E81A8776F4D01C7D8A640A2271D2CCDD25957A5150F169D90977044F70EA2','DEPENDENCY_DRIFT_REFUSED');
 same('RRL_STOCK_CASE_PICK_CMD','PACKAGE','2CAE60FCC1E7A21D850FAA0135B422196382F985025E9C46174ED92A19272DC5','DEPENDENCY_DRIFT_REFUSED');
end;
/
declare n number;applied date;begin
 select max(APPLIED_AT)into applied from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-23-trade-short-guard-v2' and STATUS='APPLIED';
 -- Shortage decisions on trade stock decided under this branch are working history; reverting the branch is refused once any exists.
 select count(*)into n from RRL_STOCK_OPERATION o join RRL_CASE_PICK_SHORT s on s.CASE_PICK_SHORT_ID=json_value(o.CANONICAL_REQUEST,'$.source.short_id' returning number)
  join RRL_CASE_PICK_TASK ct on ct.CASE_PICK_TASK_ID=s.CASE_PICK_TASK_ID join RRL_TRADE_SITE ts on ts.WARE_ID=ct.WARE_ID
  where o.COMMAND_TYPE='CASE_SHORT_APPROVE'and o.STATE='APPLIED'and(applied is null or o.CREATED_AT>=applied);
 if n<>0 then raise_application_error(-20999,'TRADE_SHORT_HISTORY_PRESENT');end if;
end;
/
@@before_guard_body.sql
@@rollback_verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-23-trade-short-guard-v2' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set STATUS='ROLLED_BACK',APPLIED_AT=sysdate,APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'Trade stock guard admits CASE_SHORT_APPROVE bound to its own CASE line',sysdate,user,'apply.sql','rollback.sql','ROLLED_BACK');
commit;
