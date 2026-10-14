from pathlib import Path
import re,json
paths=[Path("SQL/Перенос версий/копия от 21_11_2011.pdc"),Path("SQL/Перенос версий/Версия бд от 06.11.2011"),Path("WMS Эталон/Версия бд от 06.11.2011")]
for p in paths:
 b=p.read_bytes();text=b.decode("cp1251",errors="replace")
 hits=list(re.finditer("pall_splitter",text,re.I))
 print(json.dumps({"path":str(p),"bytes":len(b),"hits":len(hits),"prefix":repr(b[:20])}))
 for i,m in enumerate(hits[:4]):
  print(json.dumps({"position":m.start(),"context":text[max(0,m.start()-120):m.start()+750]},ensure_ascii=True))
