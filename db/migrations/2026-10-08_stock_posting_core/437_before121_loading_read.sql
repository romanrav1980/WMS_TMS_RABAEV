create or replace package RRL_STOCK_LOADING_READ authid definer as
 procedure describe_source(p_identifier varchar2,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob,p_snapshot out clob);
 function preview_json(p_identifier varchar2) return clob;
end;
/

create or replace package body RRL_STOCK_LOADING_READ as
 procedure describe_source(p_identifier varchar2,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob,p_snapshot out clob) is
  d json_object_t:=json_object_t();src json_object_t:=json_object_t();v json_object_t;tree json_object_t;
 begin
  d.put('command_type','SHIP_PALLET');d.put('operation_id',p_operation);d.put('metadata',json_object_t());src.put('pallet_identifier',p_identifier);d.put('source',src);
  RRL_STOCK_SHIPPING_CORE.compile_shipment(d.to_clob,p_operation,p_policies,p_resources,p_domain,true);v:=json_object_t.parse(p_domain);
  if v.get_number('case_task') is not null then p_snapshot:=RRL_STOCK_HU_READ.case_snapshot_json(v.get_number('case_task'));
  elsif v.get_string('bound_physical_uid') is not null then p_snapshot:=RRL_STOCK_HU_READ.snapshot_json(v.get_string('bound_physical_uid'));
  else raise_application_error(-20886,'SINGLE_LOAD_PHYSICAL_BINDING_REQUIRED');end if;
  tree:=json_object_t.parse(p_snapshot);
  if tree.get_array('ancestors').get_size>0 then raise_application_error(-20886,'SINGLE_LOAD_REQUIRES_WHOLE_UPPER_HU');end if;
 end;
 function preview_json(p_identifier varchar2) return clob is
  p clob;r clob;d clob;s clob;j json_object_t:=json_object_t();tree json_object_t;
 begin
  describe_source(p_identifier,'READ.LOADING',p,r,d,s);tree:=json_object_t.parse(s);
  j.put('shipment_identifier',p_identifier);j.put('composition_signature',RRL_STOCK_QC_GATE.signature_for_plan(d));
  j.put('root',tree.get_string('root'));j.put('expected_version',treat(tree.get_array('nodes').get(0) as json_object_t).get_number('version'));j.put('snapshot',tree);
  return j.to_clob;
 end;
end;
/
