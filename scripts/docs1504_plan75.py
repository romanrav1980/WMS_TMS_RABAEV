from pathlib import Path
import json
p=Path('wiki/requirements/retailcase_delivery_v55/implementation_plan.json');b=json.loads(p.read_text(encoding='utf-8-sig'))
b['planRevision']=75
b['continuationStopConditions']={'complete':'All current-scope sprint code results complete; external acceptance tracked separately','source':'Owner 14Oct: continue until all sprints complete or 15Oct07:00 Europe/Moscow, keep Claude queue supplied','deadlineMoscow':'2026-10-15T07:00:00+03:00'}
ready=[i['id'] for i in b['increments'] if i['status']=='implemented_pending_full_acceptance']
b['completionCountMeaning']='Implemented current-scope code results, not independent/external/production acceptance; deferred gateway excluded by owner decision'
b['completedFunctionalSprintCount']=len(ready);b['remainingFunctionalSprintCount']=len(b['increments'])-len(ready);b['completedIncrementIds']=ready
b['deliveryReadinessReport']='reports/retailcase/2026-10-13/71-store-fleet-route-integration.md'
b['activeExecutionOrder']=['NI08.1: C0033 final UI metadata','NI08.1: C0034 night Gantt','One integrated quality/encoding gate and final readiness report']
p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
