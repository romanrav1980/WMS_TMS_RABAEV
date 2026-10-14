from pathlib import Path
import json
out={};f=Path("db/migrations/2026-10-11_ni042_small_hu")
out[str(f/"001_schema.sql")]="alter table RRL_WH_FINAL_SCALE_USE add SIGNATURE_VERSION number(2)default 2 not null;\nalter table RRL_WH_FINAL_SCALE_USE add constraint RRL_WH_FINAL_USE_VERSION_C check(SIGNATURE_VERSION in(2,3));\n"
s=(f/"000_before_gate.sql").read_text(encoding="utf-8")
s=s.replace(" function signature_for_plan(p_domain clob) return varchar2;"," function signature_version_for_plan(p_domain clob)return number;\n function signature_for_plan(p_domain clob) return varchar2;",1)
needle="create or replace package body RRL_STOCK_QC_GATE as"
s=s.replace(needle,needle+"""
 function signature_version_for_plan(p_domain clob)return number is
  d json_object_t:=json_object_t.parse(p_domain);task_no number:=d.get_number('case_task');n number;
 begin
  if task_no is null then return 2;end if;
  select case when p.FINAL_WEIGHT_REQUIRED=1 and upper(p.LOAD_UNIT_CLASS)='CONTAINER'then 3 else 2 end into n
   from RRL_CASE_PICK_TASK c join RRL_PALLET_TYPE p on p.PALLET_TYPE_ID=c.PALLET_TYPE_ID where c.CASE_PICK_TASK_ID=task_no;
  return n;
 end;
""")
s=s.replace("j.put('version',2);","j.put('version',signature_version_for_plan(p_domain));\n  if signature_version_for_plan(p_domain)=3 then\n   for z in(select SSCC,PALLET_TYPE_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=v_case)loop j.put('case_identifier',z.SSCC);j.put('case_type_id',z.PALLET_TYPE_ID);end loop;\n  end if;",1)
needle="   for z in(select HU_LINK_ID,PARENT_UID,LINK_VERSION,level DEPTH"
start=s.index(needle);end=s.index("   end loop;x.put('links',links);",start)+len("   end loop;")
s=s[:start]+"   if signature_version_for_plan(p_domain)=2 then\n"+s[start:end]+"\n   end if;"+s[end:]
s=s.replace("j.put('case_task_id',task_no);j.put('case_content_version',dom.get_number('case_version'));","j.put('case_task_id',task_no);j.put('case_content_version',dom.get_number('case_version'));j.put('composition_signature_version',signature_version_for_plan(domain));")
out[str(f/"002_gate.sql")]=s
s=(f/"000_before_admission.sql").read_text(encoding="utf-8")
s=s.replace("package RRL_STOCK_QC_GATE) as","package RRL_STOCK_QC_GATE,package RRL_STOCK_HU_CMD) as",1)
s=s.replace(" function approved(p_domain clob,p_operation varchar2)return number;"," function approved(p_domain clob,p_operation varchar2)return number;\n function preserve_case(p_task number)return number;",1)
s=s.replace("signature_value varchar2(64);actor_value varchar2(50);","signature_value varchar2(64);actor_value varchar2(50);signature_version number;")
s=s.replace("  insert into RRL_WH_FINAL_SCALE_USE(","  signature_version:=RRL_STOCK_QC_GATE.signature_version_for_plan(p_domain);\n  insert into RRL_WH_FINAL_SCALE_USE(",1)
s=s.replace("COMPOSITION_SIGNATURE,ACTOR)\n   values(key_value,p_operation,tare_key,task_no,version_no,signature_value,actor_value);","COMPOSITION_SIGNATURE,ACTOR,SIGNATURE_VERSION)\n   values(key_value,p_operation,tare_key,task_no,version_no,signature_value,actor_value,signature_version);",1)
s=s.replace("u.CASE_CONTENT_VERSION=version_no and u.COMPOSITION_SIGNATURE=signature_value","u.CASE_CONTENT_VERSION<=version_no and u.SIGNATURE_VERSION=RRL_STOCK_QC_GATE.signature_version_for_plan(p_domain) and u.COMPOSITION_SIGNATURE=signature_value")
# Oracle SQL cannot call PL/SQL boolean helpers; signature-version getter is SQL-compatible NUMBER.
pos=s.rindex("\nend;\n/")
s=s[:pos]+"""
 function preserve_case(p_task number)return number is
  required_flag number;identifier varchar2(150);qc json_object_t;
 begin
  select case when p.FINAL_WEIGHT_REQUIRED=1 and upper(p.LOAD_UNIT_CLASS)='CONTAINER'then 1 else 0 end,s.PALLET_UID into required_flag,identifier
   from RRL_CASE_PICK_TASK c join RRL_PALLET_TYPE p on p.PALLET_TYPE_ID=c.PALLET_TYPE_ID left join RRL_SBORKA_PALLETS s on s.ID=c.LEGACY_SBORKA_PALLET_ID
   where c.CASE_PICK_TASK_ID=p_task;
  if required_flag=0 or identifier is null then return 0;end if;
  qc:=json_object_t.parse(RRL_STOCK_QC_GATE.status_json(identifier));
  return case when qc.get_boolean('ready')then 1 else 0 end;
 end;
"""+s[pos:]
# Avoid SQL→PLSQL accessible-by enforcement for a helper-owned call: precompute version scalar.
s=s.replace("signature_value varchar2(64);n number;tx_id_value varchar2(100);","signature_value varchar2(64);n number;tx_id_value varchar2(100);current_signature_version number;")
s=s.replace("tx_id_value:=dbms_transaction.local_transaction_id(false);","tx_id_value:=dbms_transaction.local_transaction_id(false);current_signature_version:=RRL_STOCK_QC_GATE.signature_version_for_plan(p_domain);",1)
s=s.replace("u.SIGNATURE_VERSION=RRL_STOCK_QC_GATE.signature_version_for_plan(p_domain)","u.SIGNATURE_VERSION=current_signature_version")
out[str(f/"003_admission.sql")]=s
s=(f/"000_before_hu.sql").read_text(encoding="utf-8")
needle="    if ct.LEGACY_SBORKA_PALLET_ID is not null then"
assert s.count(needle)==1
s=s.replace(needle,"""    if ct.LEGACY_SBORKA_PALLET_ID is not null and RRL_WH_FINAL_SCALE_ADMISSION.preserve_case(ct.CASE_PICK_TASK_ID)=1 then
     insert into RRL_CASE_PICK_EVENT(CASE_PICK_EVENT_ID,CASE_PICK_TASK_ID,EVENT_TYPE,PAYLOAD_JSON,CREATED_BY)
      values(RRL_CASE_PICK_EVENT_SQ.nextval,ct.CASE_PICK_TASK_ID,'CONTROL_RETAINED_SMALL_BOX',p_request,p_actor);
    elsif ct.LEGACY_SBORKA_PALLET_ID is not null then""")
