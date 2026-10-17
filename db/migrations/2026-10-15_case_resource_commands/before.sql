declare a clob;n number;begin
 dbms_lob.createtemporary(a,true);for s in(select TEXT from USER_SOURCE where NAME='RRL_CASE_TASK_ACCESS'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(s.TEXT,chr(13),''));end loop;
 if rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='5D935C287E7D1CDB1D4D1664480724F01B8ACF610E8DC9D2E7F53E3DE339E30A'then raise_application_error(-20886,'CASE_RESOURCE_FRESH_SOURCE_MISMATCH');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);for s in(select TEXT from USER_SOURCE where NAME='RRL_CASE_TASK_ACCESS'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(s.TEXT,chr(13),''));end loop;
 if rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='4B5DC26CCF434FA78081D791B7E6A7A7214B8E9E9EE209C90875836C04986C33'then raise_application_error(-20886,'CASE_RESOURCE_FRESH_SOURCE_MISMATCH');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);for s in(select TEXT from USER_SOURCE where NAME='RRL_CASE_RESOURCE_POLICY'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(s.TEXT,chr(13),''));end loop;
 if rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='D7367AA1BAC23B38B6B8403A5270FA93BC36BC5F44B4398777B6212ECFD7BE25'then raise_application_error(-20886,'CASE_RESOURCE_FRESH_SOURCE_MISMATCH');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);for s in(select TEXT from USER_SOURCE where NAME='RRL_CASE_RESOURCE_POLICY'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(s.TEXT,chr(13),''));end loop;
 if rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='DCD22AFBE1E3B1CD342FF69BE24925AAA6F82F87DFD601849B29EFA3EBD2A01B'then raise_application_error(-20886,'CASE_RESOURCE_FRESH_SOURCE_MISMATCH');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);for s in(select TEXT from USER_SOURCE where NAME='RRL_CASE_START_TIME_GUARD'and TYPE='TRIGGER'order by LINE)loop dbms_lob.append(a,replace(s.TEXT,chr(13),''));end loop;
 if rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='B99C3C94BFE509B6C488BBB24FCDB233558D1B3BCEE7AF1811512813276C8C15'then raise_application_error(-20886,'CASE_RESOURCE_FRESH_SOURCE_MISMATCH');end if;dbms_lob.freetemporary(a);
 select count(*)into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_CASE_PICK_TASK'and COLUMN_NAME='ASSIGNMENT_VERSION';
 if n!=0 then raise_application_error(-20886,'CASE_RESOURCE_VERSION_COLUMN_EXISTS');end if;
 select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_CASE_ASSIGNMENT_API','RRL_CASE_RESOURCE_COMMAND','RRL_CASE_ASSIGN_VERSION_GUARD','RRL_CASE_RESOURCE_CMD_GUARD');
 if n!=0 then raise_application_error(-20886,'CASE_RESOURCE_NAMESPACE_EXISTS');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'CASE_RESOURCE_INVALID_BEFORE');end if;
end;
/
