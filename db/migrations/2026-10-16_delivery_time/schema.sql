create table RRL_DELIVERY_WINDOW(
 OPERATION_ID varchar2(100)not null,PAYLOAD_HASH raw(32)not null,LOAD_OPERATION_ID varchar2(100)not null,
 STORE_ADDR varchar2(255)not null,WARE_ID number not null,TT_ID number not null,VERSION_NO number not null,
 WINDOW_START timestamp(6)with time zone not null,WINDOW_FINISH timestamp(6)with time zone not null,
 ACTOR varchar2(50)not null,REASON_TEXT varchar2(500)not null,RECORDED_AT timestamp(6)with time zone default systimestamp not null,
 PAYLOAD_JSON clob not null,RESULT_JSON clob not null,
 constraint RRL_DELIV_WINDOW_PK primary key(OPERATION_ID),
 constraint RRL_DELIV_WINDOW_VER_UK unique(LOAD_OPERATION_ID,STORE_ADDR,VERSION_NO),
 constraint RRL_DELIV_WINDOW_LOAD_FK foreign key(LOAD_OPERATION_ID)references RRL_TT_HU_LOAD_FACT(LOAD_OPERATION_ID),
 constraint RRL_DELIV_WINDOW_WARE_FK foreign key(WARE_ID)references RRL_WARES(ID),
 constraint RRL_DELIV_WINDOW_RANGE_C check(WINDOW_FINISH>=WINDOW_START and VERSION_NO>0),
 constraint RRL_DELIV_WINDOW_JSON_C check(PAYLOAD_JSON is json and RESULT_JSON is json)
);
create index RRL_DELIV_WINDOW_WARE_IX on RRL_DELIVERY_WINDOW(WARE_ID,WINDOW_START,LOAD_OPERATION_ID);
create table RRL_DELIVERY_ARRIVAL(
 OPERATION_ID varchar2(100)not null,PAYLOAD_HASH raw(32)not null,LOAD_OPERATION_ID varchar2(100)not null,
 STORE_ADDR varchar2(255)not null,WARE_ID number not null,TT_ID number not null,
 WINDOW_OPERATION_ID varchar2(100),ARRIVED_AT timestamp(6)with time zone not null,
 ON_TIME_STATE varchar2(20)not null,ACTOR varchar2(50)not null,REASON_TEXT varchar2(500)not null,
 RECORDED_AT timestamp(6)with time zone default systimestamp not null,PAYLOAD_JSON clob not null,RESULT_JSON clob not null,
 constraint RRL_DELIV_ARRIVAL_PK primary key(OPERATION_ID),
 constraint RRL_DELIV_ARRIVAL_LOAD_UK unique(LOAD_OPERATION_ID,STORE_ADDR),
 constraint RRL_DELIV_ARRIVAL_LOAD_FK foreign key(LOAD_OPERATION_ID)references RRL_TT_HU_LOAD_FACT(LOAD_OPERATION_ID),
 constraint RRL_DELIV_ARRIVAL_WIN_FK foreign key(WINDOW_OPERATION_ID)references RRL_DELIVERY_WINDOW(OPERATION_ID),
 constraint RRL_DELIV_ARRIVAL_WARE_FK foreign key(WARE_ID)references RRL_WARES(ID),
 constraint RRL_DELIV_ARRIVAL_STATE_C check(ON_TIME_STATE in('ON_TIME','EARLY','LATE','NO_PLAN')),
 constraint RRL_DELIV_ARRIVAL_JSON_C check(PAYLOAD_JSON is json and RESULT_JSON is json)
);
create index RRL_DELIV_ARRIVAL_WARE_IX on RRL_DELIVERY_ARRIVAL(WARE_ID,ARRIVED_AT,LOAD_OPERATION_ID);