s=s.replace("-- Packing changes the control signature of all CASE children in the touched tree.","-- Ordinary v2 CASE controls are revoked; a measured small box keeps its own unchanged v3 cargo proof.")
out[str(f/"004_hu.sql")]=s
s=(f/"000_before_qc.sql").read_text(encoding="utf-8")
needle="  q.put('composition_signature',RRL_STOCK_QC_GATE.signature_for_plan(v.to_clob));"
assert s.count(needle)==1
s=s.replace(needle,needle+"\n  q.put('composition_signature_version',RRL_STOCK_QC_GATE.signature_version_for_plan(v.to_clob));")
out[str(f/"005_qc.sql")]=s
s=(f/"000_before_archive.sql").read_text(encoding="utf-8")
needle="r.put('composition_signature',signature_value);"
assert s.count(needle)==1;s=s.replace(needle,needle+"r.put('composition_signature_version',qc.get_number('composition_signature_version'));")
out[str(f/"006_archive.sql")]=s
s=(f/"000_before_use_guard.sql").read_text(encoding="utf-8")
needle="or dom.get_object('quality').get_string('composition_signature')!=:new.COMPOSITION_SIGNATURE"
assert s.count(needle)==1;s=s.replace(needle,needle+"\n  or dom.get_object('quality').get_number('composition_signature_version')is null or dom.get_object('quality').get_number('composition_signature_version')!=:new.SIGNATURE_VERSION")
out[str(f/"007_guard.sql")]=s
out[str(f/"apply.sql")]="@@001_schema.sql\n@@002_gate.sql\n@@003_admission.sql\n@@004_hu.sql\n@@005_qc.sql\n@@006_archive.sql\n@@007_guard.sql\n"
out[str(f/"rollback.sql")]="""declare n number;begin select count(*)into n from RRL_WH_FINAL_SCALE_USE where SIGNATURE_VERSION=3;if n>0 then raise_application_error(-20863,'SMALL_CASE_V3_HISTORY_REQUIRES_FORWARD_REPAIR');end if;end;
/
@@000_before_hu.sql
@@000_before_gate.sql
@@000_before_admission.sql
@@000_before_qc.sql
@@000_before_archive.sql
@@000_before_use_guard.sql
alter table RRL_WH_FINAL_SCALE_USE drop constraint RRL_WH_FINAL_USE_VERSION_C;
alter table RRL_WH_FINAL_SCALE_USE drop(SIGNATURE_VERSION);
"""
out[str(f/"verify.sql")]="select name,type,line,text from user_errors where name not like 'BIN$%';\nselect SIGNATURE_VERSION,count(*)from RRL_WH_FINAL_SCALE_USE group by SIGNATURE_VERSION;\n"
print(json.dumps(out,ensure_ascii=True))
