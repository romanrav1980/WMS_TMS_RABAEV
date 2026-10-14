-- Physical unit birth owner is a pallet, including inventory/MES births without SAP receipt.
declare n number;
begin
 select count(*) into n from USER_CONSTRAINTS where CONSTRAINT_NAME='RRL_PALLETS_UID_UK';
 if n=0 then execute immediate 'alter table RRL_PALLETS add constraint RRL_PALLETS_UID_UK unique(UID_PALLET)';end if;
 select count(*) into n from USER_CONSTRAINTS where CONSTRAINT_NAME='RRL_WMS_UNIT_PALLET_FK';
 if n=0 then execute immediate 'alter table RRL_WMS_RECEIPT_UNIT add constraint RRL_WMS_UNIT_PALLET_FK foreign key(UID_PALLET) references RRL_PALLETS(UID_PALLET) deferrable initially deferred';end if;
 select count(*) into n from USER_CONSTRAINTS where CONSTRAINT_NAME='RRL_WMS_REC_UNIT_FK';
 if n=1 then execute immediate 'alter table RRL_WMS_RECEIPT_UNIT drop constraint RRL_WMS_REC_UNIT_FK';end if;
end;
/
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;
begin
 select count(*) into n from USER_CONSTRAINTS c join USER_CONSTRAINTS p on p.CONSTRAINT_NAME=c.R_CONSTRAINT_NAME
 where c.CONSTRAINT_NAME='RRL_WMS_UNIT_PALLET_FK' and c.STATUS='ENABLED' and c.VALIDATED='VALIDATED' and p.TABLE_NAME='RRL_PALLETS';
 if n!=1 then raise_application_error(-20808,'PHYSICAL_UNIT_OWNER_FK_NOT_VALIDATED');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-09-013-marked-birth-owner' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Physical marked unit birth owner is pallet; inventory/MES birth independent of SAP receipt',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
