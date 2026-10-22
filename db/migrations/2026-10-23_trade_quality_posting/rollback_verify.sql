-- After rollback every shared owner is byte-identical to its captured before-version again.
declare s clob;n number;
 procedure same(p_name varchar2,p_type varchar2,p_hash varchar2)is begin
  dbms_lob.createtemporary(s,true);
  for r in(select TEXT from USER_SOURCE where NAME=p_name and TYPE=p_type order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
  if dbms_lob.getlength(s)=0 or rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>p_hash then raise_application_error(-20999,'ROLLBACK_SOURCE_MISMATCH:'||p_name||':'||p_type);end if;
  dbms_lob.freetemporary(s);
 end;
begin
 same('RRL_STOCK_EFFECT_CORE','PACKAGE','676C0FC9C13365B2906DC32A9111CF1A7C61C859DD2FC5ABBA98EF9304587BB7');
 same('RRL_STOCK_EFFECT_CORE','PACKAGE BODY','4A8461AC6B8CD97B55C37D3402522E65BFC07ECC42FBC8624DEC6B9546FC0B4D');
 same('RRL_STOCK_POSTING_API','PACKAGE BODY','51D467C081F4B2443FF8EBCBADE3559A31E0F6D79180E80BFE50AD472DD7F6AE');
 same('RRL_TRADE_STOCK_GUARD','PACKAGE BODY','AB52B7FCBE3A59ED7412030B4DC93D7282674FAE1F0A51AE80C9A7AB5963667F');
 same('RRL_REGULATORY_STOCK_OUTBOX','PACKAGE BODY','43E3E02E0666705D3C3AB31E6119F940BD2F8F2AC2E035C0FB5680CF53F3D369');
 same('RRL_TRADE_QUALITY_CASE_API','PACKAGE','1F32E751412C08DFC1FF00E616C524164CAFDBB583085C76F77F419F079BB0DA');
 same('RRL_TRADE_QUALITY_CASE_API','PACKAGE BODY','D928F1F1311E65559B62B272A31660D35CDEEBDE03D94321A4CC4F029D505809');
 select count(*)into n from USER_OBJECTS where OBJECT_NAME='RRL_STOCK_QUALITY_WRITEOFF';if n<>0 then raise_application_error(-20999,'QUALITY_WRITEOFF_REMAINS');end if;
 select count(*)into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_TRADE_QUALITY_CASE'and COLUMN_NAME='POST_OPERATION_ID';if n<>0 then raise_application_error(-20999,'QUALITY_POSTING_COLUMNS_REMAIN');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;
end;
/
