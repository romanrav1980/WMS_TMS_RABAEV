declare s varchar2(20);begin select STATE into s from RRL_STOCK_RELEASE where RELEASE_ID=1;
if s!='PREPARED' then raise_application_error(-20808,'REGISTRY_REQUIRES_PREPARED');end if;end;
/
update RRL_STOCK_WRITER_REGISTRY set STATE='ADAPTED',SOURCE_HASH='80f5bb0c6fd5f08483e82ab82783b39beb25422c905da1d6f6633e4acc548970',ADAPTER_REFERENCE='StockCommandIntent;inventory-count.html;native Oracle adapters',UPDATED_AT=systimestamp where WRITER_KEY='LOCAL:WindowsApplication2/WindowsApplication2/Form1.cs';
update RRL_STOCK_WRITER_REGISTRY set STATE='ADAPTED',SOURCE_HASH='255d3fe465563dcf3347d821aea7a8b8e159de9adc0d8977264fd63634e51550',ADAPTER_REFERENCE='task_completion.py;wave_commands.py;case_pick_commands.py',UPDATED_AT=systimestamp where WRITER_KEY='LOCAL:api/wms_api_server/app/services/picking_service.py';
commit;
