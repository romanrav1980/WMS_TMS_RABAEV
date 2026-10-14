create table RRL_DAY_INSPECTION(
 OPERATION_ID varchar2(100)primary key,
 REVIEW_OPERATION_ID varchar2(100)not null references RRL_DAY_REVIEW(OPERATION_ID),
 INSPECTION_ROLE varchar2(30)not null check(INSPECTION_ROLE in('WAREHOUSE_CHIEF','DISPATCHER')),
 ACTOR varchar2(50)not null,OBSERVED_EMPTY number(1)not null check(OBSERVED_EMPTY in(0,1)),
 NOTE varchar2(2000)not null,REQUEST_JSON clob not null,REQUEST_HASH varchar2(64)not null,
 SOURCE_HASH varchar2(64)not null,SOURCE_CHECKED_AT timestamp with time zone not null,
 RECORDED_AT timestamp with time zone default systimestamp not null,RESULT_JSON clob not null,
 constraint RRL_DAY_INSPECT_ROLE_U unique(REVIEW_OPERATION_ID,INSPECTION_ROLE),
 constraint RRL_DAY_INSPECT_REQUEST_J check(REQUEST_JSON is json),
 constraint RRL_DAY_INSPECT_RESULT_J check(RESULT_JSON is json)
);
/
merge into RIGHTS r using(select 'GLOBAL_ADMIN'USER_GROUP,'warehouse_day_inspect'RIGHT1 from dual)s
on(r.USER_GROUP=s.USER_GROUP and upper(r.RIGHT1)=upper(s.RIGHT1))
when not matched then insert(RIGHT1,USER_GROUP,ID,DESCR)
values(s.RIGHT1,s.USER_GROUP,(select nvl(max(ID),0)+1 from RIGHTS),'Подтверждение осмотра грузовой зоны начальником склада');
/
