create or replace package body RRL_STOCK_INTERWARE_CUSTODY as
 procedure assert_scope(p_receipt varchar2,p_actor varchar2)is n number;
 begin
  select count(*)into n from RRL_INTERWARE_RECEIPT r join RUSERS u on u.ID=p_actor where r.OPERATION_ID=p_receipt and nvl(u.DELETED,0)=0 and RRL_HAS_WRIGHT(u.ID,'interwarehouse_receive')=1 and(u.WARE_ID=r.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN');
  if n!=1 then raise_application_error(-20882,'INTERWARE_CURRENT_CUSTODY_ACTOR_REQUIRED');end if;
 end;
 procedure describe_source(p_receipt varchar2,p_actor varchar2,p_domain out json_object_t) is
 receipt RRL_INTERWARE_RECEIPT%rowtype;unloaded RRL_INTERWARE_UNLOAD%rowtype;cargo RRL_TT_HU_LOAD_FACT%rowtype;n number;
 begin
 select *into receipt from RRL_INTERWARE_RECEIPT where OPERATION_ID=p_receipt;select *into unloaded from RRL_INTERWARE_UNLOAD where OPERATION_ID=receipt.UNLOAD_OPERATION_ID;
 select *into cargo from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=receipt.SOURCE_LOAD_OPERATION_ID;
 select count(*)into n from RUSERS u where ID=p_actor and nvl(DELETED,0)=0 and(WARE_ID=receipt.WARE_ID or upper(trim(USER_GROUP))='GLOBAL_ADMIN')and RRL_HAS_WRIGHT(u.ID,'interwarehouse_receive')=1;
 if n!=1 then raise_application_error(-20882,'INTERWARE_CUSTODY_TARGET_ACTOR_REQUIRED');end if;
 if cargo.STATUS!='DEPARTED' or cargo.DEPARTURE_OPERATION_ID is null or cargo.DEPARTED_AT is null or cargo.CUSTODY_RELEASED_AT is not null or cargo.CUSTODY_RELEASE_OPERATION_ID is not null or cargo.ROOT_UID!=receipt.ROOT_UID or unloaded.ROOT_UID!=receipt.ROOT_UID or unloaded.PLAN_OPERATION_ID!=receipt.PLAN_OPERATION_ID or unloaded.WARE_ID!=receipt.WARE_ID then raise_application_error(-20886,'INTERWARE_CUSTODY_ORIGINAL_PROOF_REQUIRED');end if;
 select count(*)into n from RRL_STOCK_OPERATION where OPERATION_ID=receipt.OPERATION_ID and STATE='APPLIED'and COMMAND_TYPE='INTERWARE_RECEIVE';if n!=1 then raise_application_error(-20886,'INTERWARE_CUSTODY_APPLIED_RECEIPT_REQUIRED');end if;
 select count(*)into n from RRL_INTERWARE_CUSTODY_PROOF where RECEIPT_OPERATION_ID=p_receipt;if n!=0 then raise_application_error(-20886,'INTERWARE_CUSTODY_ALREADY_RELEASED');end if;
 p_domain:=json_object_t();p_domain.put('receipt_operation_id',p_receipt);p_domain.put('unload_operation_id',receipt.UNLOAD_OPERATION_ID);p_domain.put('source_load_operation_id',receipt.SOURCE_LOAD_OPERATION_ID);p_domain.put('uid',receipt.ROOT_UID);p_domain.put('warehouse_id',receipt.WARE_ID);
 p_domain.put('custody_released_at',to_char(unloaded.CREATED_AT,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'));p_domain.put('departure_operation_id',cargo.DEPARTURE_OPERATION_ID);
 exception when no_data_found then raise_application_error(-20886,'INTERWARE_CUSTODY_ACTUAL_RECEIPT_REQUIRED');
 end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
 d json_object_t:=json_object_t.parse(p_request);v json_object_t;f json_array_t:=json_array_t();r json_array_t:=json_array_t();
 begin
 describe_source(d.get_object('source').get_string('receipt_operation_id'),d.get_string('actor'),v);
 RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_INTERWARE_RECEIPT',v.get_string('receipt_operation_id'));
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_INTERWARE_UNLOAD',v.get_string('unload_operation_id'));
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TT_HU_LOAD_FACT',v.get_string('source_load_operation_id'));
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_INTERWARE_CUSTODY_PROOF',p_operation);
 RRL_STOCK_PLAN_HELPER.anchor(r,30,'HU',v.get_string('uid'));RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','TT.LOAD.HU:'||v.get_string('uid'));
 RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
 p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
 d json_object_t:=json_object_t.parse(p_request);op varchar2(100):=d.get_string('operation_id');resolved clob;v json_object_t;fresh json_object_t;j json_object_t:=json_object_t();
 v_receipt varchar2(100);v_load varchar2(100);v_unload varchar2(100);released_at timestamp with time zone;
 begin
 select RESOLVED_PLAN_JSON into resolved from RRL_STOCK_OPERATION where OPERATION_ID=op;v:=json_object_t.parse(resolved).get_object('domain');v_receipt:=v.get_string('receipt_operation_id');v_load:=v.get_string('source_load_operation_id');v_unload:=v.get_string('unload_operation_id');
 describe_source(v_receipt,p_actor,fresh);if dbms_lob.compare(v.to_clob,fresh.to_clob)!=0 then raise_application_error(-20886,'INTERWARE_CUSTODY_SOURCE_CHANGED');end if;
 select CREATED_AT into released_at from RRL_INTERWARE_UNLOAD where OPERATION_ID=v_unload;
 insert into RRL_INTERWARE_CUSTODY_PROOF(OPERATION_ID,RECEIPT_OPERATION_ID,SOURCE_LOAD_OPERATION_ID,ACTOR)values(op,v_receipt,v_load,p_actor);
 update RRL_TT_HU_LOAD_FACT set CUSTODY_RELEASED_AT=released_at,CUSTODY_RELEASE_OPERATION_ID=op where LOAD_OPERATION_ID=v_load and CUSTODY_RELEASED_AT is null and CUSTODY_RELEASE_OPERATION_ID is null;
 if sql%rowcount!=1 then raise_application_error(-20886,'INTERWARE_CUSTODY_COMPARE_SET_CONFLICT');end if;
 j.put('operation_id',op);j.put('receipt_operation_id',v_receipt);j.put('source_load_operation_id',v_load);j.put('pallet_identifier',v.get_string('uid'));j.put('warehouse_id',v.get_number('warehouse_id'));
 j.put('status','FIRST_LEG_CUSTODY_RELEASED');j.put('custody_released_at',v.get_string('custody_released_at'));j.put('original_departure_retained',true);j.put('stock_changed',false);j.put('customer_delivery_confirmed',false);p_result:=j.to_clob;
 end;
end;

/
