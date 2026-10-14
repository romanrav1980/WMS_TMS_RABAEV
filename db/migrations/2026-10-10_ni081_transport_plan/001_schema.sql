begin execute immediate q'[create table RRL_PLANNER_APPLY_RESULT(
 PLAN_ID number primary key references RRL_PLANNER_PLANS(ID),SOURCE_HASH varchar2(64)not null,
 SHIPMENT_DATE date not null,DOCK varchar2(100),ACTOR nvarchar2(50)not null,
 RESULT_JSON clob not null check(RESULT_JSON is json),APPLIED_AT timestamp with time zone default systimestamp not null)]';
exception when others then if sqlcode!=-955 then raise;end if;end;
/
