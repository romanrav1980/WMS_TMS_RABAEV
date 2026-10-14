begin execute immediate q'[create table RRL_TARE_DAMAGE_ORIGIN(
 DAMAGE_OPERATION_ID varchar2(100) primary key references RRL_TARE_RESOLUTION(OPERATION_ID),
 ORIGIN_BALANCE_KEY raw(32) not null references RRL_TARE_BALANCE(BALANCE_KEY),
 QUANTITY number(18,0) not null check(QUANTITY>0),
 CREATED_AT timestamp with time zone default systimestamp not null)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/

begin execute immediate q'[create table RRL_TARE_DAMAGE_POSITION(
 DAMAGE_OPERATION_ID varchar2(100) not null references RRL_TARE_DAMAGE_ORIGIN(DAMAGE_OPERATION_ID),
 BALANCE_KEY raw(32) not null references RRL_TARE_BALANCE(BALANCE_KEY),
 QUANTITY number(18,0) not null check(QUANTITY>=0),
 VERSION_NO number(19) not null check(VERSION_NO>0),
 LAST_OPERATION_ID varchar2(100) not null references RRL_STOCK_OPERATION(OPERATION_ID),
 primary key(DAMAGE_OPERATION_ID,BALANCE_KEY))]';exception when others then if sqlcode!=-955 then raise;end if;end;
/

begin execute immediate q'[create index RRL_TARE_DAMAGE_POS_BAL_IX on RRL_TARE_DAMAGE_POSITION(BALANCE_KEY,DAMAGE_OPERATION_ID)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/

begin execute immediate q'[create table RRL_TARE_DAMAGE_OFFER(
 OFFER_OPERATION_ID varchar2(100) primary key references RRL_TARE_OFFER(OPERATION_ID),
 DAMAGE_OPERATION_ID varchar2(100) not null references RRL_TARE_DAMAGE_ORIGIN(DAMAGE_OPERATION_ID))]';exception when others then if sqlcode!=-955 then raise;end if;end;
/

begin execute immediate q'[create table RRL_TARE_DAMAGE_MOVE(
 ACCEPT_OPERATION_ID varchar2(100) primary key references RRL_TARE_ACCEPT(OPERATION_ID),
 DAMAGE_OPERATION_ID varchar2(100) not null references RRL_TARE_DAMAGE_ORIGIN(DAMAGE_OPERATION_ID),
 FROM_BALANCE_KEY raw(32) not null references RRL_TARE_BALANCE(BALANCE_KEY),
 TO_BALANCE_KEY raw(32) not null references RRL_TARE_BALANCE(BALANCE_KEY),
 QUANTITY number(18,0) not null check(QUANTITY>0),
 CREATED_AT timestamp with time zone default systimestamp not null,
 check(FROM_BALANCE_KEY!=TO_BALANCE_KEY))]';exception when others then if sqlcode!=-955 then raise;end if;end;
/

begin execute immediate q'[create index RRL_TARE_DAMAGE_MOVE_ORIG_IX on RRL_TARE_DAMAGE_MOVE(DAMAGE_OPERATION_ID,CREATED_AT)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
