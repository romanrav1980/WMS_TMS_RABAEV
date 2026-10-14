create table RRL_INTERWARE_UNIT_MANIFEST(
 PLAN_OPERATION_ID varchar2(100)primary key references RRL_INTERWARE_PLAN(OPERATION_ID),
 UNIT_SIGNATURE varchar2(64)not null,
 MANIFEST_JSON clob not null check(MANIFEST_JSON is json),
 CREATED_BY nvarchar2(50)not null,
 CREATED_AT timestamp with time zone default systimestamp not null
);
