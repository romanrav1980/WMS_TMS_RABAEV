begin execute immediate q'~create table RRL_PICK_RANGE_APPROVAL(PROPOSAL_ID varchar2(100)primary key references RRL_PICK_RANGE_PROPOSAL(PROPOSAL_ID),
 OPERATION_ID varchar2(100)unique not null references RRL_PICK_RANGE_OPERATION(OPERATION_ID)deferrable initially deferred,
 WARE_ID number not null,ARTICLE varchar2(40)not null,PROOF_JSON clob not null check(PROOF_JSON is json))~';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'~create table RRL_PICK_RANGE_STATUS(PICK_FACE_ARTICUL_ID number primary key references RRL_PICK_FACE_ARTICUL(PICK_FACE_ARTICUL_ID),
 MODE_CODE varchar2(20)not null check(MODE_CODE in('ACTIVE','DRAINING','CLOSED')),
 APPROVAL_OPERATION_ID varchar2(100)not null references RRL_PICK_RANGE_OPERATION(OPERATION_ID)deferrable initially deferred)~';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'~create table RRL_PICK_RANGE_ALLOW_REPL(PICK_FACE_ARTICUL_ID number not null references RRL_PICK_FACE_ARTICUL(PICK_FACE_ARTICUL_ID),
 DRAIN_OPERATION_ID varchar2(100)not null references RRL_PICK_RANGE_OPERATION(OPERATION_ID)deferrable initially deferred,
 REPLENISH_TASK_ID number not null references RRL_PICK_WAVE_REPLENISH_TASK(PICK_WAVE_REPLENISH_TASK_ID),
 MAX_ORIGINAL_QTY number not null check(MAX_ORIGINAL_QTY>=0),
 primary key(PICK_FACE_ARTICUL_ID,DRAIN_OPERATION_ID,REPLENISH_TASK_ID))~';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'~create table RRL_PICK_RANGE_MEMBER(PROPOSAL_ID varchar2(100)not null references RRL_PICK_RANGE_APPROVAL(PROPOSAL_ID),
 PICK_FACE_ARTICUL_ID number not null references RRL_PICK_FACE_ARTICUL(PICK_FACE_ARTICUL_ID),
 ROLE_CODE varchar2(10)not null check(ROLE_CODE in('OLD','NEW')),
 primary key(PROPOSAL_ID,PICK_FACE_ARTICUL_ID,ROLE_CODE))~';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'~create table RRL_PICK_RANGE_DRAIN_CLOSE(OPERATION_ID varchar2(100)primary key references RRL_PICK_RANGE_OPERATION(OPERATION_ID)deferrable initially deferred,
 PICK_FACE_ARTICUL_ID number not null references RRL_PICK_FACE_ARTICUL(PICK_FACE_ARTICUL_ID),
 FROM_APPROVAL_OPERATION_ID varchar2(100)not null references RRL_PICK_RANGE_OPERATION(OPERATION_ID))~';exception when others then if sqlcode!=-955 then raise;end if;end;
/
