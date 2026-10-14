begin execute immediate q'[create table RRL_TRANSPORT_COST_CLAIM(
 DEPARTURE_OPERATION_ID varchar2(100)primary key references RRL_STOCK_OPERATION(OPERATION_ID),
 OPERATION_ID varchar2(100)not null unique references RRL_LOGISTICS_COST_RUN(OPERATION_ID),
 SOURCE_PRICE_ID number not null,VERSION_NO number(19)not null,
 foreign key(SOURCE_PRICE_ID,VERSION_NO)references RRL_TRANSPORT_NORM_HISTORY(SOURCE_PRICE_ID,VERSION_NO))]';
exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'[create table RRL_TRANSPORT_COST_DETAIL(
 OPERATION_ID varchar2(100)not null references RRL_LOGISTICS_COST_RUN(OPERATION_ID),
 COST_CODE varchar2(40)not null,QUANTITY number(19)not null check(QUANTITY>0),
 RATE_VALUE number(27,9)not null check(RATE_VALUE>=0),AMOUNT number(27,2)not null check(AMOUNT>=0),
 BASIS varchar2(20)not null check(BASIS in('TRIP','POINT','PLACE')),
 primary key(OPERATION_ID,COST_CODE),check(AMOUNT=QUANTITY*round(RATE_VALUE,2)))]';
exception when others then if sqlcode!=-955 then raise;end if;end;
/
