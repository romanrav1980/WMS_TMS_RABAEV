create table RRL_SAP_STORE_DECISION(
 SENDER varchar2(100)not null,MESSAGE_ID varchar2(100)not null,DECISION_ID varchar2(100)not null,
 CUSTOMER_ORDER_ID number not null references RRL_SAP_STORE_ORDER(CUSTOMER_ORDER_ID),
 VERSION_NO number not null,PAYLOAD_HASH varchar2(64)not null,
 ORIGINAL_CONTENT_HASH varchar2(64)not null,DECISION_CODE varchar2(10)not null,
 ACTOR varchar2(50)not null,RAW_XML clob not null,RESULT_JSON clob not null check(RESULT_JSON is json),
 CREATED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_SAP_STORE_DEC_PK primary key(SENDER,MESSAGE_ID),
 constraint RRL_SAP_STORE_DEC_ID_UK unique(SENDER,DECISION_ID),
 constraint RRL_SAP_STORE_DEC_VER_UK unique(CUSTOMER_ORDER_ID,VERSION_NO),
 constraint RRL_SAP_STORE_DEC_VER_CK check(VERSION_NO>0),
 constraint RRL_SAP_STORE_DEC_CODE_CK check(DECISION_CODE in('ACCEPT','REJECT'))
);
/
