declare a clob;begin
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_DRIVER_SCOPE'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='6E05F8AED77DF0387C70DD68C36F8A6C27D0364BE49F5CF7310C55B9DEC4AEC8'then raise_application_error(-20886,'SOURCE_GUARD_RRL_DRIVER_SCOPE');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_DRIVER_SCOPE'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='26B618BD9D617299EA88D3C8150BC820AD8068BDFF2EA8A9B2106A0B176A3BF9'then raise_application_error(-20886,'SOURCE_GUARD_RRL_DRIVER_SCOPE');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_POSTING_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='E5199D7752C6B08CC0F11CA444D2D66526FFB6E932C9909D9C75CC9FF1C3681C'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_POSTING_API');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_STORE_RETURN_CUST_CMD'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='CB38863C3AC47CBA119DCAC31F105B98986BF19478EDD66B23AA8C5E08B0B0F1'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_STORE_RETURN_CUST_CMD');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_TRANSPORT_DRIVER_USER_GUARD'and TYPE='TRIGGER'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='347CABDDE3D4238E0238EFBB7630F15D9CD9157CEA12CD742B284B4C4B6DF538'then raise_application_error(-20886,'SOURCE_GUARD_RRL_TRANSPORT_DRIVER_USER_GUARD');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_TT_OPERATION_PLAN_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='7364432ED0997E9A9127B78CC819D273238CE2D325B6E8D7F83C860AAEB78FA1'then raise_application_error(-20886,'SOURCE_GUARD_RRL_TT_OPERATION_PLAN_API');end if;dbms_lob.freetemporary(a);
end;
/
