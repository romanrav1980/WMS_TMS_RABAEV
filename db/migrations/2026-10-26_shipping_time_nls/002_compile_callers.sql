declare n number;begin
 select count(*)into n from USER_OBJECTS where OBJECT_NAME='RRL_TT_PLAN_SHIPPPING_HOUR'and OBJECT_TYPE='FUNCTION'and STATUS='INVALID';if n>0 then execute immediate 'alter function RRL_TT_PLAN_SHIPPPING_HOUR compile';end if;
 select count(*)into n from USER_OBJECTS where OBJECT_NAME='RRL_TT_REORDER_ADR'and OBJECT_TYPE='FUNCTION'and STATUS='INVALID';if n>0 then execute immediate 'alter function RRL_TT_REORDER_ADR compile';end if;
 select count(*)into n from USER_OBJECTS where OBJECT_NAME='RRL_ST_DEFER_API'and OBJECT_TYPE='PACKAGE BODY'and STATUS='INVALID';if n>0 then execute immediate 'alter package RRL_ST_DEFER_API compile body';end if;
 select count(*)into n from USER_OBJECTS where OBJECT_NAME='RRL_TRANSPORT_PLAN_API'and OBJECT_TYPE='PACKAGE BODY'and STATUS='INVALID';if n>0 then execute immediate 'alter package RRL_TRANSPORT_PLAN_API compile body';end if;
 select count(*)into n from USER_OBJECTS where OBJECT_NAME='TRANSPORT_TASK'and OBJECT_TYPE='PACKAGE BODY'and STATUS='INVALID';if n>0 then execute immediate 'alter package TRANSPORT_TASK compile body';end if;
end;
/
