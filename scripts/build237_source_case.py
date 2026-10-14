from pathlib import Path
import json
s=Path("scripts/ni062_marked_custody_case.py").read_text(encoding="utf-8")
s=s.replace('approval="RET231.LEGACY:"+tag','approval="RET237.SUPPLIER:"+tag').replace('driver_actor="DR233"+tag','driver_actor="DR237"+tag')
needle=' q.execute("select a.RECEIPT_OPERATION_ID'
setup=""" dossier=api(admin,"GET","/api/delivery/store-returns/STORE229.RECEIVE:"+tag+"0")
 q.execute("select count(*)from RRL_STORE_RETURN_APPROVAL where OPERATION_ID=:p",p=approval)
 if not q.fetchone()[0]:
  api(admin,"POST","/api/delivery/store-returns/STORE229.RECEIVE:"+tag+"0/approve",{"operation_id":approval,"line_no":1,"quantity":"1","disposition":"SUPPLIER","reason":"Own237 exact originally accepted unit returned to supplier","decision_reference":"DEV237:"+tag,"unit_keys":[dossier["units"][0]["key"]]})
"""
s=s.replace(needle,setup+needle,1)
s=s.replace('receipt,line,uid,article,uom,qty,disposition,trip,plate,driver=q.fetchone();ware=51365792;',"""receipt,line,uid,article,uom,qty,disposition,trip,plate,driver=q.fetchone()
 q.execute("select tt.ID,tt.TRANSPORT,tt.VODITEL_ID from RRL_TRANSPORT_TASK tt where tt.ID=33546");trip,plate,driver=q.fetchone()
 ware=51365792;""",1)
s=s.replace('RET233.','RET237.').replace('RETURN233:','RETURN237:').replace('RET233:','RET237:').replace('(3,10,10)','(2,10,10)')
s=s.replace('PASS233','PASS237 source').replace('Own233','Own237').replace('cell="QR233"+tag','cell="QR233"+tag')
print(json.dumps({"scripts/ni062_marked_supplier_source_case.py":s},ensure_ascii=True))
