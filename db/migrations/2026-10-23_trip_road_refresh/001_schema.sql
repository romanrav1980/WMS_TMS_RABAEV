declare n number;begin
 if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_BEFORE');end if;
 select count(*)into n from USER_OBJECTS where OBJECT_NAME='RRL_TT_ROAD_REFRESH';if n<>0 then raise_application_error(-20999,'ROAD_REFRESH_ALREADY_EXISTS');end if;
end;
/
create table RRL_TT_ROAD_REFRESH(
 OPERATION_ID varchar2(100)not null,TT_ID number not null,ACTOR varchar2(50)not null,
 REQUEST_HASH varchar2(64)not null,RESULT_JSON clob not null,CREATED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_TT_ROAD_REFRESH_PK primary key(OPERATION_ID),
 constraint RRL_TT_ROAD_REFRESH_JSON check(RESULT_JSON is json)
);
create or replace trigger RRL_TT_ROAD_REFRESH_APPEND before update or delete on RRL_TT_ROAD_REFRESH
begin raise_application_error(-20911,'ROAD_REFRESH_APPEND_ONLY');end;
/