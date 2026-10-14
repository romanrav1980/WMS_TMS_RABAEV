declare n number;begin
 select count(*)into n from USER_TABLES where TABLE_NAME='RRL_IW_RECOVERY_PUT_PLAN';
 if n=0 then execute immediate 'create table RRL_IW_RECOVERY_PUT_PLAN(
 OPERATION_ID varchar2(100)primary key,RECOVERY_OPERATION_ID varchar2(100)not null references RRL_INTERWARE_RECOVERY_RECEIPT(OPERATION_ID),
 TASK_ID number not null unique references RRL_WAREHOUSE_TASK(TASK_ID),TARGET_CELL varchar2(60)not null,ACTOR varchar2(100)not null,
 TEMP_DECISION_OPERATION_ID varchar2(100),TASK_TEMP_MIN number,TASK_TEMP_MAX number,
 CREATED_AT timestamp with time zone default systimestamp not null)';end if;
 select count(*)into n from USER_TABLES where TABLE_NAME='RRL_IW_RECOVERY_PLACEMENT';
 if n=0 then execute immediate 'create table RRL_IW_RECOVERY_PLACEMENT(
 TASK_ID number primary key references RRL_IW_RECOVERY_PUT_PLAN(TASK_ID),
 RECOVERY_OPERATION_ID varchar2(100)not null unique references RRL_INTERWARE_RECOVERY_RECEIPT(OPERATION_ID),
 OPERATION_ID varchar2(100)not null unique,ROOT_UID varchar2(200)not null,WARE_ID number not null,
 TARGET_CELL varchar2(60)not null,BASE_QTY number not null check(BASE_QTY>0),BASE_UOM varchar2(20)not null,
 ACTOR varchar2(100)not null,CREATED_AT timestamp with time zone default systimestamp not null)';end if;
end;
/
