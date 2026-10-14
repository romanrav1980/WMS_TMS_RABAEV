declare n number;begin
 select count(*)into n from USER_TABLES where TABLE_NAME='RRL_WORKLOAD_SCOPE_SITE';
 if n=0 then execute immediate q'[create table RRL_WORKLOAD_SCOPE_SITE(
 WARE_ID number not null,WORK_SCOPE varchar2(30)not null,SITE_CODE varchar2(50)not null,
 VERSION_NO number(19)not null,ACTIVE number(1)not null,REASON nvarchar2(500)not null,
 OPERATION_ID varchar2(100)not null unique references RRL_WORKLOAD_OPERATION(OPERATION_ID),
 CREATED_BY nvarchar2(50)not null,CREATED_AT timestamp with time zone default systimestamp not null,
 primary key(WARE_ID,WORK_SCOPE,VERSION_NO),
 constraint RRL_WORK_SCOPE_KIND_CK check(WORK_SCOPE in('CASE_DISPATCH','FULLPAL_DISPATCH','OUTBOUND_WORKLOAD')),
 constraint RRL_WORK_SCOPE_VERSION_CK check(VERSION_NO>=1),
 constraint RRL_WORK_SCOPE_ACTIVE_CK check(ACTIVE in(0,1)))]';end if;
end;
/
