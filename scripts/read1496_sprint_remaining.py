import json
from pathlib import Path
p=json.loads(Path('wiki/requirements/nikora_delivery_v55/implementation_plan.json').read_text(encoding='utf-8-sig'))
for s in p['sprints']:
 print(s['id'],s['status'])
 print(' change:',s.get('changeRequired'))
 for k in ('remaining','remainingWork','blockers','acceptanceStatus'):
  if k in s: print(k,s[k])
