begin execute immediate q'[create table RRL_TARE_BOOK(
 OPERATION_ID varchar2(100) primary key references RRL_STOCK_OPERATION(OPERATION_ID),
 BALANCE_KEY raw(32) not null references RRL_TARE_BALANCE(BALANCE_KEY),
 OWNER_WARE_ID number not null,PALLET_TYPE_ID number not null references RRL_PALLET_TYPE(PALLET_TYPE_ID),
 PLACE_KIND varchar2(6) not null check(PLACE_KIND in('CASE','HU')),PLACE_ID varchar2(200 byte) not null,
 STATUS varchar2(12) default 'HELD' not null check(STATUS in('HELD','CANCELLED','TRANSFERRED')),
 QUANTITY number(1) default 1 not null check(QUANTITY=1),
 CREATED_BY nvarchar2(50) not null,CREATED_AT timestamp with time zone default systimestamp not null,
 CLOSED_OPERATION_ID varchar2(100) references RRL_STOCK_OPERATION(OPERATION_ID),CLOSED_BY nvarchar2(50),CLOSED_AT timestamp with time zone,
 check((STATUS='HELD' and CLOSED_OPERATION_ID is null and CLOSED_BY is null and CLOSED_AT is null)or(STATUS!='HELD' and CLOSED_OPERATION_ID is not null and CLOSED_BY is not null and CLOSED_AT is not null))
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'[create unique index RRL_TARE_BOOK_PLACE_UQ on RRL_TARE_BOOK(case when STATUS='HELD' then PLACE_KIND end,case when STATUS='HELD' then PLACE_ID end)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate 'create index RRL_TARE_BOOK_BALANCE_IX on RRL_TARE_BOOK(BALANCE_KEY,STATUS)';exception when others then if sqlcode!=-955 then raise;end if;end;
/
create or replace view RRL_TARE_AVAILABILITY as
select b.BALANCE_KEY,b.OWNER_WARE_ID,b.PALLET_TYPE_ID,b.CUSTODIAN_ID,b.QUANTITY PHYSICAL_QTY,b.BALANCE_VERSION,
 nvl(h.QTY,0) ASSEMBLY_QTY,b.QUANTITY-nvl(h.QTY,0) AVAILABLE_QTY
from RRL_TARE_BALANCE b left join(select BALANCE_KEY,sum(QUANTITY) QTY from RRL_TARE_BOOK where STATUS='HELD' group by BALANCE_KEY)h on h.BALANCE_KEY=b.BALANCE_KEY
where b.CUSTODIAN_KIND='WAREHOUSE' and b.CONDITION_CODE='GOOD';
/
