declare n number;
begin
 if user!='RABAEV' then raise_application_error(-20801,'RABAEV only'); end if;
 select count(*) into n from RRL_WMS_RECEIPT_UNIT where BASE_QTY<>1;
 if n>0 then raise_application_error(-20802,'Non-piece marking quantities exist; preserve their recorded values'); end if;
 execute immediate 'alter table RRL_WMS_RECEIPT_UNIT drop constraint RRL_WMS_REC_UNIT_QTY_CK';
 execute immediate 'alter table RRL_WMS_RECEIPT_UNIT drop column BASE_QTY';
 update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-07-007-ni01-unit-quantity';
 commit;
end;
/
