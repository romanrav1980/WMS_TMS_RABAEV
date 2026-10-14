from pathlib import Path
import re,json,hashlib
out={}
for p in Path(".").glob("SQL/Перенос версий/*"):
 if p.is_file():
  raw=p.read_bytes();text=raw.decode("cp1251",errors="replace")
  matches=list(re.finditer(r"create\s+or\s+replace\s+package\s+body\s+(?:RABAEV\.)?PALL_SPLITTER\b",text,re.I))
  print(json.dumps({"path":str(p),"sha256":hashlib.sha256(raw).hexdigest(),"bodies":len(matches)}))
  for m in matches:
   end=m.start()+re.search(r"(?m)^/\s*$",text[m.start():]).start()
   body=text[m.start():end+2]
   target=Path("tmp/legacy268")/(p.name+".splitter.sql");target.parent.mkdir(parents=True,exist_ok=True);target.write_text(body,encoding="utf-8")
   print(json.dumps({"extracted":str(target),"length":len(body),"commits":len(re.findall(r"\bcommit\b",body,re.I)),"functions":re.findall(r"function\s+(\w+)",body,re.I)}))
