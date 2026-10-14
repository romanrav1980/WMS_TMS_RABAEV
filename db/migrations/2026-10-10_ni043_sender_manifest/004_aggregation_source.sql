-- Aggregation scanning also belongs to inventory/MES birth.
-- Preserve the existing canonical scan table; never manufacture a SAP receipt.
declare n number;parent_name varchar2(128);begin
 select count(*)into n from RRL_WMS_RECEIPT_AGG a where not exists(select 1 from RRL_PALLETS p where p.UID_PALLET=a.UID_PALLET);
 if n!=0 then raise_application_error(-20899,'TRACE124_AGGREGATION_ORPHAN');end if;
 select p.TABLE_NAME into parent_name from USER_CONSTRAINTS c join USER_CONSTRAINTS p on p.CONSTRAINT_NAME=c.R_CONSTRAINT_NAME where c.CONSTRAINT_NAME='RRL_WMS_REC_AGG_FK';
 if parent_name!='RRL_PALLETS' then
  execute immediate 'alter table RRL_WMS_RECEIPT_AGG add constraint RRL_WMS_REC_AGG_LOT_FK foreign key(UID_PALLET) references RRL_PALLETS(UID_PALLET) deferrable initially deferred';
  execute immediate 'alter table RRL_WMS_RECEIPT_AGG drop constraint RRL_WMS_REC_AGG_FK';
  execute immediate 'alter table RRL_WMS_RECEIPT_AGG rename constraint RRL_WMS_REC_AGG_LOT_FK to RRL_WMS_REC_AGG_FK';
 end if;
end;
/
