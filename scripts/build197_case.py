from pathlib import Path
import json
s=Path("scripts/ni042_weight_choice_plan_case.py").read_text(encoding="utf-8")
s=s.replace('article="QW196"+tag.upper()','article="QW197"+tag.upper();selected=int(sys.argv[2])if len(sys.argv)>2 else 12;assert selected in(8,12)')
s=s.replace("CASE196.QA","CASE197.QA").replace("WEIGHT196.CHOICE","WEIGHT197.CHOICE").replace("QA196","QA197")
s=s.replace('if x["net_weight_kg"]=="8"','if x["net_weight_kg"]==str(selected)')
s=s.replace('"weighted_box_barcode":labels[0]','"weighted_box_barcode":labels[0 if selected==8 else 1]')
s=s.replace('{"weighted_box_barcode":labels[1]}','{"weighted_box_barcode":labels[1 if selected==8 else 0]}')
s=s.replace('accepted["selected_net_weight_kg"]=="8"','accepted["selected_net_weight_kg"]==str(selected)')
s=s.replace('active["active_choice"]["selected_net_weight_kg"]=="8"','active["active_choice"]["selected_net_weight_kg"]==str(selected)')
s=s.replace('("ACCEPTED",8,10,15)','("ACCEPTED",selected,10,15)')
s=s.replace('(10,8)','(10,selected)').replace('(8,lot,src)','(selected,lot,src)').replace('q.fetchone()[0]==8','q.fetchone()[0]==selected')
start=s.index('  PickingService().cancel_plan(plan,"admin")')
end=s.index('\n finally:',start)
a=Path("scripts/ni042_weight_box_capacity_case.py").read_text(encoding="utf-8")
flow=a[a.index('  wave=picking.create_wave'):a.index('  q.execute("select RRL_STOCK_REPL_CAPACITY.unit_volume')]
flow='  picking=PickingService()\n'+flow
flow+='''  post("WAVE_PICK_RELEASE",{},{ "wave_id":wave})
  q.execute("select t.CASE_PICK_TASK_ID,l.CASE_PICK_LINE_ID,t.SSCC,l.CELL_CODE from RRL_CASE_PICK_TASK t join RRL_CASE_PICK_LINE l on l.CASE_PICK_TASK_ID=t.CASE_PICK_TASK_ID where t.PICK_WAVE_ID=:id",id=wave)
  case,line,carrier,cell=q.fetchone();case,line=int(case),int(line)
  q.execute("select u.PHYSICAL_UNIT_KEY,u.BASE_QTY from RRL_WMS_RECEIPT_UNIT u join RRL_STOCK_RESERVATION r on r.RESERVATION_ID=u.HARD_RESERVATION_ID where r.SOURCE_DOC_TYPE='PICK_WAVE'and r.SOURCE_DOC_ID=:p_wave and r.RESERVATION_DOMAIN='PICKING'and r.BASE_QTY>0",p_wave=wave)
  assert q.fetchall()==[(chosen["physical_unit_key"],selected)]
'''
tail=a[a.index('  q.execute("select PALLET_TYPE_ID'):a.index('  q.execute("select u.UNIT_ID')]
flow+=tail
flow+='''  operation="CASE.WEIGHT197:"+str(case)
  pick_body={"operation_id":operation,"scan_cell":cell,"scan_container":carrier,"weighted_box_barcode":labels[0 if selected==8 else 1]}
  result=request(f"/tasks/{case}/lines/{line}/weighted-box",pick_body)
  assert request(f"/tasks/{case}/lines/{line}/weighted-box",pick_body)==result
  q.execute("select PICKED_QTY from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=:p_line",p_line=line);assert q.fetchone()[0]==selected
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=:p_ware",p_ware=ware);assert q.fetchone()==(20,selected)
  print("PASS197 original10/planned",selected,"exact physical HARD",chosen["physical_unit_key"],"storage replenishment/full source20/actual CASE pick/replay/P20-Hactual",operation,flush=True)
'''
s=s[:start]+flow+s[end:]
s=s.replace('  for plan in plans:\n   PickingService().cancel_plan(plan,"admin")','''  for plan in plans:
   PickingService().cancel_plan(plan,"admin")
  from app.modules.inventory.infrastructure.weighted_planning import WeightedPlanning
  q.execute("select CHOICE_ID from RRL_PICK_WEIGHT_CHOICE where CUSTOMER_ORDER_ID=:p_order and STATUS in('ACCEPTED','USED')",p_order=order)
  for(choice_id,)in q.fetchall():WeightedPlanning(OracleGateway()).cancel(choice_id,"Retire owned197 source after native task cancellation","admin")
  q.execute("update RUSERS set DELETED=1 where ID=:p_actor",p_actor=approver);c.commit()''')
print(json.dumps({"scripts/ni042_weight_unit_pin_case.py":s},ensure_ascii=True))
