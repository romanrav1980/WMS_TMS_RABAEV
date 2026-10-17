declare a clob;begin
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_WH_WEIGH_REQUEST_API'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='6056CF3B8CE3FE3F71BCA1CB0C030F3AD73C834A78C911B6CF6201E7A20CE3E8'then raise_application_error(-20886,'WH_EMPTY_SOURCE:RRL_WH_WEIGH_REQUEST_API:PACKAGE');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_WH_WEIGH_REQUEST_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='B21176B5ED0F8B82EB316E1CE276106BCA35170C4F1EE9BAFA2E980B846CBC4E'then raise_application_error(-20886,'WH_EMPTY_SOURCE:RRL_WH_WEIGH_REQUEST_API:PACKAGE BODY');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_CASE_RESOURCE_POLICY'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='D7367AA1BAC23B38B6B8403A5270FA93BC36BC5F44B4398777B6212ECFD7BE25'then raise_application_error(-20886,'WH_EMPTY_SOURCE:RRL_CASE_RESOURCE_POLICY:PACKAGE');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_CASE_RESOURCE_POLICY'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='091A694D638E09257E47104D782BB95F9D8FBC4D10FD6F1181E252683C2F2580'then raise_application_error(-20886,'WH_EMPTY_SOURCE:RRL_CASE_RESOURCE_POLICY:PACKAGE BODY');end if;dbms_lob.freetemporary(a);
end;
/
