create or replace package RRL_STORE_MARK_CORE authid definer accessible by(package RRL_STOCK_STORE_RECEIPT_READ,package RRL_STOCK_STORE_RECEIPT_CMD)as
 function source_proof(p_domain json_object_t)return json_object_t;
 function preview(p_domain json_object_t)return clob;
 procedure verify_scans(p_domain json_object_t,p_metadata json_object_t,p_proof out json_object_t);
 procedure declare_rows(p_domain json_object_t,p_policies in out nocopy json_array_t,p_resources in out nocopy json_array_t);
end;
/
create or replace package body RRL_STORE_MARK_CORE as
 function source_proof(p_domain json_object_t)return json_object_t is
  tree json_object_t:=p_domain.get_object('snapshot');node json_object_t;proof json_object_t;profiles clob;n number;bad number;
  article varchar2(160);wire clob;
 begin
  if tree.get_array('nodes').get_size!=1 or tree.get_number('leaf_count')!=1 or tree.get_number('top_place_count')!=1 then raise_application_error(-20886,'STORE_MARK_SINGLE_STOCK_SCOPE_REQUIRED');end if;
  node:=treat(tree.get_array('nodes').get(0)as json_object_t);article:=node.get_string('article');
  wire:=RRL_INTERWARE_UNIT_SOURCE.issued_manifest(p_domain.get_string('load_operation_id'),node.get_string('uid'),tree.to_clob);proof:=json_object_t.parse(wire);
  select count(*),sum(case when SCAN_MODE='UNIT'then 0 else 1 end),
   json_arrayagg(json_object('system_code'value SYSTEM_CODE,'profile_code'value PROFILE_CODE,'profile_version'value PROFILE_VERSION,'scan_mode'value SCAN_MODE)order by SYSTEM_CODE,PROFILE_CODE returning clob)
   into n,bad,profiles from RRL_SKU_RECEIPT_PROFILE where ARTICUL=article;
  if n<1 or n>50 or bad!=0 or proof.get_number('physical_unit_count')<1 then raise_application_error(-20886,'STORE_MARK_CURRENT_UNIT_PROFILES_REQUIRED');end if;
  if n*proof.get_number('physical_unit_count')>20000 then raise_application_error(-20881,'STORE_MARK_SCAN_BOUND');end if;
  proof.put('profiles',json_array_t.parse(profiles));proof.put('supported',true);proof.put('expected_scan_count',n*proof.get_number('physical_unit_count'));return proof;
 end;
 function preview(p_domain json_object_t)return clob is p json_object_t;
 begin p:=source_proof(p_domain);return p.to_clob;
 exception when others then
  if sqlcode between -20999 and -20800 then p:=json_object_t();p.put('supported',false);p.put('reason',substr(sqlerrm,1,250));return p.to_clob;else raise;end if;
 end;
 procedure verify_scans(p_domain json_object_t,p_metadata json_object_t,p_proof out json_object_t)is
  node json_object_t;leg json_object_t;legs json_array_t:=json_array_t();qc json_object_t:=json_object_t();n number;
 begin
  p_proof:=source_proof(p_domain);node:=treat(p_domain.get_object('snapshot').get_array('nodes').get(0)as json_object_t);leg:=node.clone();
  leg.put('cell',p_proof.get_string('source_cell'));legs.append(leg);qc.put('legs',legs);
  RRL_INTERWARE_MARK_SCAN.validate_scan(qc.to_clob,p_metadata.to_clob,n);
  if n!=p_proof.get_number('physical_unit_count')then raise_application_error(-20884,'STORE_MARK_UNIT_COUNT_CONFLICT');end if;
 end;
 procedure declare_rows(p_domain json_object_t,p_policies in out nocopy json_array_t,p_resources in out nocopy json_array_t)is node json_object_t;
 begin
  node:=treat(p_domain.get_object('snapshot').get_array('nodes').get(0)as json_object_t);
  RRL_STOCK_PLAN_HELPER.stock_closure(p_policies,p_resources,node.get_string('uid'),node.get_string('article'),p_domain.get_object('snapshot').get_string('cell'),null);
 end;
end;
/
