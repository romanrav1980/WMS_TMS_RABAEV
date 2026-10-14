-- Restore source_scope265 package/checkpointapp first. Preserve allbusiness history/archive.
declare v_meta boolean:=false;begin
 RRL_STOCK_CONFIG_API.begin_change('admin','warehouse_settings_edit');v_meta:=true;
 update RUSERS set DELETED=1 where ID='SAP_FILE_GATEWAY'and USER_GROUP='SAP_GATEWAY';
 RRL_STOCK_CONFIG_API.end_change;v_meta:=false;commit;
exception when others then if v_meta then rollback;RRL_STOCK_CONFIG_API.end_change;end if;raise;end;
/
@@../2026-10-11_ni022_source_scope/001_api.sql
