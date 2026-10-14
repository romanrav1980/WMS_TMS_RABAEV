begin execute immediate q'[create table RRL_TARE_LOSS_CLAIM(
 OPERATION_ID varchar2(100) primary key references RRL_STOCK_OPERATION(OPERATION_ID),
 BALANCE_KEY raw(32) not null references RRL_TARE_BALANCE(BALANCE_KEY),
 OWNER_WARE_ID number not null,PALLET_TYPE_ID number not null,
 CONDITION_CODE varchar2(10) not null check(CONDITION_CODE in('GOOD','DAMAGED')),
 QUANTITY number(18,0) not null check(QUANTITY>0),
 REASON_TEXT varchar2(2000 byte) not null,DECISION_REFERENCE varchar2(255 byte) not null,
 ACTOR nvarchar2(50) not null,CREATED_AT timestamp with time zone default systimestamp not null
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'[create table RRL_TARE_LOSS_DECISION(
 OPERATION_ID varchar2(100) primary key references RRL_STOCK_OPERATION(OPERATION_ID),
 CLAIM_OPERATION_ID varchar2(100) not null unique references RRL_TARE_LOSS_CLAIM(OPERATION_ID),
 OUTCOME varchar2(12) not null check(OUTCOME in('WRITE_OFF','REJECT')),
 REASON_TEXT varchar2(2000 byte) not null,DECISION_REFERENCE varchar2(255 byte) not null,
 ACTOR nvarchar2(50) not null,CREATED_AT timestamp with time zone default systimestamp not null
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate 'create index RRL_TARE_LOSS_BALANCE_IX on RRL_TARE_LOSS_CLAIM(BALANCE_KEY,CREATED_AT)';exception when others then if sqlcode!=-955 then raise;end if;end;
/
create or replace view RRL_TARE_LOSS_PENDING as
select c.BALANCE_KEY,sum(c.QUANTITY) QUANTITY from RRL_TARE_LOSS_CLAIM c
where not exists(select 1 from RRL_TARE_LOSS_DECISION d where d.CLAIM_OPERATION_ID=c.OPERATION_ID) group by c.BALANCE_KEY;
/
