declare n number;
begin
 select count(*) into n from user_tables where table_name='RRL_STORE_SCALE_DEVICE';
 if n=0 then execute immediate 'create table RRL_STORE_SCALE_DEVICE(
 DEVICE_ID varchar2(100) primary key,STORE_ADDR varchar2(255) not null references RRL_STORE_RECEIPT_POLICY(STORE_ADDR),
 SENDER_ID nvarchar2(50) not null,POLICY_VERSION number(10) default 1 not null,
 ACTIVE_FLAG number(1) default 0 not null check(ACTIVE_FLAG in(0,1)),
 CAPACITY_KG number(27,9) not null check(CAPACITY_KG>0),RESOLUTION_KG number(27,9) not null check(RESOLUTION_KG>0),
 CALIBRATION_REF varchar2(100) not null,CALIBRATED_UNTIL timestamp with time zone not null,
 CHANGED_BY varchar2(50) not null,CHANGED_AT timestamp with time zone default systimestamp not null)';end if;
 select count(*) into n from user_tables where table_name='RRL_STORE_SCALE_CAPTURE';
 if n=0 then execute immediate 'create table RRL_STORE_SCALE_CAPTURE(
 CAPTURE_KEY varchar2(64) primary key,DEVICE_ID varchar2(100) not null references RRL_STORE_SCALE_DEVICE(DEVICE_ID),
 CAPTURE_ID varchar2(100) not null,LOAD_OPERATION_ID varchar2(100) not null references RRL_TT_HU_LOAD_FACT(LOAD_OPERATION_ID),
 STORE_ADDR varchar2(255) not null references RRL_STORE_RECEIPT_POLICY(STORE_ADDR),
 DEVICE_POLICY_VERSION number(10) not null,DEVICE_CALIBRATION_REF varchar2(100) not null,
 CAPACITY_KG number(27,9) not null,RESOLUTION_KG number(27,9) not null,
 GROSS_WEIGHT_KG number(27,9) not null check(GROSS_WEIGHT_KG>0),
 SAMPLE_MIN_KG number(27,9) not null,SAMPLE_MAX_KG number(27,9) not null,
 SAMPLE_COUNT number(3) not null,SPAN_MS number(6) not null,
 MEASURED_AT timestamp with time zone not null,ZERO_CHECK_AT timestamp with time zone not null,
 RECEIVED_AT timestamp with time zone default systimestamp not null,RECORDED_BY varchar2(50) not null,
 SOURCE_SHA256 varchar2(64) not null,SOURCE_JSON clob not null check(SOURCE_JSON is json),
 RESULT_JSON clob not null check(RESULT_JSON is json),unique(DEVICE_ID,CAPTURE_ID))';end if;
 select count(*) into n from user_indexes where index_name='RRL_STORE_SCALE_LOAD_IDX';
 if n=0 then execute immediate 'create index RRL_STORE_SCALE_LOAD_IDX on RRL_STORE_SCALE_CAPTURE(LOAD_OPERATION_ID,STORE_ADDR,RECEIVED_AT)';end if;
end;
/
