declare s clob;n number;begin
if user<>'RABAEV'or sys_context('USERENV','SERVICE_NAME')<>'orcl'then raise_application_error(-20999,'WRONG_TARGET');end if;
dbms_lob.createtemporary(s,true);
for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_METADATA_TX'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
if rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>'760B46639107BAC50A07AB3522FBA3E6417A628C44B0B885419E3E52A9BB5136'then raise_application_error(-20999,'DEPOT_SCOPE_SOURCE_DRIFT');end if;
dbms_lob.freetemporary(s);
dbms_lob.createtemporary(s,true);
for r in(select TEXT from USER_SOURCE where NAME='RRL_WARE_DEPOT_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
if rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>'B58D669744EB6908BAF48A0A536ECAE4665612274EB2DED4971E8465498A0C08'then raise_application_error(-20999,'DEPOT_SCOPE_SOURCE_DRIFT');end if;
dbms_lob.freetemporary(s);
select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;
end;
/
