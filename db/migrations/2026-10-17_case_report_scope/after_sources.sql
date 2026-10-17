declare a clob;begin
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_CASE_REPORT_SCOPE'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='8851BCBA50CB77D554BD60314B83A80DA0B5C74D88456938C821692D8C6D3042'then raise_application_error(-20886,'SOURCE_GUARD_RRL_CASE_REPORT_SCOPE');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_CASE_REPORT_SCOPE'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='61D7B05F1A7755A517F3195FEAAB4892235B049EEF6EB387CF1A43B6C1C4400E'then raise_application_error(-20886,'SOURCE_GUARD_RRL_CASE_REPORT_SCOPE');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_CASE_RESOURCE_POLICY'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='8C5C471BC0CDE948F9E3D442BE7D00CF69D02198D80DA6208350E46D7736BD7A'then raise_application_error(-20886,'SOURCE_GUARD_RRL_CASE_RESOURCE_POLICY');end if;dbms_lob.freetemporary(a);
end;
/
