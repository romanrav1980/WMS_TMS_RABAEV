create or replace function RRL_SET_SCAN_PROOVE(PALLET_UID1 varchar2  ,
    count_of_errors1 int ,
    prim1 varchar2,p_operation_id varchar2 default null,p_actor varchar2 default null) return int authid definer is
 state varchar2(20);
begin
 select STATE into state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if state='PREPARED' then return RRL_SET_SCAN_PROOVE_SP_OLD(PALLET_UID1,count_of_errors1,prim1);end if;
 if state!='ACTIVE' then raise_application_error(-20885,'STOCK_RELEASE_NOT_ACTIVE');end if;
 return RRL_STOCK_QUALITY_ENTRY.scan(PALLET_UID1,count_of_errors1,prim1,null,p_actor,p_operation_id);

end;
/

create or replace function RRL_SET_SCAN_PROOVE2(PALLET_UID1 varchar2  ,
    count_of_errors1 int ,
    prim1 varchar2 , 
    SBORSHIK1  VARCHAR2,
    KLADOVSHIK1 VARCHAR2,p_operation_id varchar2 default null,p_actor varchar2 default null) return int authid definer is
 state varchar2(20);
begin
 select STATE into state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if state='PREPARED' then return RRL_SET_SCAN_PROOVE2_SP_OLD(PALLET_UID1,count_of_errors1,prim1,SBORSHIK1,KLADOVSHIK1);end if;
 if state!='ACTIVE' then raise_application_error(-20885,'STOCK_RELEASE_NOT_ACTIVE');end if;
 return RRL_STOCK_QUALITY_ENTRY.scan(PALLET_UID1,count_of_errors1,prim1,SBORSHIK1,nvl(p_actor,nvl(KLADOVSHIK1,SBORSHIK1)),p_operation_id);

end;
/

create or replace function RRL_TRIAL_BY_WEIGHT(PALLET_UID1  varchar2 ,
    TRIAL_WEIGHT1 varchar2 ,
    WOOD_WEIGHT1 varchar2 ,
    user_id1 varchar2,p_operation_id varchar2 default null) return int authid definer is
 state varchar2(20);
begin
 select STATE into state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if state='PREPARED' then return RRL_TRIAL_BY_WEIGHT_SP_OLD(PALLET_UID1,TRIAL_WEIGHT1,WOOD_WEIGHT1,user_id1);end if;
 if state!='ACTIVE' then raise_application_error(-20885,'STOCK_RELEASE_NOT_ACTIVE');end if;
 return RRL_STOCK_QUALITY_ENTRY.weight('WEIGHT',PALLET_UID1,TRIAL_WEIGHT1,WOOD_WEIGHT1,user_id1,p_operation_id);

end;
/

create or replace function RRL_TRIAL_BY_WEIGHT2(PALLET_UID1  varchar2 ,
    TRIAL_WEIGHT1 varchar2 ,
    WOOD_WEIGHT1 varchar2 ,
    user_id1 varchar2,p_operation_id varchar2 default null) return int authid definer is
 state varchar2(20);
begin
 select STATE into state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if state='PREPARED' then return RRL_TRIAL_BY_WEIGHT2_SP_OLD(PALLET_UID1,TRIAL_WEIGHT1,WOOD_WEIGHT1,user_id1);end if;
 if state!='ACTIVE' then raise_application_error(-20885,'STOCK_RELEASE_NOT_ACTIVE');end if;
 return RRL_STOCK_QUALITY_ENTRY.weight('WEIGHT2',PALLET_UID1,TRIAL_WEIGHT1,WOOD_WEIGHT1,user_id1,p_operation_id);

end;
/

create or replace function RRL_UPDATE_PALLET_ROW2(articul1 varchar2 ,
    pallet_uid1 varchar2 ,
    count1  number , 
    user_id1 varchar2) return varchar2 authid definer is
 state varchar2(20);result varchar2(1024);
begin
 select STATE into state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if state='PREPARED' then return RRL_UPDATE_PALLET_ROW2_SP_OLD(articul1,pallet_uid1,count1,user_id1);end if;
 if state!='ACTIVE' then raise_application_error(-20885,'STOCK_RELEASE_NOT_ACTIVE');end if;
 if dbms_transaction.local_transaction_id(false) is not null then raise_application_error(-20862,'PALLET_EDIT_REQUIRES_CLEAN_TRANSACTION');end if;
 RRL_STOCK_METADATA_TX.begin_change(user_id1,'outgoing_pallet_edit');
 savepoint RRL_PALLET_EDIT;
 result:=RRL_UPDATE_PALLET_ROW2_SP_CALC(articul1,pallet_uid1,count1,user_id1);
 if result!='ok' or result is null then rollback to RRL_PALLET_EDIT;
 else
  update RRL_SBORKA_PALLETS set PROOVED_BY_SCAN=0,PROOVED=0,KLADOVSHIK=user_id1 where PALLET_UID=pallet_uid1;
 end if;
 RRL_STOCK_METADATA_TX.end_change;return result;
exception when others then RRL_STOCK_METADATA_TX.end_change;raise;
end;
/

create or replace function RRL_UPDATE_PALLET_ROW3(row_id1 int ,
    articul1 varchar2 ,
    pallet_uid1 varchar2 , 
    PACK_COUNT2 number , 
    QUANTITY2 number , 
    CURRENT_MOD_ID2 int , 
    ORDER_WEIGHT2 number , 
    PRIHOD_PALLET_UID2 varchar2 ,
    user_id1 varchar2) return varchar2 authid definer is
 state varchar2(20);result varchar2(1024);
begin
 select STATE into state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if state='PREPARED' then return RRL_UPDATE_PALLET_ROW3_SP_OLD(row_id1,articul1,pallet_uid1,PACK_COUNT2,QUANTITY2,CURRENT_MOD_ID2,ORDER_WEIGHT2,PRIHOD_PALLET_UID2,user_id1);end if;
 if state!='ACTIVE' then raise_application_error(-20885,'STOCK_RELEASE_NOT_ACTIVE');end if;
 if dbms_transaction.local_transaction_id(false) is not null then raise_application_error(-20862,'PALLET_EDIT_REQUIRES_CLEAN_TRANSACTION');end if;
 RRL_STOCK_METADATA_TX.begin_change(user_id1,'outgoing_pallet_edit');
 savepoint RRL_PALLET_EDIT;
 result:=RRL_UPDATE_PALLET_ROW3_SP_CALC(row_id1,articul1,pallet_uid1,PACK_COUNT2,QUANTITY2,CURRENT_MOD_ID2,ORDER_WEIGHT2,PRIHOD_PALLET_UID2,user_id1);
 if result!='ok' or result is null then rollback to RRL_PALLET_EDIT;
 else
  update RRL_SBORKA_PALLETS set PROOVED_BY_SCAN=0,PROOVED=0,KLADOVSHIK=user_id1 where PALLET_UID=pallet_uid1;
 end if;
 RRL_STOCK_METADATA_TX.end_change;return result;
exception when others then RRL_STOCK_METADATA_TX.end_change;raise;
end;
/
