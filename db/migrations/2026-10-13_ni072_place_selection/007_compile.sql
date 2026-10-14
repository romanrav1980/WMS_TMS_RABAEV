begin
 for x in(select OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where STATUS='INVALID'and OBJECT_NAME not like 'BIN$%'and OBJECT_TYPE in('PACKAGE','PACKAGE BODY','TRIGGER'))loop
  begin execute immediate 'alter '||case when x.OBJECT_TYPE='PACKAGE BODY'then 'package'else lower(x.OBJECT_TYPE)end||' '||x.OBJECT_NAME||' compile'||case when x.OBJECT_TYPE='PACKAGE BODY'then ' body'else ''end;exception when others then null;end;
 end loop;
end;
/
