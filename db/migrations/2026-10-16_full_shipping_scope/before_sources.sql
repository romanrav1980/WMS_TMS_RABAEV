declare a clob;begin
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_HU_SHIP_CMD'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='F920997DD5DF1D785374F0046C5BC4C6049EC89B417E63C1D73BCD502654D6BD'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_HU_SHIP_CMD');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_LOADING_READ'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='659391AEB924F448FE5FFB45D2A7058186F76B5D0C06233612E3FD8492CEFC2C'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_LOADING_READ');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_POSTING_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='48E72FF66CE1B008733327D41EED7784BC46AA88B75D86E56B2613569941E126'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_POSTING_API');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_SHIPPING_CORE'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='A2764F611192C0E5C3D005005398C7BDC4162F5507DC1D4A7DEF018D67D3E737'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_SHIPPING_CORE');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_SINGLE_LOAD_CMD'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='D46F4E78881BB80F4DB326E6ADCC46D423DB7E57B39C1DBB5DDA9818D4F695F7'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_SINGLE_LOAD_CMD');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_TRIP_DEPART_CMD'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='B8EDC2FC83B3E9517E63FB1E429EB823A0BC6C5040F2836778B148FBF2DD7608'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_TRIP_DEPART_CMD');end if;dbms_lob.freetemporary(a);
end;
/
