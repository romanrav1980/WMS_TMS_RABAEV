begin execute immediate q'~create table RRL_PICK_RANGE_OPERATION(OPERATION_ID varchar2(100) primary key,ACTION_CODE varchar2(30)not null,WARE_ID number not null,
 ARTICLE varchar2(40)not null,ACTOR varchar2(100)not null,REQUEST_HASH varchar2(64)not null,
 REQUEST_JSON clob not null check(REQUEST_JSON is json),RESULT_JSON clob not null check(RESULT_JSON is json),
 CREATED_AT timestamp with time zone default systimestamp not null)~';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'~create table RRL_PICK_RANGE_PROPOSAL(PROPOSAL_ID varchar2(100)primary key references RRL_PICK_RANGE_OPERATION(OPERATION_ID),
 WARE_ID number not null,ARTICLE varchar2(40)not null,SOURCE_SIGNATURE varchar2(64)not null,
 SOURCE_JSON clob not null check(SOURCE_JSON is json))~';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'~create table RRL_PICK_RANGE_CANCEL(PROPOSAL_ID varchar2(100)primary key references RRL_PICK_RANGE_PROPOSAL(PROPOSAL_ID),
 CANCEL_OPERATION_ID varchar2(100)unique not null references RRL_PICK_RANGE_OPERATION(OPERATION_ID),
 REASON varchar2(2000)not null)~';exception when others then if sqlcode!=-955 then raise;end if;end;
/
