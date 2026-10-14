begin execute immediate 'create index RRL_STORE_RETURN_STORE_IDX on RRL_STORE_RETURN_TRANSPORT(STORE_ADDR,TT_ID,PLANNED_AT,OPERATION_ID)';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate 'create index RRL_STORE_RETURN_DRIVER_IDX on RRL_STORE_RETURN_TRANSPORT(DRIVER_ID,TT_ID,OPERATION_ID)';exception when others then if sqlcode!=-955 then raise;end if;end;
/
