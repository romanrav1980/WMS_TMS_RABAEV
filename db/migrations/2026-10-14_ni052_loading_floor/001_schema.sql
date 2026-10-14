begin
 execute immediate q'[create table RRL_TT_LOAD_FLOOR_FACT(
 LOAD_OPERATION_ID varchar2(100) primary key,
 VEHICLE_ID number not null,
 PROFILE_VERSION number not null,
 PALLET_TYPE_ID number not null,
 TYPE_ORIGIN varchar2(24) not null,
 SOURCE_REFERENCE varchar2(200) not null,
 ACTOR nvarchar2(50) not null,
 RECORDED_AT timestamp with time zone default systimestamp not null,
 CONFIRMATION_JSON clob not null,
 constraint RRL_LOAD_FLOOR_LOAD_FK foreign key(LOAD_OPERATION_ID)references RRL_TT_HU_LOAD_FACT(LOAD_OPERATION_ID),
 constraint RRL_LOAD_FLOOR_PROFILE_FK foreign key(VEHICLE_ID,PROFILE_VERSION)references RRL_VEHICLE_PROFILE_HIST(VEHICLE_ID,VERSION_NO),
 constraint RRL_LOAD_FLOOR_TYPE_FK foreign key(PALLET_TYPE_ID)references RRL_PALLET_TYPE(PALLET_TYPE_ID),
 constraint RRL_LOAD_FLOOR_ORIGIN_CK check(TYPE_ORIGIN in('CASE_TYPE','HELD_HU_TARE_BOOK')),
 constraint RRL_LOAD_FLOOR_JSON_CK check(CONFIRMATION_JSON is json)
 )]';
end;
/
