declare a clob;n number;begin
 dbms_lob.createtemporary(a,true);
 for s in(select TEXT from USER_SOURCE where NAME='RRL_WH_WEIGH_REQUEST_API'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(s.TEXT,chr(13),''));end loop;
 if rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='6CBAE75B943EB8BE58D8EEA6E3E682EDBE28A5655CDD4225292F0853C35ADE89'then raise_application_error(-20886,'WH_ZERO_EXACT_SOURCE_RRL_WH_WEIGH_REQUEST_API');end if;
 dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for s in(select TEXT from USER_SOURCE where NAME='RRL_WH_WEIGH_REQUEST_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(s.TEXT,chr(13),''));end loop;
 if rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='1D64EC22FA49A7FB7C39E10FFEC9CB5B9C0D24AE54E1E329B43A0FB9F3A7D368'then raise_application_error(-20886,'WH_ZERO_EXACT_SOURCE_RRL_WH_WEIGH_REQUEST_API');end if;
 dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for s in(select TEXT from USER_SOURCE where NAME='RRL_WH_SCALE_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(s.TEXT,chr(13),''));end loop;
 if rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='AACBA7EF3C676C11664CE1CB9A394052B91EE0B7D487BAEED1780C1D969A7269'then raise_application_error(-20886,'WH_ZERO_EXACT_SOURCE_RRL_WH_SCALE_API');end if;
 dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for s in(select TEXT from USER_SOURCE where NAME='RRL_ASSEMBLY_SCALE_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(s.TEXT,chr(13),''));end loop;
 if rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='3959831FE6663ECA0049CAED70ED6FE0C00570B61732A491CD0BA55A03774159'then raise_application_error(-20886,'WH_ZERO_EXACT_SOURCE_RRL_ASSEMBLY_SCALE_API');end if;
 dbms_lob.freetemporary(a);
end;
/
declare n number;begin select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_WH_WEIGH_ZERO','RRL_WH_WEIGH_ZERO_GUARD')or STATUS='INVALID';if n!=0 then raise_application_error(-20886,'WH_ZERO_ROLLBACK_OBJECTS_OR_INVALID');end if;end;
/
