whenever sqlerror exit failure rollback
declare begin if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;
end;
/
-- Restore only over the exact candidate bodies (no drift) and only before any ORDER with a non-executable line was accepted.
declare s clob;n number;
 procedure same(p_name varchar2,p_type varchar2,p_hash varchar2,p_code varchar2)is begin
  dbms_lob.createtemporary(s,true);
  for r in(select TEXT from USER_SOURCE where NAME=p_name and TYPE=p_type order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
  if dbms_lob.getlength(s)=0 or rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>p_hash then raise_application_error(-20999,p_code||':'||p_name||':'||p_type);end if;
  dbms_lob.freetemporary(s);
 end;
begin
 same('RRL_TRADE_DOCUMENT_API','PACKAGE BODY','DBFE94BF22705395208A14082480FA04B48808CB45B02D495A836B593F63596A','AFTER_SOURCE_DRIFT_REFUSED');
 same('RRL_TRADE_ORDER_API','PACKAGE BODY','AC41B2AA980FAB902A578BF9078F89C1B667C64254B599DD1855F0CB74935689','AFTER_SOURCE_DRIFT_REFUSED');
 same('RRL_TRADE_DOCUMENT_API','PACKAGE','99158EB4546B739E4E9EB3A0FAAEDCF4C6AC3F5F0A4329D15C91BDA846D1BDE0','DEPENDENCY_DRIFT_REFUSED');
 same('RRL_TRADE_ORDER_API','PACKAGE','9168989E0B7BEA4B865B746B3319097C9226CA25C4F2D43950E3BD183A76B170','DEPENDENCY_DRIFT_REFUSED');
end;
/
declare n number;begin
 -- Accepted ORDER documents with non-executable lines exist only under this kit; the previous bodies would reject their next version.
 select count(*)into n from RRL_TRADE_DOCUMENT where ENTITY_TYPE='ORDER'and STATUS='ACCEPTED'
  and json_exists(BODY_JSON,'$.lines[*]?(@.normalization.executable == false)');
 if n<>0 then raise_application_error(-20999,'TRADE_ORDER_UNIT_HISTORY_PRESENT');end if;
end;
/
@@before_document_api_body.sql
@@before_order_api_body.sql
@@rollback_verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-27-trade-order-units' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set STATUS='ROLLED_BACK',APPLIED_AT=sysdate,APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'Trade ORDER keeps non-executable normalized lines; trips refuse and binding skips them',sysdate,user,'apply.sql','rollback.sql','ROLLED_BACK');
commit;
