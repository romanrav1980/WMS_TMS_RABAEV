from pathlib import Path
import json
p=json.loads(Path("wiki/requirements/retailcase_delivery_v55/execution/execution_plan.json").read_text(encoding="utf-8-sig"))
print("TOP",list(p)[:30])
def walk(x):
 if isinstance(x,dict):
  if any(v in("NI01.1","NI03.3","NI08.1")for v in x.values()if isinstance(v,str)):print(json.dumps(x,ensure_ascii=False)[:5500])
  for v in x.values():walk(v)
 elif isinstance(x,list):
  for v in x:walk(v)
walk(p)
