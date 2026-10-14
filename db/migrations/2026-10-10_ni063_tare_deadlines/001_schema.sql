begin execute immediate q'[create table RRL_TARE_RETURN_POLICY(
 SCOPE_KIND varchar2(10) not null check(SCOPE_KIND in('STORE','CUSTOMER')),
 SCOPE_KEY varchar2(255 byte) not null,
 RETURN_MODE varchar2(16) not null check(RETURN_MODE in('NEXT_DELIVERY','DAYS','SAME_DAY')),
 RETURN_DAYS number(4,0),
 TIMEZONE_REGION varchar2(64 byte) not null,
 POLICY_VERSION number(19,0) not null check(POLICY_VERSION>=1),
 CHANGED_BY nvarchar2(50) not null,CHANGED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_TARE_RETURN_POLICY_PK primary key(SCOPE_KIND,SCOPE_KEY),
 check((RETURN_MODE='DAYS' and RETURN_DAYS between 1 and 3660)or(RETURN_MODE!='DAYS' and RETURN_DAYS is null))
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'[create table RRL_TARE_DELIVERY_POLICY(
 ACCEPT_OPERATION_ID varchar2(100) primary key references RRL_TARE_ACCEPT(OPERATION_ID),
 SCOPE_KIND varchar2(10) not null,SCOPE_KEY varchar2(255 byte) not null,
 POLICY_VERSION number(19,0) not null,RETURN_MODE varchar2(16) not null,RETURN_DAYS number(4,0),
 TIMEZONE_REGION varchar2(64 byte) not null,DUE_AT timestamp with time zone
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate 'create index RRL_TARE_OFFER_TO_KEY_IX on RRL_TARE_OFFER(TO_KIND,OWNER_WARE_ID,TO_ID,PALLET_TYPE_ID,CONDITION_CODE)';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate 'create index RRL_TARE_OFFER_FROM_KEY_IX on RRL_TARE_OFFER(FROM_KIND,OWNER_WARE_ID,FROM_ID,PALLET_TYPE_ID,CONDITION_CODE)';exception when others then if sqlcode!=-955 then raise;end if;end;
/
