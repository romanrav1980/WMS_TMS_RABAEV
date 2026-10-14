import json
from pathlib import Path
base="db/migrations/2026-10-10_ni081_range_apply/";out={}
p=Path(base+"006_core.sql");s=p.read_text(encoding="utf-8")
s=s.replace("q number;v_new clob;v_old clob;","q number;v_proof clob;v_face number;v_cell varchar2(100);layout json_object_t;")
s=s.replace("refs:=recommendation.get_array('reference_templates');old_faces:=s.get_object('existing_range').get_array('cells');", "refs:=recommendation.get_array('reference_templates');layout:=s.get_object('existing_range');old_faces:=layout.get_array('cells');")
s=s.replace("  x:=treat(refs.get(0)as json_object_t);", "  x:=treat(refs.get(0)as json_object_t);v_face:=x.get_number('pick_face_id');")
s=s.replace("a.PICK_FACE_ID=x.get_number('pick_face_id')", "a.PICK_FACE_ID=v_face")
s=s.replace("  insert into RRL_PICK_RANGE_APPROVAL(", "  v_proof:=s.to_clob;\n  insert into RRL_PICK_RANGE_APPROVAL(")
s=s.replace("values(identity,p_operation,p_ware,p_article,s.to_clob);", "values(identity,p_operation,p_ware,p_article,v_proof);")
s=s.replace("   x:=treat(old_faces.get(i)as json_object_t);", "   x:=treat(old_faces.get(i)as json_object_t);v_face:=x.get_number('pick_face_id');v_cell:=x.get_string('cell');")
s=s.replace("TARGET_CELL_CODE=x.get_string('cell')", "TARGET_CELL_CODE=v_cell")
s=s.replace("s RRL_PICK_RANGE_STATUS%rowtype;n number;j", "s RRL_PICK_RANGE_STATUS%rowtype;n number;v_mapping number;j")
s=s.replace("  select *into a from RRL_PICK_FACE_ARTICUL where PICK_FACE_ARTICUL_ID=b.get_number('pick_face_articul_id')for update;", "  v_mapping:=b.get_number('pick_face_articul_id');\n  select *into a from RRL_PICK_FACE_ARTICUL where PICK_FACE_ARTICUL_ID=v_mapping for update;")
out[str(p)]=s
p=Path("db/migrations/2026-10-10_ni081_range_proposal/002_api.sql");a=p.read_text(encoding="utf-8")
a=a.replace("p_action not in('SAVE_DRAFT','CANCEL_DRAFT')","p_action not in('SAVE_DRAFT','CANCEL_DRAFT','APPROVE','CLOSE_DRAIN')")
a=a.replace("if p_action='SAVE_DRAFT'and p_source is null", "if p_action in('SAVE_DRAFT','APPROVE')and p_source is null")
anchor="  if p_action='SAVE_DRAFT'then\n   s:=json_object_t.parse(p_source);"
apply="""  if p_action in('APPROVE','CLOSE_DRAIN')then
   RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
   savepoint RRL_RANGE157;v_saved:=true;g_tx:=dbms_transaction.local_transaction_id(true);
   RRL_PICK_RANGE_APPLY_CORE.apply_change(p_operation,p_actor,p_action,p_ware,p_article,p_request,p_source,result);
   j:=json_object_t.parse(result);j.put('operation_id',p_operation);result:=j.to_clob;
   insert into RRL_PICK_RANGE_OPERATION(OPERATION_ID,ACTION_CODE,WARE_ID,ARTICLE,ACTOR,REQUEST_HASH,REQUEST_JSON,RESULT_JSON)
    values(p_operation,p_action,p_ware,p_article,p_actor,digest,p_request,result);
   p_result:=result;g_tx:=null;return;
  end if;
"""
if a.count(anchor)!=1:raise ValueError("proposal source anchor")
a=a.replace(anchor,apply+anchor)
a=a.replace("select count(*)into n from RRL_PICK_RANGE_CANCEL where PROPOSAL_ID=identity;", """select (select count(*)from RRL_PICK_RANGE_CANCEL where PROPOSAL_ID=identity)
    +(select count(*)from RRL_PICK_RANGE_APPROVAL where PROPOSAL_ID=identity)into n from dual;""")
a=a.replace("'PICK_RANGE_PROPOSAL_ALREADY_CANCELLED'","'PICK_RANGE_PROPOSAL_NOT_CURRENT_DRAFT'")
out[base+"007_proposal_contract.sql"]=a
out[base+"007_proposal_body.sql"]="create or replace "+a.split("create or replace ",2)[2]
out[base+"apply_commands.sql"]="@@006_core.sql\n@@007_proposal_body.sql\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
m["packages"].append("RRL_PICK_RANGE_APPLY_CORE")
idx=m["components"].index("../2026-10-10_ni081_range_proposal/002_api.sql")
m["components"][idx]="../2026-10-10_ni081_range_apply/007_proposal_contract.sql"
m["components"].insert(idx,"../2026-10-10_ni081_range_apply/006_core.sql")
out[str(p)]=json.dumps(m,ensure_ascii=False,indent=2)+"\n"
print(json.dumps(out))
