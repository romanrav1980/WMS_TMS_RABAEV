declare n number;v_group varchar2(15);v_meta boolean:=false;
begin
 RRL_STOCK_CONFIG_API.begin_change('admin','warehouse_settings_edit');v_meta:=true;savepoint RRL_SAP_GATE266;
 select count(*)into n from RUSERS where ID='SAP_FILE_GATEWAY';
 if n=0 then
  insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)
   values('SAP_FILE_GATEWAY',lower(rawtohex(sys.dbms_crypto.randombytes(16))),'Local SAP XML gateway','SAP_GATEWAY',null,0,0);
 else
  select USER_GROUP into v_group from RUSERS where ID='SAP_FILE_GATEWAY';
  if v_group!='SAP_GATEWAY'or v_group is null then raise_application_error(-20863,'SAP_GATEWAY_EXISTING_ACCOUNT_REQUIRES_REVIEW');end if;
 end if;
 for role in(select 'sap_article_import'RIGHT1 from dual union all select 'sap_supply_import'from dual
   union all select 'sap_store_order_import'from dual union all select 'sap_store_all_ware'from dual)loop
  select count(*)into n from RIGHTS where USER_GROUP='SAP_GATEWAY'and RIGHT1=role.RIGHT1;
  if n=0 then insert into RIGHTS(USER_GROUP,RIGHT1)values('SAP_GATEWAY',role.RIGHT1);end if;
 end loop;
 RRL_STOCK_CONFIG_API.end_change;v_meta:=false;commit;
exception when others then
 if v_meta then rollback to RRL_SAP_GATE266;RRL_STOCK_CONFIG_API.end_change;end if;raise;
end;
/
