from pathlib import Path
import json
s=Path("scripts/ni033_case_http_close_flow.py").read_text(encoding="utf-8").replace("167","209")
s=s.replace('lot="CASE209.QA:"','article2=article+"B";dst2="Q209E"+tag;lot2="CASE209.B:"+tag\nlot="CASE209.QA:"')
needle=' q.execute("select count(*)from RRL_WARES where ID=:id",id=ware)'
extra=''' meta("declare x RRL_ARTICULS%rowtype;begin select *into x from RRL_ARTICULS where ACTICUL=:old;x.ACTICUL:=:article;x.BARCODE_SHT:=:barcode;insert into RRL_ARTICULS values x;end;",old=article,article=article2,barcode="BC209B"+tag)
 meta("insert into RRL_STOCK_UOM_CONVERSION(ARTICUL,INPUT_UOM,BASE_UOM,POLICY_VERSION,NUMERATOR,DENOMINATOR,BASE_SCALE,PROVENANCE)select :article,INPUT_UOM,BASE_UOM,POLICY_VERSION,NUMERATOR,DENOMINATOR,BASE_SCALE,'Own209 second route point'from RRL_STOCK_UOM_CONVERSION where ARTICUL=:old",article=article2,old=article)
 meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('SKU',:article),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",article=article2)
'''
assert needle in s;s=s.replace(needle,extra+needle)
s=s.replace('for cell in(src,dst,"CPT_"','for cell in(src,dst,dst2,"CPT_"').replace('pick=int(cell==dst)','pick=int(cell in(dst,dst2))')
needle=' revision=int(q.callfunc("REVIZION.create_revizion"'
extra=''' meta("update RRL_PICK_FACE set PICK_SEQUENCE=1 where PICK_FACE_ID=:id",id=face)
 face2=seq("RRL_PICK_FACE_SQ")
 meta("insert into RRL_PICK_FACE(PICK_FACE_ID,WARE_ID,CELL_CODE,PICK_SEQUENCE,MAX_VOLUME,CREATED_BY)values(:id,:ware,:cell,2,.2,'admin')",id=face2,ware=ware,cell=dst2)
 meta("insert into RRL_PICK_FACE_ARTICUL(PICK_FACE_ARTICUL_ID,PICK_FACE_ID,ARTICUL,BOX_VOLUME_M3,USE_ARTICUL_REPLENISH_RULE,REPLENISHMENT_QTY_MODE)values(RRL_PICK_FACE_ARTICUL_SQ.nextval,:face,:article,.24,0,'FULL_PALLET')",face=face2,article=article2)
'''
assert needle in s;s=s.replace(needle,extra+needle)
needle='  q.execute("select min(CUSTOMER_ID)from RRL_CUSTOMER")'
extra='''  post("INVENTORY_REGISTER_LOT",{"uid":lot2,"cell":src,"article":article2,"quantity":"2","expiry_date":"2030-01-01","price":0,"reason":"Own209 second physical route point"},{"revision_id":revision})
'''
s=s.replace(needle,extra+needle)
needle='  picking=PickingService();'
extra='''  meta("insert into RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,LINE_NO,ARTICUL,ORDER_QTY,UNIT_CODE)values(RRL_CUSTOMER_ORDER_ROW_SQ.nextval,:order_id,2,:article,1,'EA')",order_id=order,article=article2)
'''
s=s.replace(needle,extra+needle)
s=s.replace('assert q.fetchone()[0]=="CASE_PICK"','assert q.fetchall()==[("CASE_PICK",),("CASE_PICK",)]')
needle='  case,line,carrier,cell=q.fetchone();case,line=int(case),int(line)'
replace='''  source_rows=q.fetchall();assert len(source_rows)==2
  q.execute("select l.CASE_PICK_LINE_ID,l.CELL_CODE,l.PICK_SEQUENCE,l.ARTICUL,t.CASE_PICK_TASK_ID,t.SSCC from RRL_CASE_PICK_LINE l join RRL_CASE_PICK_TASK t on t.CASE_PICK_TASK_ID=l.CASE_PICK_TASK_ID where t.PICK_WAVE_ID=:id order by l.PICK_SEQUENCE",id=wave)
  first,second=q.fetchall();assert first[2]==1 and second[2]==2 and first[1]==dst and second[1]==dst2 and first[4]==second[4]
  line,cell,_,_,case,carrier=first;case,line=int(case),int(line)
  # Future slotting changes do not rewrite the issued route.
  meta("update RRL_PICK_FACE set PICK_SEQUENCE=99 where PICK_FACE_ID=:id",id=face)
'''
assert needle in s;s=s.replace(needle,replace)
needle='  result=request(f"/tasks/{case}/lines/{line}/confirm",body)'
extra='''  ahead={**body,"operation_id":"CASE209.AHEAD:"+str(case),"offline_event_id":"CASE209.AHEAD:"+str(case),"scan_cell":second[1],"scan_product":article2}
  rejected=api.post(base+f"/tasks/{case}/lines/{second[0]}/confirm",json=ahead)
  assert rejected.status_code==409 and "CASE_ROUTE_EARLIER_POINT_UNFINISHED"in rejected.text,(rejected.status_code,rejected.text[:1200])
  q.execute("select nvl(sum(PICKED_QTY),0)from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=:id",id=case);assert q.fetchone()[0]==0
'''
s=s.replace(needle,extra+needle)
needle='  q.execute("select STATUS,CLOSED_AT,CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",id=case);state=q.fetchone()'
extra='''  ahead["operation_id"]="CASE209.SECOND:"+str(case);ahead["offline_event_id"]=ahead["operation_id"]
  second_result=request(f"/tasks/{case}/lines/{second[0]}/confirm",ahead)
  assert request(f"/tasks/{case}/lines/{second[0]}/confirm",ahead)==second_result
  q.execute("select nvl(sum(PICKED_QTY),0)from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=:id",id=case);assert q.fetchone()[0]==2
  print("PASS209 distinct physical cells/frozen ranks1then2/futureface99 does not rewrite issued1/next point refused before first/native stock picks1+1/each replay",case,dst,dst2,flush=True)
'''
assert needle in s;s=s.replace(needle,extra+needle)
s=s.replace('assert q.fetchone()==(2,1)','assert q.fetchone()==(4,2)')
s=s.replace('where p.ARTICUL=:article and r.REMAIN>0",article=article)','where p.ARTICUL in(:article,:article2) and r.REMAIN>0",article=article,article2=article2)')
s=s.replace('for uid,cell,unit,version in q.fetchall()]','for uid,cell,unit,version in q.fetchall()]')
# Native inventory count requires the actual article of each leaf.
s=s.replace('select r.UID_POLETA,r.CELL,r.BASE_UOM,r.STOCK_VERSION from','select r.UID_POLETA,r.CELL,r.BASE_UOM,r.STOCK_VERSION,p.ARTICUL from')
s=s.replace('"article":article,"unit":unit','"article":count_article,"unit":unit').replace('for uid,cell,unit,version in q.fetchall()]','for uid,cell,unit,version,count_article in q.fetchall()]')
print(json.dumps({"scripts/ni042_issued_route_case.py":s},ensure_ascii=True))
