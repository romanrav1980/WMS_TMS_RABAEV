begin execute immediate q'[create table RRL_STORE_RETURN_SAP(
 OPERATION_ID varchar2(100 byte) primary key references RRL_STOCK_OPERATION(OPERATION_ID),
 APPROVAL_OPERATION_ID varchar2(100 byte) not null unique references RRL_STORE_RETURN_APPROVAL(OPERATION_ID),
 SAP_SENDER varchar2(100 byte) not null,
 MESSAGE_ID varchar2(100 byte) not null,
 RETURN_DOCUMENT varchar2(100 byte) not null,
 WARE_ID number not null,
 RECEIVE_CELL varchar2(255 byte) not null,
 ORIGINAL_XML_BASE64 clob not null,
 ORIGINAL_SHA256 varchar2(64 byte) not null,
 IMPORTED_BY nvarchar2(50) not null,
 IMPORTED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_STORE_RETURN_SAP_MSG_UQ unique(SAP_SENDER,MESSAGE_ID),
 constraint RRL_STORE_RETURN_SAP_DOC_UQ unique(SAP_SENDER,RETURN_DOCUMENT)
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
