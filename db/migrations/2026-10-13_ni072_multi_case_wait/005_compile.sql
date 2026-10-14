begin
 for x in(select OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where STATUS='INVALID'and OBJECT_TYPE in('PACKAGE','PACKAGE BODY','TRIGGER','PROCEDURE','FUNCTION','VIEW')and OBJECT_NAME not like 'BIN$%')loop
  begin execute immediate 'alter '||case when x.OBJECT_TYPE='PACKAGE BODY'then'package'else lower(x.OBJECT_TYPE)end||' '||dbms_assert.simple_sql_name(x.OBJECT_NAME)||' compile'||case when x.OBJECT_TYPE='PACKAGE BODY'then' body'else''end;exception when others then null;end;
 end loop;
end;
/
