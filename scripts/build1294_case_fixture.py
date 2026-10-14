from pathlib import Path
import json
original=Path("scripts/ni042_marked_direct_receiving_case.py").read_text(encoding="utf-8")
prefix=original[:original.index(' q.execute("select min(CUSTOMER_ID),max(CUSTOMER_ID)')]
prefix=prefix.replace('tag=sys.argv[1]if len(sys.argv)>1 else uuid4().hex[:8]','tag="1294ab01"')
prefix=prefix.replace('201','1294')
prefix=prefix.replace('receive="Q1294R"+tag;pick="Q1294P"+tag;storage="Q1294S"+tag','receive="B94R"+tag;pick="B94P"+tag;storage="B94S"+tag')
# Current gateway contract requires v2. This is explicitly an own development payload.
prefix=prefix.replace('WarehouseSupplyOrder",version="1"','WarehouseSupplyOrder",version="2"')
prefix=prefix.replace('with oracledb.connect(user=s.oracle_user', 'if Path("tmp/context1294.json").exists():raise SystemExit("Retained fixture exists; resume it")\nwith oracledb.connect(user=s.oracle_user')
prefix=prefix.replace('call("PUT",f"/api/finished-goods', 'call("PUT",f"/api/finished-goods')
tail=''' q.execute("select min(CUSTOMER_ID)from RRL_CUSTOMER");customer=q.fetchone()[0]
 ctx={"stage":"METADATA","tag":tag,"warehouse":ware,"article":article,"source":sscc,"cell":receive,"gtin":gtin,"supply":imported,"revision":revision,"units":units}
 def save():Path("tmp/context1294.json").write_text(json.dumps(ctx,indent=2),encoding="utf-8")
 save()
 result=call("POST",f"/api/receiving/supply-orders/{imported['order_id']}/pallets",body,201);ctx["receipt"]=result;save()
 order=seq("RRL_CUSTOMER_ORDER_SQ")
 meta("insert into RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID,ORDER_NO,CUSTOMER_ID,WARE_ID)values(:id,:n,:customer,:ware)",id=order,n="B02.1294:"+tag,customer=customer,ware=ware)
 meta("insert into RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,LINE_NO,ARTICUL,ORDER_QTY,UNIT_CODE)values(RRL_CUSTOMER_ORDER_ROW_SQ.nextval,:o,1,:a,5,'EA')",o=order,a=article)
 ctx["order"]=order;save()
 plan=picking.create_plan(PickingPlanCreateRequest(customer_order_id=order,created_by="admin"));ctx["plan"]=plan;save()
 wave=picking.create_wave(PickWaveCreateRequest(wave_code="B02.1294:"+tag,ware_id=ware,created_by="admin"));ctx["wave"]=wave;save()
 picking.add_wave_plan(wave,PickWaveAddPlanRequest(pick_plan_id=plan,created_by="admin"))
 picking.preview_wave(wave,PickWaveActionRequest(updated_by="admin"))
 picking.launch_wave(wave,PickWaveActionRequest(updated_by="admin",operation_id="B02.LAUNCH1294:"+tag))
 post("WAVE_PICK_RELEASE",{"wave_id":wave},{},op="B02.RELEASE1294:"+tag)
 q.execute("select t.CASE_PICK_TASK_ID,l.CASE_PICK_LINE_ID,t.SSCC,l.CELL_CODE,l.PLANNED_QTY,t.PALLET_TYPE_ID from RRL_CASE_PICK_TASK t join RRL_CASE_PICK_LINE l on l.CASE_PICK_TASK_ID=t.CASE_PICK_TASK_ID where t.PICK_WAVE_ID=:w",w=wave)
 case,line,carrier,cell,quantity,case_type=q.fetchone()
 ctx.update(case=int(case),line=int(line),carrier=carrier,cell=cell,quantity=str(quantity),case_type=int(case_type));save()
 tare="/api/inventory/tare"
 availability=call("GET",tare+f"/warehouses/{ware}/availability");current=next(x for x in availability if x["pallet_type_id"]==case_type)
 call("POST",tare+"/count",{"operation_id":"B02.TARE.COUNT1294:"+tag,"owner_ware_id":ware,"pallet_type_id":case_type,"condition":"GOOD","observed_quantity":"1","expected_version":current["balance_version"]or 0,"reason":"Own dev B02 UI fixture","decision_reference":"B02.1294:"+tag})
 call("POST",tare+"/book",{"operation_id":"B02.TARE.BOOK1294:"+tag,"place_kind":"CASE","place_id":str(case)})
 call("POST",f"/api/case-pick/tasks/{case}/claim",{});call("POST",f"/api/case-pick/tasks/{case}/start",{})
 q.execute("select u.UNIT_ID,u.PHYSICAL_UNIT_KEY from RRL_WMS_RECEIPT_UNIT u join RRL_STOCK_RESERVATION r on r.RESERVATION_ID=u.HARD_RESERVATION_ID where r.SOURCE_DOC_TYPE='PICK_WAVE'and r.SOURCE_DOC_ID=:w and r.SOURCE_LINE_ID=(select PICK_TASK_ID from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=:l)and r.BASE_QTY>0 order by u.PHYSICAL_UNIT_KEY",w=wave,l=line)
 selected=q.fetchall();assert len(selected)==5
 ctx["scans"]=[code for unit_id,_ in selected for code in units[int(unit_id)-1]["codes"]];ctx["stage"]="READY_FOR_UI";save()
 print(json.dumps({k:v for k,v in ctx.items()if k not in("scans","units","supply")}))
'''
print(json.dumps({"scripts/prepare1294_case_fixture.py":prefix+tail},ensure_ascii=True))
