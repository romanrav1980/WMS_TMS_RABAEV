begin execute immediate 'create index RRL_IW_GROUP_DISPATCH_REC_IX on RRL_IW_GROUP_DISPATCH(RECEIPT_OPERATION_ID,OPERATION_ID)';exception when others then if sqlcode!=-955 then raise;end if;end;
/
