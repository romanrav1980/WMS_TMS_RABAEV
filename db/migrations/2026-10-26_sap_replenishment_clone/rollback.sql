whenever sqlerror exit failure rollback
declare begin if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;end;
/
declare s clob;
 procedure same(n varchar2,t varchar2,h varchar2)is begin
  dbms_lob.createtemporary(s,true);
  for r in(select TEXT from USER_SOURCE where NAME=n and TYPE=t order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
  if dbms_lob.getlength(s)=0 or rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>h then raise_application_error(-20999,'AFTER_SOURCE_DRIFT_REFUSED'||':'||n||':'||t);end if;
  dbms_lob.freetemporary(s);
 end;
 begin
 same('RRL_SAP_PALLET_WRITE_GUARD','TRIGGER','915C3E502EEBD4670E67FDA737DB92EE385781C221A86EE1ECB3A8E2D864F7DB');
 same('RRL_STOCK_TASK_PLAN','PACKAGE BODY','F860BD48AB59205FCE072A1E95E4192B1FF6783507C7938261B6F2F7E9AAF692');
 same('RRL_STOCK_TASK_CORE','PACKAGE BODY','F365252A78143CB361BA6A643C7D5579E4AB8CF00CF569ADFCE126991BF24F9C');
end;
/
declare n number;begin
 select count(*)into n from RRL_STOCK_OPERATION o join RRL_PALLETS p on p.CREATED_BY_STOCK_OP=o.OPERATION_ID
 join RRL_SAP_PALLET_RECEIPT r on r.UID_PALLET=p.STOCK_ORIGIN_UID
 where o.COMMAND_TYPE='TASK_COMPLETE'and o.STATE='APPLIED';
 if n<>0 then raise_application_error(-20999,'SAP_REPLENISHMENT_CLONE_HISTORY_PRESENT');end if;
end;
/
@@before_trigger.sql
@@rollback_verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-26-sap-replenishment-clone' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)when matched then update set STATUS='ROLLED_BACK',APPLIED_AT=sysdate,APPLIED_BY=user when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(x.MIGRATION_ID,'Exact native SAP replenishment partial clone',sysdate,user,'apply.sql','rollback.sql','ROLLED_BACK');
commit;
