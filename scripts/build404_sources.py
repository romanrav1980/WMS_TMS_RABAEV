from pathlib import Path
import json
base=Path('scripts/source334_marked_case.py').read_text(encoding='utf-8')
out={}
for number in (404,405):
 t=base.replace('334',str(number))
 start=t.index('  loading_context=')
 end=t.index(' finally:',start)
 tail='''  context=dict(tag=tag,article=article,lot=lot,warehouse=ware,shipcell=shipcell,src=src,dst=dst,task=task,st=st,st_uid=st_uid,order=order,wave=wave,vehicle=vehicle,dock=dock,source_trip=trip,barcode=gtin,units=units,ff=ff,driver=driver,trtype=trtype)
  Path("tmp/contextNUMBER.json").write_text(json.dumps(context,indent=2),encoding="utf-8")
  print("SOURCE_NUMBER picked3/QC/currentP3H3; not loaded, group preparation next")
'''
 t=t[:start]+tail.replace('NUMBER',str(number))+t[end:]
 if number==405:
  t=t.replace('ware=100000+int(tag[:6],16);shipcell="QH"+tag;','first=json.loads(Path("tmp/context404.json").read_text(encoding="utf-8"));ware=first["warehouse"];shipcell=first["shipcell"];')
  t=t.replace('meta("insert into RRL_WARES(ID,NAME,PREFIX) values(:ware,:n,:p)",n="Own FULLPAL HU "+tag,p="Q"+tag[:2])','')
  t=t.replace('meta("insert into RRL_RECEIPT_WARE_SETTINGS(WARE_ID,OUTGOING_QC_MODE,OUTGOING_QC_INDEPENDENT) values(:ware,\'NONE\',0)")','')
  t=t.replace(' for cell in (src,dst,shipcell):',' for cell in (src,dst):')
  t=t.replace('for system,profile in[("CRPT","TOBACCO"),("EGAIS","ALCOHOL")]:','for system,profile in[("CRPT","TOBACCO")]:')
  needle=' q.execute("select min(CUSTOMER_ID)'
  t=t.replace(needle,' for unit in units:unit["codes"]=unit["codes"][:1]\n'+needle,1)
  marker='  scan_aggregations=[dict(system_code="CRPT"'
  lines=t.splitlines()
  for i,line in enumerate(lines):
   if line.startswith(marker):lines.insert(i+1,'  scan_aggregations=scan_aggregations[:1]');break
  t='\n'.join(lines)+'\n'
 out['scripts/source'+str(number)+'_group.py']=t
print(json.dumps(out))
