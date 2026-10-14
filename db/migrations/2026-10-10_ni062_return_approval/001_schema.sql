begin execute immediate 'create table RRL_STORE_RETURN_APPROVAL(
 OPERATION_ID varchar2(100 byte) primary key references RRL_STOCK_OPERATION(OPERATION_ID),
 RECEIPT_OPERATION_ID varchar2(100 byte) not null,
 LINE_NO number(10) not null,
 LOT_UID varchar2(200 byte) not null,
 ARTICLE varchar2(160 byte) not null,
 BASE_UOM varchar2(20 byte) not null,
 BASE_QTY number(27,9) not null check(BASE_QTY>0),
 DISPOSITION varchar2(20 byte) not null check(DISPOSITION in(''REUSE'',''SUPPLIER'',''DISPOSAL'')),
 REASON_TEXT varchar2(2000 byte) not null,
 DECISION_REFERENCE varchar2(255 byte) not null,
 COMPLETE_GOOD_BOX number(1) not null check(COMPLETE_GOOD_BOX in(0,1)),
 APPROVED_BY nvarchar2(50) not null,
 APPROVED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_STORE_RETURN_ORIGINAL_FK foreign key(RECEIPT_OPERATION_ID,LINE_NO) references RRL_STORE_RECEIPT_LINE(OPERATION_ID,LINE_NO)
)';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate 'create index RRL_STORE_RETURN_ORIGINAL_IDX on RRL_STORE_RETURN_APPROVAL(RECEIPT_OPERATION_ID,LINE_NO)';exception when others then if sqlcode!=-955 then raise;end if;end;
/
