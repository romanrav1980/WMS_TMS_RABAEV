-- Physical load facts supplement RRL_TT_LOAD_TASK (the existing plan); no second ST-trip assignment.
declare n number;begin
 select count(*) into n from USER_TABLES where TABLE_NAME='RRL_TT_HU_LOAD_FACT';
 if n=0 then execute immediate q'[
  create table RRL_TT_HU_LOAD_FACT(
   LOAD_OPERATION_ID varchar2(100) primary key,
   TT_ID number not null references RRL_TRANSPORT_TASK(ID),
   ROOT_UID varchar2(200) not null references RRL_PALLETS(UID_PALLET),
   VEHICLE_ID number not null references RRL_TR_VEHICLE(ID),
   VEHICLE_NUMBER varchar2(50) not null,DOCK varchar2(50) not null,WARE_ID number not null,
   STATUS varchar2(15) default 'LOADED' not null check(STATUS in('LOADED','UNLOADED','DEPARTED')),
   GROSS_WEIGHT_KG number(27,9) not null check(GROSS_WEIGHT_KG>0),
   BOUNDING_VOLUME_M3 number(27,9) not null check(BOUNDING_VOLUME_M3>0),
   CONTENT_VERSION number(19) not null,COMPOSITION_JSON clob not null check(COMPOSITION_JSON is json),
   LOADED_BY varchar2(50) not null,LOADED_AT timestamp with time zone default systimestamp not null,
   DEPARTURE_OPERATION_ID varchar2(100),DEPARTED_AT timestamp with time zone,
   constraint RRL_TT_LOAD_OP_FK foreign key(LOAD_OPERATION_ID) references RRL_STOCK_OPERATION(OPERATION_ID),
   constraint RRL_TT_DEPART_OP_FK foreign key(DEPARTURE_OPERATION_ID) references RRL_STOCK_OPERATION(OPERATION_ID)
  )]';
  execute immediate 'create index RRL_TT_HU_LOAD_TT_I1 on RRL_TT_HU_LOAD_FACT(TT_ID,STATUS)';
  execute immediate q'[create unique index RRL_TT_HU_LOAD_UID_U1 on RRL_TT_HU_LOAD_FACT(case when STATUS in('LOADED','DEPARTED') then ROOT_UID end)]';
  execute immediate q'[create table RRL_TT_HU_LOAD_ST(
   LOAD_OPERATION_ID varchar2(100) not null references RRL_TT_HU_LOAD_FACT(LOAD_OPERATION_ID),
   SBORKA_PALLET_ID number not null references RRL_SBORKA_PALLETS(ID),
   ACTIVE_FLAG number(1) default 1 not null check(ACTIVE_FLAG in(0,1)),
   constraint RRL_TT_HU_LOAD_ST_PK primary key(LOAD_OPERATION_ID,SBORKA_PALLET_ID)
  )]';
  execute immediate 'create unique index RRL_TT_HU_LOAD_ST_U1 on RRL_TT_HU_LOAD_ST(case when ACTIVE_FLAG=1 then SBORKA_PALLET_ID end)';
 end if;
end;
/
