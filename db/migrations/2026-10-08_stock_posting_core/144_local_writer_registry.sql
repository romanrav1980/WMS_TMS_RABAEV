declare s varchar2(20);begin select STATE into s from RRL_STOCK_RELEASE where RELEASE_ID=1;if s!='PREPARED' then raise_application_error(-20808,'REGISTRY_REQUIRES_PREPARED');end if;end;
/

update RRL_STOCK_WRITER_REGISTRY set STATE='ADAPTED',SOURCE_HASH='288cd577e8260e7bed4f41be738f340fac348ef5f1a43174a5abc6b84deed663',ADAPTER_REFERENCE='api/wms_api_server/app/modules/inventory/infrastructure/task_completion.py',UPDATED_AT=systimestamp where WRITER_KEY='LOCAL:api/wms_api_server/app/modules/inventory/infrastructure/task_stock_move.py';
update RRL_STOCK_WRITER_REGISTRY set STATE='ADAPTED',SOURCE_HASH='ae6dec762c2f014ab321705c2a1b5b6ef9bb5c0b51bcb832810c294b8c7bc9fd',ADAPTER_REFERENCE='api/wms_api_server/app/modules/inventory/infrastructure/task_completion.py',UPDATED_AT=systimestamp where WRITER_KEY='LOCAL:api/wms_api_server/app/modules/inventory/infrastructure/task_reservation.py';
update RRL_STOCK_WRITER_REGISTRY set STATE='ADAPTED',SOURCE_HASH='c16599b001cb9f37feef1d7c400d5e5c46f6d3b2de3ff99670e15569e3ce7a46',ADAPTER_REFERENCE='api/wms_api_server/app/modules/inventory/infrastructure/task_completion.py',UPDATED_AT=systimestamp where WRITER_KEY='LOCAL:api/wms_api_server/app/services/warehouse_task_domain_sync_service.py';
update RRL_STOCK_WRITER_REGISTRY set STATE='ADAPTED',SOURCE_HASH='f0258bbeedef8d294db2fcfad43612ddb0f1cb0ee0da93a7dfb6b5c92efc48c6',ADAPTER_REFERENCE='api/wms_api_server/app/modules/inventory/infrastructure/reservation_commands.py',UPDATED_AT=systimestamp where WRITER_KEY='LOCAL:api/wms_api_server/app/services/stock_reservation_service.py';
commit;
