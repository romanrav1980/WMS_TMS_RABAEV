raise SystemExit("Retired authoring generator: use final SQL/current manifest and fresh affected-owner checkpoint; never overwrite later runtime")
from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni053_marked_recipient");out={}
out[str(f/"001_mark_core.sql")]="""create or replace package RRL_STORE_MARK_CORE authid definer accessible by(package RRL_STOCK_STORE_RECEIPT_READ,package RRL_STOCK_STORE_RECEIPT_CMD)as
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
"""
s=(f/"000_before_rrl_stock_store_receipt_cmd.sql").read_text(encoding="utf-8")
s=s.replace("root_node json_object_t;","root_node json_object_t;proof json_object_t;",1)
s=s.replace("if v.get_boolean('requires_marked_recipient_flow') then raise_application_error(-20886,'STORE_MARKED_RECIPIENT_FLOW_REQUIRED');end if;","if v.get_boolean('requires_marked_recipient_flow') then RRL_STORE_MARK_CORE.verify_scans(v,m,proof);v.put('marked_unit_proof',proof);elsif m.has('unit_scans')and m.get_array('unit_scans').get_size>0 then raise_application_error(-20886,'STORE_UNEXPECTED_UNIT_SCANS');end if;")
s=s.replace("RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);","RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);\n  if v.has('marked_unit_proof')then RRL_STORE_MARK_CORE.declare_rows(v,f,r);end if;",1)
s=s.replace("has_issue:=has_issue or weight_issue;","has_issue:=has_issue or weight_issue;\n  if v.has('marked_unit_proof')and has_issue then raise_application_error(-20886,'STORE_MARKED_DISPOSITION_UNIT_ASSIGNMENT_REQUIRED');end if;")
s=s.replace("  assert_input(m,now_v);","  assert_input(m,now_v);\n  if v.has('marked_unit_proof')and(not now_v.has('marked_unit_proof')or dbms_lob.compare(v.get_object('marked_unit_proof').to_clob,now_v.get_object('marked_unit_proof').to_clob)!=0)then raise_application_error(-20890,'CLOSURE_CHANGED: store marked unit proof');end if;")
s=s.replace("j.put('operation_id',op);","if v.has('marked_unit_proof')then j.put('physical_unit_count',v.get_object('marked_unit_proof').get_number('physical_unit_count'));j.put('original_unit_signature',v.get_object('marked_unit_proof').get_string('unit_signature'));j.put('mark_scan_confirmed',true);j.put('regulatory_ack_verified',false);end if;\n  j.put('operation_id',op);",1)
out[str(f/"002_receipt.sql")]=s
s=(f/"000_before_rrl_stock_store_receipt_read.sql").read_text(encoding="utf-8")
# Active account and current binding applies even to committed replay.
s=s.replace("select count(*) into n from RUSERS where ID=p_actor and USER_GROUP='GLOBAL_ADMIN';","select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0;\n  if n!=1 then raise_application_error(-20882,'STORE_CURRENT_RECEIVER_REQUIRED');end if;\n  select count(*) into n from RUSERS where ID=p_actor and upper(trim(USER_GROUP))='GLOBAL_ADMIN';")
s=s.replace("  p_domain:=j.to_clob;","  if j.get_boolean('requires_marked_recipient_flow')and not j.get_boolean('already_received')then j.put('marked_unit_control',json_object_t.parse(RRL_STORE_MARK_CORE.preview(j)));end if;\n  p_domain:=j.to_clob;",1)
out[str(f/"003_reader.sql")]=s
s=(f/"000_before_rrl_stock_posting_api.sql").read_text(encoding="utf-8")
s=s.replace("  if g_kind='INTERWARE_CUSTODY_RELEASE'then","  if g_kind='STORE_RECEIPT'then declare doc json_object_t:=json_object_t.parse(p_request);begin RRL_STOCK_STORE_RECEIPT_READ.require_receiver(p_actor,doc.get_object('source').get_string('store_address'));end;end if;\n  if g_kind='INTERWARE_CUSTODY_RELEASE'then")
out[str(f/"004_root.sql")]=s
out[str(f/"005_recompile.sql")]="alter package RRL_STOCK_STORE_RECEIPT_CMD compile body;\nalter package RRL_STOCK_POSTING_API compile body;\n"
out[str(f/"rollback.sql")]="declare n number;begin select count(*)into n from RRL_STOCK_OPERATION where COMMAND_TYPE='STORE_RECEIPT'and STATE='APPLIED'and json_exists(RESOLVED_PLAN_JSON,'$.domain.marked_unit_proof');if n>0 then raise_application_error(-20863,'MARKED_STORE_RECEIPT_FORWARD_REPAIR_REQUIRED');end if;end;\n/\n@@000_before_rrl_stock_store_receipt_cmd.sql\n@@000_before_rrl_stock_store_receipt_read.sql\n@@000_before_rrl_stock_posting_api.sql\n@@005_recompile.sql\n"
out["wiki/database/retailcase_ni053_marked_recipient_design_20261011.md"]="# NI05.3: уникальные QR при окончательной приёмке\n229 extends original STORE_RECEIPT/current recipient permission+address before replay; original single STOCK issued fingerprint/current physical versions/current mandatory UNIT profiles/exact QR matrix, frozen/revalidated under original stock closure. Whole acceptance only; marked discrepancy requires per-unit disposition and remains refused. Existing fact/disposition/common outbox one TX, no warehouse stock consumption/unit birth or real government ACK. Original direct/two-leg customer lineage retained; nested/aggregate/serialized nonprofile remain explicit unsupported. Fresh captured sources/paired recovery; forward repair after marked receipt.\n"
print(json.dumps(out,ensure_ascii=True))
