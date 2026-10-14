from pathlib import Path
import json
p=Path('wiki/requirements/nikora_delivery_v55/implementation_plan.json');b=json.loads(p.read_text(encoding='utf-8-sig'));b['planRevision']=76
for i in b['increments']:
 if i['id']=='NI08.1':
  i['status']='implemented_pending_full_acceptance';i['changeRequired']='Native store/fleet/weekly route and C0032 recovery/C0033 schedule/C0034 night Gantt implemented. Final common gate PASS. External/pilot acceptance separate.'
  i['remainingDeliveryWork']='No assigned current-scope code gap remains. Real provider/legal/equipment and independent/pilot acceptance remain separate.'
for stream in b['sprints']:
 if stream['id']=='NI08':stream['status']='implemented_pending_full_acceptance'
b['completedFunctionalSprintCount']=18;b['remainingFunctionalSprintCount']=0;b['completedIncrementIds']=[i['id'] for i in b['increments']]
b['currentSprint']=None;b['activeExecutionOrder']=[];b['allCurrentScopeCodeImplemented']=True;b['allSprintsAccepted']=False
b['currentWork']={'root':'Current scope code completed; final common gate PASS and report73 saved','claudeQueue':[],'deferred':'Government Track and trace gateway per owner; external/equipment/independent/pilot acceptance separate'}
b['parallelAssignment']['externalClaude']='C0029-C0034 RELEASE, final corrections accepted; queue complete'
b['latestDelivery']['reports']=['71-store-fleet-route-integration.md','72-gantt-day-overlap.md','73-current-sprint-code-completion.md']
b['latestDelivery']['claudeCompleted']='C0029-C0034/K0040 RELEASE plus final reviewed corrections';b['latestDelivery']['claudeNext']=None
b['deliveryReadinessReport']='reports/nicora/2026-10-13/73-current-sprint-code-completion.md'
b['currentCodeCompletionEvidence']={'gate':'reports/nicora/2026-10-13/final_gate1512.log','architectureFiles':778,'cycles':0,'legacyDebtItems':73,'testsPassed':24,'adminTypeScript':'PASS','terminalTypeScript':'PASS','industrialAcceptance':False}
p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=Path('wiki/requirements/nikora_delivery_v55/implementation_plan.md');s=p.read_text(encoding='utf-8');s=s.replace('Редакция75','Редакция76')
s=s.replace('Из18 функциональных спринтов17 имеют реализованный текущий кодовый объём; NI08.1 завершает интерфейс маршрута и ночную Ганту.','Все18 функциональных спринтов имеют реализованный текущий согласованный кодовый объём. NI08.1 завершён: экран маршрута, восстановление утверждения и ночная Ганта приняты; общий gate PASS. Назначенных незавершённых кодовых задач нет.')
s=s.replace('Native реализован; C0033/C0034 UI завершаются','Реализован; native/API/UI и итоговый gate PASS')
a=s.index('## Текущие исполнители');z=s.index('## Отдельные условия приёмки',a)
s=s[:a]+'''## Итог совместного исполнения

Codex завершил Oracle/API/серверную выборку Ганта, интеграцию и общий gate. Claude завершил C0029–C0034, включая исправления итогового ревью. Ведомые Codex сдали fleet/access/weekly native блоки. Очередь текущего объёма пуста, все file locks освобождены. [Итог73](../../../reports/nicora/2026-10-13/73-current-sprint-code-completion.md); [скриншот](../../../reports/nicora/2026-10-13/claude/C0034/screenshots/g2b_real_card_route.png).

Условие завершения текущей разработки достигнуто до срока15.10.2026 07:00МСК. Новые задачи не создаются ради занятости; последующие реальные подключения/пилот имеют отдельный объём.

'''+s[z:]
p.write_text(s,encoding='utf-8')
