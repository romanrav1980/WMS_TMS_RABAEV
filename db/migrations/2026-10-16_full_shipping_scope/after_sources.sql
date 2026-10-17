declare a clob;begin
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_FULL_SHIPPING_SCOPE'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='4E84A63314FBDBD19217B2E2F493DC350FDB3E6A9FE40E54708AE0844676188F'then raise_application_error(-20886,'SOURCE_GUARD_RRL_FULL_SHIPPING_SCOPE');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_FULL_SHIPPING_SCOPE'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='CE310A9F13078390F2362B7F1FEBE3475BAB45314EDA09E967A728B15BC91DDF'then raise_application_error(-20886,'SOURCE_GUARD_RRL_FULL_SHIPPING_SCOPE');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_HU_SHIP_CMD'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='ED379E233FC4E5984311566918049912031B375FFBA366463596CD1FF9EFE01E'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_HU_SHIP_CMD');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_LOADING_READ'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='659391AEB924F448FE5FFB45D2A7058186F76B5D0C06233612E3FD8492CEFC2C'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_LOADING_READ');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_POSTING_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='D85B5FCABC365BEAFE91A06F03B6ACBF9E8BB681B42551C5C72E40047B89474A'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_POSTING_API');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_SHIPPING_CORE'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='A337A38767F9146132100B3D325A796498890707864D812E98C16BD0716446EB'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_SHIPPING_CORE');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_SINGLE_LOAD_CMD'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='D46F4E78881BB80F4DB326E6ADCC46D423DB7E57B39C1DBB5DDA9818D4F695F7'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_SINGLE_LOAD_CMD');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_TRIP_DEPART_CMD'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='FDF4067129E4B4B466F9C95FF73ADE421431018D70CC6DE4E1AA95A046FE6A19'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_TRIP_DEPART_CMD');end if;dbms_lob.freetemporary(a);
end;
/
