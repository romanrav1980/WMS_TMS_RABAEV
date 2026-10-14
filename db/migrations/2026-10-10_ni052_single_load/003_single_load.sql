create or replace package RRL_STOCK_SINGLE_LOAD_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/
create or replace package body RRL_STOCK_SINGLE_LOAD_CMD as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');src json_object_t:=d.get_object('source');v json_object_t:=json_object_t();tree json_object_t;sd json_object_t;load_domain json_object_t;
  p clob;r clob;dom clob;snap clob;f json_array_t;resources json_array_t;ships json_array_t:=json_array_t();entry json_object_t:=json_object_t();req json_object_t:=json_object_t();signature_text varchar2(64);
 begin
  if not m.has('loading_context') then raise_application_error(-20886,'SINGLE_LOAD_CONTEXT_REQUIRED');end if;
  RRL_STOCK_LOADING_READ.describe_source(src.get_string('pallet_identifier'),p_operation,p,r,dom,snap);
  tree:=json_object_t.parse(snap);sd:=json_object_t.parse(dom);signature_text:=RRL_STOCK_QC_GATE.signature_for_plan(dom);
  if m.get_string('expected_composition_signature') is null or m.get_string('expected_composition_signature')!=signature_text
   or m.get_number('expected_version') is null or m.get_number('expected_version')!=treat(tree.get_array('nodes').get(0) as json_object_t).get_number('version') then raise_application_error(-20890,'CLOSURE_CHANGED: standalone load composition');end if;
  RRL_STOCK_QC_GATE.assert_approved(dom);
  req.put('command_type','SHIP_PALLET');req.put('operation_id',p_operation);req.put('source',src);req.put('metadata',json_object_t());entry.put('request',req);entry.put('domain',sd);ships.append(entry);
  f:=json_array_t.parse(p);resources:=json_array_t.parse(r);
  RRL_STOCK_HU_LOAD_CORE.compile_load(p_request,snap,ships.to_clob,f,resources,load_domain);
  v.put('shipment',entry);v.put('snapshot',tree);v.put('composition_signature',signature_text);v.put('loading',load_domain);
  p_policies:=f.to_clob;p_resources:=resources.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');plan clob;v json_object_t;tree json_object_t;entry json_object_t;sd json_object_t;
  op varchar2(100):=d.get_string('operation_id');root_node json_object_t;scan_alias varchar2(200);now_p clob;now_r clob;now_d clob;now_s clob;result_json clob;j json_object_t:=json_object_t();
 begin
  if RRL_HAS_WRIGHT(p_actor,'stock_posting_shipping')!=1 then raise_application_error(-20882,'PHYSICAL_LOAD_FORBIDDEN');end if;
  select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=op;v:=json_object_t.parse(plan).get_object('domain');tree:=v.get_object('snapshot');root_node:=treat(tree.get_array('nodes').get(0) as json_object_t);
  scan_alias:=root_node.get_string('sscc');
  if m.get_string('scan_container') is null or(m.get_string('scan_container')!=tree.get_string('root') and(scan_alias is null or m.get_string('scan_container')!=scan_alias))
   or m.get_string('scan_cell') is null or m.get_string('scan_cell')!=tree.get_string('cell') then raise_application_error(-20886,'SINGLE_LOAD_PLACE_CELL_SCAN_REQUIRED');end if;
  RRL_STOCK_HU_LOAD_CORE.begin_load(v.get_object('loading').to_clob);
  entry:=v.get_object('shipment');sd:=entry.get_object('domain');
  -- Actual ST/CASE locks are taken in the existing shipping engine after the trip locks.
  RRL_STOCK_LOADING_READ.describe_source(d.get_object('source').get_string('pallet_identifier'),op,now_p,now_r,now_d,now_s);
  if RRL_STOCK_QC_GATE.signature_for_plan(now_d)!=v.get_string('composition_signature') or dbms_lob.compare(now_s,tree.to_clob)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: standalone physical load');end if;
  RRL_STOCK_SHIPPING_CORE.execute_resolved(entry.get_object('request').to_clob,sd.to_clob,0,p_actor,result_json);
  RRL_STOCK_HU_LOAD_CORE.finish_load(v.get_object('loading').to_clob,tree.to_clob,op,p_actor);
  j.put('operation_id',op);j.put('status','LOADED');j.put('physical_load',v.get_object('loading'));j.put('shipment',json_object_t.parse(result_json));j.put('composition_at_departure',tree);j.put('physical_places',1);p_result:=j.to_clob;
 end;
end;
/
