declare a clob;begin
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_PALLET_QC_CMD'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='D078ADDE87BC320924ECC99F64AC81CF56EDA6A4756A1459D0B0AD634E9DD35E'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_PALLET_QC_CMD');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_QC_GATE'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='43802690FCE635C2DDE8A4927894E888EFCF4E7D55B79901A81B78B72D87A3A9'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_QC_GATE');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_WH_FINAL_SCALE_ADMISSION'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='B9A9872C98D91647CB797E970CDEFE952889F7FF7ECE06A52D30647F59CAB357'then raise_application_error(-20886,'SOURCE_GUARD_RRL_WH_FINAL_SCALE_ADMISSION');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_WH_FINAL_SCALE_ADMISSION'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='26699E1022101CBA6E4D78F4893B77A6B167DB010F70C496ABC188D46ECEB217'then raise_application_error(-20886,'SOURCE_GUARD_RRL_WH_FINAL_SCALE_ADMISSION');end if;dbms_lob.freetemporary(a);
end;
/
