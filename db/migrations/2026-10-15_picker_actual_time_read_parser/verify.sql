declare n number;a clob;h varchar2(64);
 procedure check_source(p_type varchar2,p_hash varchar2)is begin
  dbms_lob.createtemporary(a,true);for r in(select TEXT from USER_SOURCE where NAME='RRL_PICKER_TIME_READ'and TYPE=p_type order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
  a:=rtrim(ltrim(a,chr(10)||chr(9)||' '),chr(10)||chr(9)||' ');h:=rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256));dbms_lob.freetemporary(a);
  if h is null or h!=p_hash then raise_application_error(-20886,'PICKER_TIME_READ_PARSER_SOURCE_DRIFT:'||p_type);end if;end;
begin
 check_source('PACKAGE','DD146D61195506D9E33029E048E2CDF85DB62F6940DA9FA5637173994C96BB95');check_source('PACKAGE BODY','9006A19AB62C2CFA1A872DA10D5DFF5E7C6E658EC83242CB3E01135AC40B5977');
 select count(*)into n from USER_OBJECTS where STATUS='INVALID'and OBJECT_NAME not like 'BIN$%';if n!=0 then raise_application_error(-20886,'PICKER_TIME_READ_PARSER_INVALID');end if;
 select count(*)into n from USER_ERRORS where NAME='RRL_PICKER_TIME_READ';if n!=0 then raise_application_error(-20886,'PICKER_TIME_READ_PARSER_ERRORS');end if;
 select (select count(*)from RRL_PICKER_TIME_STREAM)+(select count(*)from RRL_PICKER_TIME_EVENT)+(select count(*)from RRL_PICKER_TIME_SPAN)+(select count(*)from RRL_PICKER_TIME_COMMAND)into n from dual;
 if n!=17 then raise_application_error(-20886,'PICKER_TIME_READ_PARSER_HISTORY_DRIFT');end if;
 select count(*)into n from RRL_PICKER_TIME_STREAM where OPERATOR_ID='N1939.OP'and STREAM_VERSION=6 and SHIFT_STATE='OFF'and WORK_STATE='IDLE';
 if n!=1 then raise_application_error(-20886,'PICKER_TIME_READ_PARSER_STATE_DRIFT');end if;
 select count(*)into n from RRL_PICKER_TIME_EVENT where OPERATOR_ID='N1939.OP';if n!=6 then raise_application_error(-20886,'PICKER_TIME_READ_PARSER_EVENTS_DRIFT');end if;
 select count(*)into n from RRL_PICKER_TIME_SPAN where OPERATOR_ID='N1939.OP';if n!=3 then raise_application_error(-20886,'PICKER_TIME_READ_PARSER_SPANS_DRIFT');end if;
 select count(*)into n from RRL_PICKER_TIME_COMMAND where ACTOR_ID='N1939.OP';if n!=7 then raise_application_error(-20886,'PICKER_TIME_READ_PARSER_COMMANDS_DRIFT');end if;
end;
/
