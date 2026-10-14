begin
 execute immediate q'[create table RRL_PALLET_FLOOR_TYPE(
 UID_PALLET varchar2(200) primary key,
 PALLET_TYPE_ID number not null,
 TYPE_VERSION number not null,
 LAST_OPERATION_ID varchar2(100) not null,
 DECLARED_WARE_ID number not null,
 constraint RRL_PAL_FLOOR_UID_FK foreign key(UID_PALLET)references RRL_PALLETS(UID_PALLET),
 constraint RRL_PAL_FLOOR_TYPE_FK foreign key(PALLET_TYPE_ID)references RRL_PALLET_TYPE(PALLET_TYPE_ID),
 constraint RRL_PAL_FLOOR_OP_FK foreign key(LAST_OPERATION_ID)references RRL_STOCK_OPERATION(OPERATION_ID),
 constraint RRL_PAL_FLOOR_VERSION_CK check(TYPE_VERSION>=1 and TYPE_VERSION=trunc(TYPE_VERSION))
 )]';
end;
/
alter table RRL_TT_LOAD_FLOOR_FACT drop constraint RRL_LOAD_FLOOR_ORIGIN_CK;
/
alter table RRL_TT_LOAD_FLOOR_FACT add constraint RRL_LOAD_FLOOR_ORIGIN_CK check(TYPE_ORIGIN in('CASE_TYPE','HELD_HU_TARE_BOOK','ROOT_STOCK_TYPE'));
/
