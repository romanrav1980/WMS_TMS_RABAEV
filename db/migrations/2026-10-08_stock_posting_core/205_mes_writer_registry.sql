declare s varchar2(20);begin select STATE into s from RRL_STOCK_RELEASE where RELEASE_ID=1;
if s!='PREPARED' then raise_application_error(-20808,'REGISTRY_REQUIRES_PREPARED');end if;end;
/
update RRL_STOCK_WRITER_REGISTRY set STATE='ADAPTED',SOURCE_HASH='8c7cd94cdf1876f3d1460ec4b23370860b688e0c04979d7011927309f51dbc7b',
 ADAPTER_REFERENCE='api/wms_api_server/app/modules/inventory/infrastructure/mes_commands.py;mes_task_commands.py;mes_supply_commands.py',
 UPDATED_AT=systimestamp where WRITER_KEY='LOCAL:api/wms_api_server/app/services/mes_service.py';
commit;
