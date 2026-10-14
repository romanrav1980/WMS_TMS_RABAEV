-- Refuse before changing constraints if retained inventory/MES birth evidence needs the new owner.
declare n number;
begin
 select count(*) into n from RRL_WMS_RECEIPT_UNIT u where not exists(select 1 from RRL_SAP_PALLET_RECEIPT r where r.UID_PALLET=u.UID_PALLET);
 if n>0 then raise_application_error(-20808,'ROLLBACK_BLOCKED_BY_RETAINED_NON_SAP_UNIT_BIRTHS');end if;
 select count(*) into n from USER_CONSTRAINTS where CONSTRAINT_NAME='RRL_WMS_REC_UNIT_FK';
 if n=0 then execute immediate 'alter table RRL_WMS_RECEIPT_UNIT add constraint RRL_WMS_REC_UNIT_FK foreign key(UID_PALLET) references RRL_SAP_PALLET_RECEIPT(UID_PALLET) deferrable initially deferred';end if;
 select count(*) into n from USER_CONSTRAINTS where CONSTRAINT_NAME='RRL_WMS_UNIT_PALLET_FK';
 if n=1 then execute immediate 'alter table RRL_WMS_RECEIPT_UNIT drop constraint RRL_WMS_UNIT_PALLET_FK';end if;
end;
/
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-09-013-marked-birth-owner';
commit;
/
