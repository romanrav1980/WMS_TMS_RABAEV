from pathlib import Path
import json,re
out={}
for name,text in [('receive390_initial.py','Accepted one of three original marked units; two missing'),('receive396_initial.py','Accepted one of two returned original marked units; one missing')]:
 p=Path('scripts/'+name);t=p.read_text(encoding='utf-8');t=re.sub(r'discrepancy_reason="[^"]*"',lambda m:'discrepancy_reason='+json.dumps(text),t,count=1);out[p.as_posix()]=t
p=Path('scripts/prepare398_cycle.py');t=p.read_text(encoding='utf-8')
lines=[]
for line in t.splitlines():
 if '\ufffd'in line:
  matches=list(re.finditer(r'"[^"]*"',line))
  for match in reversed(matches):
   if '\ufffd'in match.group():line=line[:match.start()]+json.dumps('Own exact accepted and recovered original units')+line[match.end():]
 lines.append(line)
out[p.as_posix()]='\n'.join(lines)+'\n'
print(json.dumps(out))
