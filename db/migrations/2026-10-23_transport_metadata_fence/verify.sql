declare s clob;n number;procedure same(t varchar2,h varchar2)is begin dbms_lob.createtemporary(s,true);for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_METADATA_TX'and TYPE=t order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;if rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>h then raise_application_error(-20999,'TRANSPORT_METADATA_SOURCE_MISMATCH:'||t);end if;end;begin
 if user<>'RABAEV'or sys_context('USERENV','SERVICE_NAME')<>'orcl'then raise_application_error(-20999,'WRONG_TARGET');end if;
same('PACKAGE','99751329FC37C1DC722ABAC65761BF5B7912234213DD75C3A85A456062471D5C');
same('PACKAGE BODY','0AF674340F3C89C27AE61A7EED81D5A900F5B4C4CF2AF7513214DC494C23133B');
select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;end;
/
