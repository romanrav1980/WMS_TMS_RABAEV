from pathlib import Path
import json
t=Path("scripts/source311_marked_case.py").read_text(encoding="utf-8").replace("311","385")
t=t.replace("'BOX',0.125","'BOX',1")
needle=' meta("insert into RRL_STOCK_POLICY_GUARD'
at=t.index(needle)
t=t[:at]+''' box_prefix="047"+str(int(tag,16)%10000000000).zfill(10);box_gtin=box_prefix+str((10-sum(int(n)*(3 if i%2==0 else 1)for i,n in enumerate(reversed(box_prefix)))%10)%10)
'''+t[at:]
needle='("E1BPE1MARMRT",dict(ALT_UNIT="EA",NUMERATOR="1",DENOMINATR="1",EAN_UPC=gtin))'
assert needle in t;t=t.replace(needle,needle+',("E1BPE1MARMRT",dict(ALT_UNIT="BOX",NUMERATOR="3",DENOMINATR="1",EAN_UPC=box_gtin))')
a=t.index('  target=ware+50000000;');b=t.index('\n finally:',a)
t=t[:a]+'''  q.execute("select BARCODE_KOR from RRL_ARTICULS where ACTICUL=:article",article=article);assert q.fetchone()[0]==box_gtin
  context={"tag":tag,"article":article,"lot":lot,"warehouse":ware,"source_load":shipop,"source_trip":trip,"barcode":gtin,"box_barcode":box_gtin,"source_quantity":"3","units":units,"aggregations":scan_aggregations,"sap_order_id":order_id,"order":order,"st":st,"st_uid":st_uid,"receive":receive,"pick":pick,"src":src,"dst":dst,"shipcell":shipcell,"vehicle":vehicle,"plate":"QL"+tag,"driver":driver,"supplier_batch":"PB385:"+tag,"expiry":"2030-01-01"}
  Path("tmp/context385.json").write_text(json.dumps(context,indent=2),encoding="utf-8")
  print("SOURCE385 actualSAP3EA/oneBOX3/customboxEAN/verifiedbatch/same3keys6codes/existing fullpalshipment/depart/sourceP0")
'''+t[b:]
print(json.dumps({"scripts/source385_marked_reuse.py":t}))
