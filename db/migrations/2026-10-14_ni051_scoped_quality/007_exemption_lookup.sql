declare n number;begin
 select count(*) into n from USER_INDEXES where INDEX_NAME='RRL_QC_EXEMPT_DOCUMENT_IX';
 if n=0 then execute immediate 'create index RRL_QC_EXEMPT_DOCUMENT_IX on RRL_QC_EXEMPT_FACT(DOCUMENT_ID)';end if;
end;
/
