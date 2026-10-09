declare s varchar2(20);begin select STATE into s from RRL_STOCK_RELEASE where RELEASE_ID=1;if s!='PREPARED' then raise_application_error(-20808,'REGISTRY_REQUIRES_PREPARED');end if;end;
/
update RRL_STOCK_WRITER_REGISTRY set STATE='UNCONVERTED',SOURCE_HASH='b4cae943ab1cb72dc26e21494ce31dbc0b0c05d817dc885227e06fd5e646f37e',ADAPTER_REFERENCE=null,UPDATED_AT=systimestamp where WRITER_KEY='LOCAL:api/wms_api_server/app/modules/inventory/infrastructure/receiving.py';
commit;
