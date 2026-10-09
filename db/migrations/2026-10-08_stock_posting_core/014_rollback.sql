prompt Only empty PREPARED foundation can be removed; source/archives are retained
declare n number; v_state varchar2(20);
begin
 select STATE into v_state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if v_state!='PREPARED' then raise_application_error(-20807,'Release is not PREPARED; isolated recovery required'); end if;
 select count(*) into n from RRL_STOCK_OPERATION;
 if n>0 then raise_application_error(-20808,'Operations exist; dropping durable identity forbidden'); end if;
 select count(*) into n from RRL_STOCK_BASELINE;
 if n>0 then raise_application_error(-20809,'Baseline exists; preserve history'); end if;
end;
/
alter table RRL_REMAINS drop constraint RRL_REMAINS_HARD_CK;
alter table RRL_EVENTS drop constraint RRL_EVENTS_OPERATION_UK;
alter table RRL_REMAINS drop(HARD_RESERVED_BASE,STOCK_VERSION,BASE_UOM);
alter table RRL_STOCK_RESERVATION drop(BASE_QTY,BASE_UOM,RESERVATION_VERSION);
alter table RRL_EVENTS drop(OPERATION_ID,LINE_NO,LEG_NO,BASE_QTY,BASE_UOM,UOM_POLICY_VERSION,ORIGINAL_OPERATION_ID);
drop table RRL_STOCK_B0_ROWS;
drop table RRL_STOCK_BASELINE;
drop table RRL_STOCK_WRITER_REGISTRY;
drop table RRL_STOCK_UOM_CONVERSION;
drop table RRL_STOCK_POLICY_GUARD;
drop table RRL_STOCK_GUARD;
drop table RRL_STOCK_OPERATION;
drop table RRL_STOCK_RELEASE;
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-08-014-stock-posting-foundation';
commit;