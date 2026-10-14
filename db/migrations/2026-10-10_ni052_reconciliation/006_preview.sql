create or replace package RRL_STOCK_LOAD_RECONCILE_READ authid definer as
 function preview_json(p_original varchar2) return clob;
end;
/
create or replace package body RRL_STOCK_LOAD_RECONCILE_READ as
 function preview_json(p_original varchar2) return clob is
  raw_result clob;j json_object_t;tree json_object_t;out_json json_object_t:=json_object_t();n number;
 begin
  select RESULT_JSON into raw_result from RRL_STOCK_OPERATION where OPERATION_ID=p_original and COMMAND_TYPE='HU_SHIP' and STATE='APPLIED';
  j:=json_object_t.parse(raw_result);tree:=j.get_object('composition_at_departure');
  if j.has('physical_load') and not j.get('physical_load').is_null then raise_application_error(-20886,'RECONCILE_ALREADY_HAS_PHYSICAL_LOAD');end if;
  if tree.get_array('nodes').get_size>200 or tree.get_array('ancestors').get_size!=0 then raise_application_error(-20881,'RECONCILE_PREVIEW_BOUND');end if;
  select count(*) into n from RRL_TT_LOAD_RECONCILE where SHIPPING_OPERATION_ID=p_original;
  out_json.put('shipping_operation_id',p_original);out_json.put('snapshot',tree);
  out_json.put('composition_signature',rawtohex(sys.dbms_crypto.hash(tree.to_clob,sys.dbms_crypto.hash_sh256)));
  out_json.put('already_reconciled',n>0);out_json.put('stock_already_consumed',true);out_json.put('server_rechecks_history_and_current_state',true);
  return out_json.to_clob;
 exception when no_data_found then raise_application_error(-20886,'RECONCILE_APPLIED_WHOLE_HU_SHIPMENT_REQUIRED');
 end;
end;
/
