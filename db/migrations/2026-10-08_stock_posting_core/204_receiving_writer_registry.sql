declare s varchar2(20);begin select STATE into s from RRL_STOCK_RELEASE where RELEASE_ID=1;
if s!='PREPARED' then raise_application_error(-20808,'REGISTRY_REQUIRES_PREPARED');end if;end;
/
update RRL_STOCK_WRITER_REGISTRY set STATE='ADAPTED',SOURCE_HASH='9edeef2322d828bde4b7724837f26f34f5f2a31445060d6913a0a058a280043a',
 ADAPTER_REFERENCE='api/wms_api_server/app/modules/inventory/infrastructure/receipt_commands.py;task_completion.py',
 UPDATED_AT=systimestamp
 where WRITER_KEY='LOCAL:api/wms_api_server/app/modules/inventory/infrastructure/receiving.py';
commit;
