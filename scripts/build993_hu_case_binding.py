from pathlib import Path
import json,hashlib
read=lambda p:Path(p).read_text(encoding="utf-8");d="db/migrations/2026-10-13_ni041_hu_case_binding/";files={}
def capture(p,n):
 raw=read(p);files[d+"000_before_"+n+".sql"]=raw;return "\n".join(x for x in raw.splitlines()if x.strip())+"\n"
spec=capture("tmp/992_case_bind_package.sql","binding_spec")
spec=spec.replace("accessible by(package RRL_STOCK_CASE_MOVE_CMD)","accessible by(package RRL_STOCK_CASE_MOVE_CMD,package RRL_STOCK_HU_CMD)")
needle="end;\n/";assert spec.count(needle)==1
spec=spec.replace(needle,""" procedure plan_tree(p_nodes json_array_t,p_resources in out nocopy json_array_t,p_domain in out nocopy json_object_t);
 procedure validate_tree(p_nodes json_array_t,p_domain json_object_t);
 function binding_for(p_domain json_object_t,p_case_id number)return json_object_t;
"""+needle)
files[d+"001_spec.sql"]=spec
body=capture("tmp/992_case_bind_package_body.sql","binding_body")
needle="  select *into f from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=s.ID;";assert body.count(needle)==1
body=body.replace(needle,needle+"""
  -- Closed fulfillment belongs to immutable shipment history, not the current warehouse movement.
  if f.STATUS in('SHIPPED','CANCELLED')then return null;end if;""")
needle="  if p_frozen is null or p_version!=p_case.CONTENT_VERSION+1";assert body.count(needle)==1
body=body.replace(needle,"""  if p_frozen is null then
   if source_snapshot(p_case)is not null then raise_application_error(-20890,'CLOSURE_CHANGED: CASE current binding appeared');end if;return;
  end if;
  if p_version!=p_case.CONTENT_VERSION+1""")
