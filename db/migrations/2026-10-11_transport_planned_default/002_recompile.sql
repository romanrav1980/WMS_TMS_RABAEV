alter package RRL_TARE_PARTICIPANT compile specification;
/
declare
begin
 for pass_no in 1..3 loop
  for p in(select OBJECT_NAME from USER_OBJECTS where STATUS='INVALID'and OBJECT_TYPE='PACKAGE BODY'order by OBJECT_NAME)loop
   execute immediate 'alter package '||dbms_assert.simple_sql_name(p.OBJECT_NAME)||' compile body';
  end loop;
 end loop;
end;
/
