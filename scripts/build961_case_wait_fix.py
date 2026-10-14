from pathlib import Path
import json,hashlib
d="db/migrations/2026-10-13_ni072_case_wait/";read=lambda p:Path(p).read_text(encoding="utf-8");files={}
p=d+"005_wait_api.sql";body=read(p)
body=body.replace("declare prep json_object_t:=json_object_t.parse(source);src_case number;","declare prep json_object_t:=json_object_t.parse(source);src_case number;case_uid varchar2(200);case_version number;")
body=body.replace("src_case:=prep.get_number('case_task_id');from_cell:=prep.get_string('cell');","src_case:=prep.get_number('case_task_id');from_cell:=prep.get_string('cell');case_uid:=prep.get_string('pallet_identifier');case_version:=prep.get_number('content_version');")
body=body.replace("decision.VERSION_NO,prep.get_string('pallet_identifier'),from_cell,target","decision.VERSION_NO,case_uid,from_cell,target")
body=body.replace("task_id,p_operation,prep.get_string('pallet_identifier'),from_cell,target,1,'CASE',prep.get_number('content_version'),source,src_case","task_id,p_operation,case_uid,from_cell,target,1,'CASE',case_version,source,src_case")
files[p]=body
p=d+"002_case_wait.sql";body=read(p)
body=body.replace("sync_id number;sync_key varchar2(400);op varchar2(100):=d.get_string('operation_id');","sync_id number;sync_key varchar2(400);op varchar2(100):=d.get_string('operation_id');new_version number;ff_id number;case_id number;")
body=body.replace("  update RRL_CUSTOMER_ORDER_FULFILLMENT set PICKED_CONTENT_VERSION=j.get_number('content_version')","  new_version:=j.get_number('content_version');ff_id:=frozen.get_number('fulfillment_id');case_id:=j.get_number('case_pick_task_id');\n  update RRL_CUSTOMER_ORDER_FULFILLMENT set PICKED_CONTENT_VERSION=new_version")
body=body.replace("FULFILLMENT_ID=frozen.get_number('fulfillment_id')and STATUS='PICKED'and PICKED_CASE_TASK_ID=j.get_number('case_pick_task_id')","FULFILLMENT_ID=ff_id and STATUS='PICKED'and PICKED_CASE_TASK_ID=case_id")
files[p]=body
files[d+"fix961.sql"]="@@002_case_wait.sql\n@@005_wait_api.sql\n@@008_compile.sql\n"
p=d+"checkpoint.json";v=json.loads(read(p));v["state"]="APPLIED_DEV_COMPILED_CASE_PENDING";v["correction961"]="Runtime JSON object method in SQL values extracted into PL/SQL scalars; initial955 beforewave,956 beforetare,959 planning40573 are failed stages, noPASS";v["sha256"].update({p:hashlib.sha256(b.encode()).hexdigest()for p,b in files.items()});files[p]=json.dumps(v,indent=2)
p="wiki/database/nicora_ni072_case_wait_20261013.md";files[p]=read(p)+"\n953 apply/current USER_ERRORS[]/INVALID[]. Actual955 stopped beforewave; retained956/959 reused same source through existing reconcile + tare count/book, CASE1129/1130 picked12+8, ST originaldeferral succeeded. WAIT registration rejected40573 before stock move;961 extracts JSON SQL scalar values. Current stageDEFERRED, own P12H12 + P8H8 intact; nofactoryrerun. Finish proof pending.\n"
p="wiki/log.md";files[p]=read(p)+"\n- 2026-10-13 checkpoint961:953 appliedVALID; retained955 phasecontinuation native originalreconcile/tare books/casepick12+8/STdeferral passed, planning failed40573, NOTPASS.961 JSON scalar correctioncheckpoint beforeapply; no stockbirth/reset/copy.\n"
p="wiki/index.md";files[p]="- [CASE ожидание961](database/nicora_ni072_case_wait_20261013.md):953 compiledVALID, retained source picked/deferred; runtime scalar correction, movement pending.\n"+read(p)
print(json.dumps(files,ensure_ascii=True))
