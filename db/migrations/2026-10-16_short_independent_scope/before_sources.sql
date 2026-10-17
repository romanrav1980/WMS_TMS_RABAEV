declare a clob;begin
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_ACCESS_API'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='5F23AB1317A104445205EFFA27E3960CA0ADDDF96BF1A1A9D055DC4109B7AEE8'then raise_application_error(-20886,'SOURCE_GUARD_RRL_ACCESS_API');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_ACCESS_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='4142C392E38DEDA38585C65073DBA7D83C6125FAACD2F378B656F7AA810F9604'then raise_application_error(-20886,'SOURCE_GUARD_RRL_ACCESS_API');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_CASE_TASK_ACCESS'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='3DF7FBF17E7FC808F991F08B4D4D1D6BAC623AC86893F106869221B3F30E4B8C'then raise_application_error(-20886,'SOURCE_GUARD_RRL_CASE_TASK_ACCESS');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_CASE_TASK_ACCESS'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='128ABB62DA15C0365457F97B4657CB2E2D3FB02AF898295967334829E79EF22A'then raise_application_error(-20886,'SOURCE_GUARD_RRL_CASE_TASK_ACCESS');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_CASE_SHORT_CMD'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='201810CAF9A0A9EBDD13576BEBA06C399F9AD1B5A45E3D61477508C1EA79D7DE'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_CASE_SHORT_CMD');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_CASE_SHORT_CMD'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='340F25C14002D76D5C6ED0C433CEC62FE3F5912856990AA5DBAF6DA5247D255D'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_CASE_SHORT_CMD');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_POSTING_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='AE731B15DF41BB6895279D8AB7DAD5324EC771218B089C70CDBC1A8B2F085754'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_POSTING_API');end if;dbms_lob.freetemporary(a);
end;
/
