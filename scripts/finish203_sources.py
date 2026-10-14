from pathlib import Path
import json
out={};f=Path("db/migrations/2026-10-11_ni042_case_sscc")
s=(f/"003_api.sql").read_text(encoding="utf-8").replace("assert_held(RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STOCK_POLICY_GUARD','WAREHOUSE.METADATA'),20)","assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STOCK_POLICY_GUARD','WAREHOUSE.METADATA'))")
s=s.replace("if ct.STATUS not in('NEW','ASSIGNED')or", "if (ct.ASSIGNED_TO is not null and ct.ASSIGNED_TO!=p_actor)or ct.STATUS not in('NEW','ASSIGNED')or",1)
out[str(f/"003_api.sql")]=s
out[str(f/"006_recompile.sql")]=s.split("create or replace context")[0]
p=Path("api/wms_api_server/app/modules/inventory/public.py")
s=p.read_text(encoding="utf-8");s+="\nfrom .api.case_label_routes import router as case_label_router\n"
out[str(p)]=s
p=Path("api/wms_api_server/app/main.py");s=p.read_text(encoding="utf-8");s+="\nfrom .modules.inventory.public import case_label_router\napp.include_router(case_label_router)\n";out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/labels.py");s=p.read_text(encoding="utf-8")
start=s.index("            cur.execute('select COMPANY_PREFIX");end=s.index("            label_id = uuid4().hex",start)
s=s[:start]+"""            result=cur.var(oracledb.DB_TYPE_VARCHAR,size=18)
            cur.execute("begin :result:=RRL_SSCC_ALLOCATOR.allocate(:ware,:actor,'warehouse_receipt_confirm');end;",result=result,ware=order[0],actor=actor)
            sscc=result.getvalue()
"""+s[end:]
needle="            cur.execute('select LABEL_ID,SSCC,PAYLOAD_HASH"
pos=s.index(needle);s=s[:pos]+"""            cur.callproc("RRL_SSCC_ALLOCATOR.assert_scope",[order[0],actor,"warehouse_receipt_confirm"])
"""+s[pos:]
s=s.replace("select LABEL_ID,SSCC,PAYLOAD_HASH from RRL_RECEIPT_LABEL", "select LABEL_ID,SSCC,PAYLOAD_HASH,CREATED_BY from RRL_RECEIPT_LABEL").replace("if old[2] != digest:","if old[2] != digest or old[3]!=actor:")
s=s.replace("from ..domain.sscc_label import check_digit, label_html, label_zpl","from ..domain.sscc_label import label_html, label_zpl")
out[str(p)]=s
# Derive an isolated actual SAP/CASE fixture from the proven previous slice.
p=Path("scripts/ni042_small_final_weight_case.py");s=p.read_text(encoding="utf-8").replace("202","203")
s=s.replace("values(:p_ware,'NONE',0)","values(:p_ware,'NONE',0)") # add configured test prefix separately, not a legal registration claim.
needle=' for cell,is_pick in'
pos=s.index(needle);s=s[:pos]+""" meta("update RRL_RECEIPT_WARE_SETTINGS set COMPANY_PREFIX='900000',EXTENSION_DIGIT=0 where WARE_ID=:p_ware",p_ware=ware)
"""+s[pos:]
needle='   call("POST",f"/api/case-pick/tasks/{case}/claim"'
pos=s.index(needle)
s=s[:pos]+"""   label_path=f"/api/case-pick/tasks/{case}/sscc-label"
   q.execute("select CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:p_case",p_case=case);empty_version=int(q.fetchone()[0])
   label_body={"operation_id":"SSCC203:"+tag,"scan_container":carrier,"expected_content_version":empty_version}
   # Native issue joins outer metadata transaction; rollback restores original identity/history.
   q.callproc("RRL_STOCK_METADATA_TX.begin_change",["admin","case_pick_execute"])
   native_result=q.var(oracledb.DB_TYPE_CLOB)
   try:
    q.callproc("RRL_CASE_SSCC_API.issue",[case,json.dumps(label_body,sort_keys=True,separators=(",",":")),"admin",native_result])
    q.execute("select SSCC from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:p_case",p_case=case);assert q.fetchone()[0]!=carrier
   finally:c.rollback();q.callproc("RRL_STOCK_METADATA_TX.end_change")
   q.execute("select SSCC from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:p_case",p_case=case);assert q.fetchone()[0]==carrier
   label=call("POST",label_path,label_body);assert call("POST",label_path,label_body)==label
   call("POST",label_path,{**label_body,"scan_container":carrier+"X"},status=409)
   from app.modules.inventory.domain.sscc_label import check_digit
   carrier=label["sscc"];assert len(carrier)==18 and carrier[-1]==check_digit(carrier[:-1])
   printed=api.get(base+label_path+"/document");assert printed.status_code==200 and "(00)"+carrier in printed.text and "<svg" in printed.text
   zpl=api.get(base+label_path+"/document?format=zpl");assert zpl.status_code==200 and ">;>800"+carrier in zpl.text
   call("POST",label_path+"/confirm",{"scan":"000000000000000000"},status=409)
   try:q.execute("delete from RRL_CASE_SSCC_LABEL where CASE_PICK_TASK_ID=:p_case",p_case=case);raise AssertionError("Label history deleted")
   except oracledb.DatabaseError as exc:c.rollback();assert exc.args[0].code==20863
   call("POST",label_path+"/confirm",{"scan":"(00)"+carrier})
   assert call("POST",label_path+"/confirm",{"scan":carrier})["confirmed"]
   print("PASS203 native label rollback/original CP retained/18-digit checksum/replay/body conflict/GS1 SVG+ZPL/scan confirm/immutable archive",carrier,flush=True)
"""+s[pos:]
out["scripts/ni042_case_sscc_case.py"]=s
print(json.dumps(out,ensure_ascii=True))
