declare n number;v_open boolean:=false;begin
 RRL_STOCK_CONFIG_API.begin_change('admin','warehouse_settings_edit');v_open:=true;
 select count(*)into n from RIGHTS where USER_GROUP='SAP_GATEWAY'and RIGHT1='sap_store_decision_import';
 if n=0 then insert into RIGHTS(USER_GROUP,RIGHT1)values('SAP_GATEWAY','sap_store_decision_import');end if;
 RRL_STOCK_CONFIG_API.end_change;v_open:=false;commit;
exception when others then if v_open then rollback;RRL_STOCK_CONFIG_API.end_change;end if;raise;end;
/
