whenever sqlerror exit failure rollback
declare begin if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;end;
/
declare s varchar2(4000);st varchar2(20);v varchar2(20);n number;begin select SEARCH_CONDITION_VC,STATUS,VALIDATED into s,st,v from USER_CONSTRAINTS where TABLE_NAME='RRL_PALLET_TYPE'and CONSTRAINT_NAME='RRL_PALLET_TYPE_CHK1';if regexp_replace(upper(s),'[[:space:]]','')!=regexp_replace(upper(q'~LOAD_UNIT_CLASS in ('PALLET', 'TROLLEY', 'CONTAINER')~'),'[[:space:]]','')or st!='ENABLED'or v!='VALIDATED'then raise_application_error(-20999,'CLASS_CONSTRAINT_DRIFT');end if;select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;end;
/
declare s clob;begin dbms_lob.createtemporary(s,true);for r in(select TEXT from USER_SOURCE where NAME='RRL_PALLET_TYPE_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;if rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))!='71383280802D45D8EE0F2A51EC877E95B5921295687E06054B1B13CA8BEBD1A6'then raise_application_error(-20999,'TYPE_API_DRIFT');end if;dbms_lob.freetemporary(s);end;
/
