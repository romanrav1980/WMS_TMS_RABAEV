declare
begin
 for pass_no in 1..3 loop
  for p in(select OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where STATUS='INVALID'and OBJECT_TYPE in('PACKAGE','PACKAGE BODY')order by case OBJECT_TYPE when 'PACKAGE'then 0 else 1 end,OBJECT_NAME)loop
   execute immediate 'alter package '||dbms_assert.simple_sql_name(p.OBJECT_NAME)||' compile '||case p.OBJECT_TYPE when 'PACKAGE'then 'specification'else 'body'end;
  end loop;
 end loop;
end;
/
