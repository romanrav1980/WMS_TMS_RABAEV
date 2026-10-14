-- Type capability only: each actual resource still requires explicit PUTAWAY qualification.
begin
 RRL_STOCK_METADATA_TX.begin_change('admin','warehouse_task_edit');
 update RRL_RESOURCE_TYPE set DEFAULT_TASK_TYPES=DEFAULT_TASK_TYPES||',PUTAWAY',UPDATED_AT=systimestamp
  where RESOURCE_TYPE in('REACHTRUCK','FORKLIFT') and ACTIVE=1
   and instr(','||replace(DEFAULT_TASK_TYPES,' ','')||',',',PUTAWAY,')=0;
 RRL_STOCK_METADATA_TX.end_change;
exception when others then RRL_STOCK_METADATA_TX.end_change;raise;
end;
/
commit;
/
