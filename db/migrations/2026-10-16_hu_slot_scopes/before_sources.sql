declare a clob;begin
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_HU_EXEC_ACCESS'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='93A63640F727EEC0E9654C635E5026BEB9863EA56450E740716C613FCFBAD894'then raise_application_error(-20886,'SOURCE_GUARD_RRL_HU_EXEC_ACCESS');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_HU_REPACK_CMD'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='7517CFBA80E9382069F891095357BE1B55C7BAEBBECF4771BE74CBB8155F2EF1'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_HU_REPACK_CMD');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_HU_SLOT_MOVE_CMD'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='AD4BF68F7174EAD2A4EE8402A2F70679E36CDCC7152C4B6087FF6B43CAF93E77'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_HU_SLOT_MOVE_CMD');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_HU_UNPACK_CMD'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='A2760E9DFD8032BA0D6528B671B1C5241B80B287135920D38E30EE4F2F473D35'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_HU_UNPACK_CMD');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_POSTING_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='EF1D280344D259E6280C1640002C760801E1975EE1A0DD85AFF2CE19D7CAEE31'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_POSTING_API');end if;dbms_lob.freetemporary(a);
end;
/
