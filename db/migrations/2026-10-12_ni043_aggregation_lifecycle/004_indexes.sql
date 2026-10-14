begin execute immediate 'create index RRL_TRACE_USE_UID_IX on RRL_TRACE_MANIFEST_USE(UID_PALLET)';exception when others then if sqlcode not in(-955,-1408)then raise;end if;end;
/
begin execute immediate 'create index RRL_TRACE_AGG_BLOCK_OP_IX on RRL_TRACE_AGG_BLOCK(INVALIDATION_OPERATION_ID)';exception when others then if sqlcode not in(-955,-1408)then raise;end if;end;
/
