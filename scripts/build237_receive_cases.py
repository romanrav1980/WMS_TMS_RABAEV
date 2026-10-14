from pathlib import Path
import json
s=Path("scripts/ni062_marked_return_receiving_case.py").read_text(encoding="utf-8").replace('pickup="RET233.PICKUP:"+tag','pickup="RET237.PICKUP:"+tag').replace('approval="RET231.LEGACY:"+tag','approval="RET237.SUPPLIER:"+tag').replace('uid="RETURN233:"+tag','uid="RETURN237:"+tag').replace('cell="QR233"+tag;second="QS234"+tag','cell="QS234"+tag;second="QR233"+tag').replace('RET234.','RET237.').replace('(3,10,10)','(2,10,10)').replace('==3','==2').replace('==2\n q.execute("select count(*)from RRL_EVENTS','==1\n q.execute("select count(*)from RRL_EVENTS').replace('PASS234','PASS237 receiving')
t=Path("scripts/ni062_marked_return_placement_case.py").read_text(encoding="utf-8").replace('receipt="RET234.RECEIVE:"+tag+"1";','receipt="";').replace('uid="RETURN233:"+tag','uid="RETURN237:"+tag').replace('source="QR233"+tag','source="QS234"+tag').replace('target="QD235"+tag;supplier="QT235"+tag','target="QT235"+tag;supplier="QD235"+tag')
# Existing policy supplier target must remain QT235, disposal QD235.
t=t.replace('"supplier_target_cell":supplier,"disposal_target_cell":target','"supplier_target_cell":target,"disposal_target_cell":supplier')
t=t.replace(' q=c.cursor();c.call_timeout=15000;',' q=c.cursor();c.call_timeout=15000;\n q.execute("select OPERATION_ID from RRL_STORE_RETURN_RECEIPT where PICKUP_OPERATION_ID=:p",p="RET237.PICKUP:"+tag);receipt=q.fetchone()[0]\n ')
t=t.replace('RET235.','RET237.PUT.').replace('PASS235','PASS237 placement')
print(json.dumps({"scripts/ni062_marked_supplier_receive_case.py":s,"scripts/ni062_marked_supplier_place_case.py":t},ensure_ascii=True))