pos=body.rfind("\nend;")
tree="""
 function binding_for(p_domain json_object_t,p_case_id number)return json_object_t is bindings json_object_t;begin
  bindings:=p_domain.get_object('case_bindings');if bindings is null then return null;end if;
  return bindings.get_object(RRL_STOCK_PLAN_HELPER.decimal_text(p_case_id));
 end;
 procedure plan_tree(p_nodes json_array_t,p_resources in out nocopy json_array_t,p_domain in out nocopy json_object_t)is
  node json_object_t;one_domain json_object_t;bindings json_object_t;ct RRL_CASE_PICK_TASK%rowtype;case_id number;
 begin
  if p_nodes is null then return;end if;
  bindings:=p_domain.get_object('case_bindings');if bindings is null then bindings:=json_object_t();end if;
  for i in 0..p_nodes.get_size-1 loop
   node:=treat(p_nodes.get(i)as json_object_t);
   if node.get_string('kind')='CASE'then
    case_id:=node.get_number('case_task_id');select *into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=case_id;
    one_domain:=json_object_t();plan_move(ct,p_resources,one_domain);
    if one_domain.has('shipment_binding')then bindings.put(RRL_STOCK_PLAN_HELPER.decimal_text(case_id),one_domain.get_object('shipment_binding'));end if;
   end if;
  end loop;
  p_domain.put('case_bindings',bindings);
 end;
 procedure validate_tree(p_nodes json_array_t,p_domain json_object_t)is node json_object_t;ct RRL_CASE_PICK_TASK%rowtype;case_id number;begin
  if p_nodes is null then return;end if;
  for i in 0..p_nodes.get_size-1 loop
   node:=treat(p_nodes.get(i)as json_object_t);
   if node.get_string('kind')='CASE'then
    case_id:=node.get_number('case_task_id');select *into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=case_id;
    validate_move(ct,binding_for(p_domain,case_id));
   end if;
  end loop;
 end;
"""
body=body[:pos]+tree+body[pos:];files[d+"002_binding.sql"]=body
hu=capture("tmp/990_rrl_stock_hu_cmd_package_body.sql","hu_cmd")
needle="  p_domain:=v.to_clob;p_policies:=f.to_clob;p_resources:=r.to_clob;";assert hu.count(needle)==1
hu=hu.replace(needle,"""  if v.has('parent_snapshot')then RRL_STOCK_CASE_BIND_MOVE.plan_tree(v.get_object('parent_snapshot').get_array('nodes'),r,v);end if;
  if v.has('child_snapshot')then RRL_STOCK_CASE_BIND_MOVE.plan_tree(v.get_object('child_snapshot').get_array('nodes'),r,v);end if;
"""+needle)
needle="v_mode varchar2(20);v_case_sscc varchar2(64);v_parent_nodes clob;v_child_nodes clob;";assert hu.count(needle)==1
hu=hu.replace(needle,needle+"old_case RRL_CASE_PICK_TASK%rowtype;")
needle="  if v_kind='HU_CREATE' then\n   v_cell:=v.get_string('cell');";assert hu.count(needle)==1
hu=hu.replace(needle,"""  if v.has('parent_snapshot')then RRL_STOCK_CASE_BIND_MOVE.validate_tree(v.get_object('parent_snapshot').get_array('nodes'),v);end if;
  if v.has('child_snapshot')then RRL_STOCK_CASE_BIND_MOVE.validate_tree(v.get_object('child_snapshot').get_array('nodes'),v);end if;
"""+needle)
needle="     update RRL_CASE_PICK_TASK set CURRENT_CELL=v_target,CONTENT_VERSION=CONTENT_VERSION+1"
assert hu.count(needle)==1
hu=hu.replace(needle,"     select *into old_case from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=v_case;\n"+needle)
needle="UPDATED_BY=p_actor where CASE_PICK_TASK_ID=v_case;\n     insert into RRL_CASE_PICK_EVENT";assert hu.count(needle)==1
hu=hu.replace(needle,"UPDATED_BY=p_actor where CASE_PICK_TASK_ID=v_case;\n     RRL_STOCK_CASE_BIND_MOVE.finish_move(old_case,RRL_STOCK_CASE_BIND_MOVE.binding_for(v,v_case),old_case.CONTENT_VERSION+1,p_actor);\n     insert into RRL_CASE_PICK_EVENT")
needle="    update RRL_CASE_PICK_TASK set CONTENT_VERSION=CONTENT_VERSION+1,UPDATED_AT=systimestamp,UPDATED_BY=p_actor where CASE_PICK_TASK_ID=v_case;";assert hu.count(needle)==1
hu=hu.replace(needle,"    select *into old_case from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=v_case;\n"+needle+"\n    RRL_STOCK_CASE_BIND_MOVE.finish_move(old_case,RRL_STOCK_CASE_BIND_MOVE.binding_for(v,v_case),old_case.CONTENT_VERSION+1,p_actor);")
files[d+"003_hu_cmd.sql"]=hu
files[d+"004_compile.sql"]=read("db/migrations/2026-10-13_ni072_case_wait/008_compile.sql")
files[d+"005_ledger.sql"]="""merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-13-008-ni041-hu-case-binding'MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Existing HU tree operations declare and preserve active CASE fulfillment versions in the same stock transaction through reused binding core; closed shipment history unchanged',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
"""
files[d+"apply.sql"]="@@001_spec.sql\n@@002_binding.sql\n@@003_hu_cmd.sql\n@@004_compile.sql\n@@005_ledger.sql\n"
files[d+"rollback.sql"]="@@000_before_binding_spec.sql\n@@000_before_binding_body.sql\n@@000_before_hu_cmd.sql\n@@004_compile.sql\n"
files[d+"verify.sql"]="select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME not like 'BIN$%';\nselect c.CASE_PICK_TASK_ID,c.CONTENT_VERSION,f.PICKED_CONTENT_VERSION,f.STATUS from RRL_CASE_PICK_TASK c join RRL_CUSTOMER_ORDER_FULFILLMENT f on f.PICKED_CASE_TASK_ID=c.CASE_PICK_TASK_ID where c.CASE_PICK_TASK_ID in(1131,1132);\n"
files[d+"checkpoint.json"]=json.dumps({"migration_id":"2026-10-13-008-ni041-hu-case-binding","state":"PREPARED","target":"RABAEV/orcl","recovery":"current990HU/current992binding captures+pairedrollback; no quantity history rewrite/copy","sha256":{p:hashlib.sha256(b.encode()).hexdigest()for p,b in files.items()}},indent=2)
page="""# NI04.1 — актуальная привязка CASE внутри HU

993 PREPARED before apply, migration2026-10-13-008-ni041-hu-case-binding. Actual CURRENT HU_CMD990 contains existing matryoshka. HU_ATTACH/DETACH directCASE and HU_MOVE tree increment CASEcontentversion but did not update activePICKED fulfillment; reuse binding core974.

Root declares ST/FF keys per CASE in parent/child snapshots, stores frozen material bindings map and validates it after existing ST/CASE row locks before tree changes. Touched CASE increments and matching FFversion occur inside the existing HU stock transaction. Unbound CASE unchanged. Closed SHIPPED/CANCELLED fulfillment is immutable historical history and is not advanced; activePICKED binding has strict original relation/warehouse/version/load proof. Existing transfercore still moves quantities/reserves/units only on leaf lots.

Packing/detaching existing policy deliberately revokes ordinary CASE controls, measured small-box exception preserved. Moving intacttree preserves current admission by old policy; no blanket recontrol is invented. Current HU slot/target/scan/warehouse constraints retained. Captures990/992/SHA/pairedrollback/no DBcopy. Livecompile and ownretained987 twoCASE HU attach/move/detach scenario still pending; not fullNI04.1 closure.
"""
files["wiki/database/nicora_ni041_hu_case_binding_20261013.md"]=page
p="wiki/index.md";files[p]="- [NI04.1 HU CASE binding993](database/nicora_ni041_hu_case_binding_20261013.md): prepared originalmatryoshka/one activeFFversion owner/frozen tree bindings, live pending.\n"+read(p)
p="wiki/log.md";files[p]=read(p)+"\n- 2026-10-13 checkpoint993 PREPARED original HU_CMD tree CASE versions with reused binding974; activePICKED only/closedhistoryunchanged, RootSTFF resources and frozenbindings, captures990992/SHA/pairedrollback, no stock writer/copy. Actualpending.\n"
print(json.dumps(files,ensure_ascii=True))
