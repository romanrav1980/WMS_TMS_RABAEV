declare s clob;n number;begin
if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl'then raise_application_error(-20999,'WRONG_TARGET');end if;
dbms_lob.createtemporary(s,true);
for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_METADATA_TX'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
if rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>'27164981B1A216F58B8F489DB70810E86124FB5FA5169D014CF8E6C120039FB0'then raise_application_error(-20999,'DEPOT_SCOPE_SOURCE_DRIFT');end if;
dbms_lob.freetemporary(s);
dbms_lob.createtemporary(s,true);
for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_METADATA_TX'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
if rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>'0C74EE21BF51C0A22B5784D1C472DCB851938BA024E9F490BCB3BDAA8AB4D049'then raise_application_error(-20999,'DEPOT_SCOPE_SOURCE_DRIFT');end if;
dbms_lob.freetemporary(s);
dbms_lob.createtemporary(s,true);
for r in(select TEXT from USER_SOURCE where NAME='RRL_WARE_DEPOT_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
if rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>'BEF1284CA7B1AAD88E4909F2DAD9EE0CA01C3C953D51DA605BD3EC55C6F283E2'then raise_application_error(-20999,'DEPOT_SCOPE_SOURCE_DRIFT');end if;
dbms_lob.freetemporary(s);
select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;
end;
/
