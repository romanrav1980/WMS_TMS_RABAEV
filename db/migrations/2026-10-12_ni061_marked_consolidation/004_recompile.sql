declare n number;begin
 for attempt in 1..5 loop
 for item in(select OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where STATUS='INVALID'and OBJECT_NAME not like 'BIN$%'and OBJECT_TYPE in('PACKAGE','PACKAGE BODY','TRIGGER','FUNCTION','PROCEDURE','VIEW'))loop
 begin
 if item.OBJECT_TYPE='PACKAGE BODY'then execute immediate 'alter package '||dbms_assert.simple_sql_name(item.OBJECT_NAME)||' compile body';
 elsif item.OBJECT_TYPE='PACKAGE'then execute immediate 'alter package '||dbms_assert.simple_sql_name(item.OBJECT_NAME)||' compile specification';
 else execute immediate 'alter '||item.OBJECT_TYPE||' '||dbms_assert.simple_sql_name(item.OBJECT_NAME)||' compile';end if;
 exception when others then null;end;
 end loop;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID'and OBJECT_NAME not like 'BIN$%';exit when n=0;
 end loop;
 if n!=0 then raise_application_error(-20899,'NESTED_RECEIVING_INVALID_OBJECTS');end if;
end;
/
