begin execute immediate q'[create table RRL_TARE_OFFER_BOOK(
 OFFER_OPERATION_ID varchar2(100) not null references RRL_TARE_OFFER(OPERATION_ID),
 BOOK_OPERATION_ID varchar2(100) not null references RRL_TARE_BOOK(OPERATION_ID),
 LOAD_OPERATION_ID varchar2(100) not null references RRL_TT_HU_LOAD_FACT(LOAD_OPERATION_ID),
 CREATED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_TARE_OFFER_BOOK_PK primary key(OFFER_OPERATION_ID,BOOK_OPERATION_ID)
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate 'create index RRL_TARE_OFFER_BOOK_BOOK_IX on RRL_TARE_OFFER_BOOK(BOOK_OPERATION_ID,OFFER_OPERATION_ID)';exception when others then if sqlcode!=-955 then raise;end if;end;
/
