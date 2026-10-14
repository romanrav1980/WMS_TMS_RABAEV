begin execute immediate 'create unique index RRL_LOG_EXP_DOC_UQ on RRL_LOGISTICS_EXPENSE(WARE_ID,ARTICLE_CODE,OBJECT_KIND,OBJECT_ID,CURRENCY,DOCUMENT_REFERENCE)';exception when others then if sqlcode!=-955 then raise;end if;end;
/
