from pathlib import Path
import json
p=Path('wiki/requirements/retailcase_delivery_v55/implementation_plan.json');b=json.loads(p.read_text(encoding='utf-8'))
b['currentSprint']='NI08.1';b['currentWork']['root']='Four store/fleet/route migrations installed, native/API scenarios PASS; integrate final UI and reconcile sprint code readiness'
b['parallelAssignment']['subordinateActive']='Fleet outer and native store access RELEASE; installed and native PASS'
b['parallelAssignment']['additionalSubordinate']='Weekly route native RELEASE; installed, preview/final/hash PASS'
b['parallelAssignment']['externalClaude']='C0029 live PASS, C0032 correction PASS; C0033 final metadata and C0034 night Gantt in progress'
b['latestDelivery']['reports']=['68-ni022-narrow-header-group.md','69-ni043-gateway-deferred.md','70-geofences-gps.md','71-store-fleet-route-integration.md']
b['latestDelivery']['claudeCompleted']='C0029 live K0037; C0032 malformed response correction K0037'
b['latestDelivery']['claudeNext']='coordination/retailcase-claude/TASK_C0034.md'
for i in b['increments']:
 if i['id']=='NI05.1':
  i['status']='implemented_pending_full_acceptance';i['changeRequired']='Scoped QC and real store profile API/UI implemented; 56 windows/replay/conflicts verified. Independent acceptance separate.'
 if i['id']=='NI08.1':
  i['status']='in_progress';i['changeRequired']='Native weekly route/fleet-store hash/current outer limits installed and verified. Remaining code: C0033 final same-snapshot UI and C0034 night Gantt.'
 if i['id']=='NI04.3':i['changeRequired']='Local marking implemented. Government gateway deferred by owner; no fake external ACK.'
b['allSprintsAccepted']=False
p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=Path('reports/retailcase/2026-10-13/71-store-fleet-route-integration.md');s=p.read_text(encoding='utf-8');s+='\nДополнение: live C0029 через API завершён (WEEKLY, replay, payload/version conflicts, 56 интервалов, отказ57/unknownTZ, восстановление исходного новойверсией). K0037. Root real GET33641:151мс, профиль/неделя изтого же snapshot; все4миграции APPLIED, INVALID0. Остаток UI: C0033 окончательные подписи/метаданные, C0034 ночная Ганта.\n';p.write_text(s,encoding='utf-8')
p=Path('wiki/database/retailcase_store_profile_20261014.md');s=p.read_text(encoding='utf-8').replace('Живой API/UI случай C0029 выполняет Claude на собственном адресе; независимая приёмка отдельно.','Живой API случай C0029 завершён на собственном Own264: версия/повтор/конфликты, 56окон безобрезания, восстановление исходного новойверсией; K0037. Независимая приёмка отдельно.');p.write_text(s,encoding='utf-8')
