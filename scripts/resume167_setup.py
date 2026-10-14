from pathlib import Path
p=Path(__file__).resolve().parents[1]/"scripts/ni033_case_http_close_flow.py"
s=p.read_text(encoding="utf-8").replace('import sys,json','import sys,json,re',1)
s=s.replace('lot="CASE167.QA:"+tag;', 'lot="CASE167.QA:"+tag+":"+uuid4().hex[:6];',1)
s=s.replace(' def meta(sql,**binds):\n  q.callproc', ''' def meta(sql,**binds):
  for key in sorted(binds,key=len,reverse=True):sql=re.sub(":"+re.escape(key)+r"\\b",":p_"+key,sql)
  binds={"p_"+key:value for key,value in binds.items()}
  q.callproc''',1)
a=s.index(' meta("insert into RRL_WARES');b=s.index(' for cell in',a)
part=s[a:b];s=s[:a]+''' q.execute("select count(*)from RRL_WARES where ID=:id",id=ware)
 if q.fetchone()[0]==0:
'''+''.join(' '+line for line in part.splitlines(keepends=True))+s[b:]
a=s.index('  meta("insert into RRL_CELLS');b=s.index(' face=seq',a)
part=s[a:b];s=s[:a]+'''  q.execute("select count(*)from RRL_CELLS where CELL=:id and WARE_ID=:ware",id=cell,ware=ware)
  if q.fetchone()[0]==0:
'''+''.join(' '+line for line in part.splitlines(keepends=True))+s[b:]
a=s.index(' face=seq');b=s.index(' revision=int',a)
part=s[a:b];s=s[:a]+''' q.execute("select count(*)from RRL_PICK_FACE f join RRL_PICK_FACE_ARTICUL a on a.PICK_FACE_ID=f.PICK_FACE_ID where f.WARE_ID=:ware and f.CELL_CODE=:cell and a.ARTICUL=:article",ware=ware,cell=dst,article=article)
 if q.fetchone()[0]==0:
'''+''.join(' '+line for line in part.splitlines(keepends=True))+s[b:]
p.write_text(s,encoding="utf-8")
