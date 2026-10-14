from pathlib import Path
import json,hashlib
p=Path('db/migrations/2026-10-14_ni051_scoped_quality');files={str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in p.rglob('*.sql')};(p/'installed_manifest.json').write_text(json.dumps({'migration_id':'2026-10-14-1447-ni051-scoped-quality','state':'APPLIED','files':files,'original_checkpoint':'checkpoint.json retained; final applied source hashes recorded here','gate_checkpoint_caveat':'codex/QC_F1/REPORT.md documents reconstructed interim gate; original migration saved sources retained'},indent=2)+'\n',encoding='utf-8')
p=Path('wiki/requirements/retailcase_delivery_v55/implementation_plan.json');d=json.loads(p.read_text(encoding='utf-8'));d['planRevision']=72;d['currentSprint']=None;d['currentSprintMeaning']='Выявленные обязательные функциональные разрывы рабочего окна закрыты. Все18 спринтов имеют реализованные срезы; полная независимая/внешняя/промышленная приёмка не объявляется завершённой. Отдельный performance-критерий NI02.2 остаётся.';d['firstChange']='NI05.1 scoped rules/storage proof/immutable exemption/label guard and NI08.1 native route/rest final approval delivered in RABAEV.';d['deliveryReadinessReport']='reports/retailcase/2026-10-13/67-sprint-code-readiness.md';d['parallelAssignment']['subordinateActive']='RELEASE: assigned implementation blocks complete; no active file ownership';d['allSprintsAccepted']=False
for x in d['increments']:
 x['deliveryCodeStatus']='implemented_scoped_delivery_independent_acceptance_pending'
 x['status']='implemented_pending_full_acceptance'
 x['deliveryOwner']='root / subordinate Codex; assigned code blocks released'
 x['architectureGate']='PASS_759_files_0_cycles_73_debt_24_tests_admin_terminal_typescript'
 if x['id']=='NI05.1':
  x['latestDeliveryReport']='reports/retailcase/2026-10-13/65-ni051-scoped-quality.md'
  x['remainingDeliveryWork']='Адресные правила, whole/storage proof, native QC audit/replay и запрет этикетки без записанного основания реализованы. Независимая полная приёмка и оборудование отдельно.'
  x['independentReviewStatus']='scoped_review_F1_fixed_and_root_integrated; full independent acceptance pending'
 if x['id']=='NI03.2':x['remainingDeliveryWork']='Цепочка, частичный остаток, назначения, пополнение и продолжение реализованы. Независимый полный маркированный/аппаратный маршрут отдельно.'
 if x['id']=='NI03.3':x['remainingDeliveryWork']='Заказ/волна, факт/остаток, смешанное исполнение/возврат и продолжение реализованы. Независимый составной маршрут и внешние подтверждения отдельно.'
 if x['id']=='NI04.1':x['remainingDeliveryWork']='Дерево HU, whole move, unpack/repack и physical slots реализованы. Независимые сочетания маркировки/нескольких мест и оборудование отдельно.'
for stream in d['sprints']:
 children=[x for x in d['increments'] if x['stream']==stream['id']]
 stream['status']='implemented_pending_full_acceptance'
 stream['changeRequired']='; '.join(x['remainingDeliveryWork'] for x in children)
 stream['pendingSlices']=[x['remainingDeliveryWork'] for x in children]
 stream['acceptanceStatus']='not_full_business_acceptance'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=Path('wiki/requirements/retailcase_delivery_v55/implementation_plan.md');p.write_text('''> Редакция72: назначенные кодовые блоки ведущего и ведомого сданы. NI05.1 адресные правила/storage-proof/аудит/печать и NI08.1 общий маршрут с перерывами применены. [Сводка18 спринтов](../../../../reports/retailcase/2026-10-13/67-sprint-code-readiness.md). Все спринты полностью принятыми **не объявляются**: независимая/внешняя/промышленная приёмка и performance NI02.2 перечислены отдельно. Исторические next-записи ниже не являются повторным поручением.

'''+p.read_text(encoding='utf-8'),encoding='utf-8')
p=Path('reports/retailcase/2026-10-13/67-sprint-code-readiness.md');s=p.read_text(encoding='utf-8').replace('Завершение отчёта native positive ведомого; независимая приёмка/весы','Native positive/аудит/повтор завершены; независимая приёмка/весы').replace('итог NI05.1 подтверждается отдельным отчётом ведомого','итог NI05.1 подтверждён codex/QC_F1/REPORT.md');s+='\nNI05.1 финальная интеграция: weight_exemption_recorded и индекс DOCUMENT_ID применены/VALID; label409 до записанного основания,200 после. Все изменённые Oracle-объекты VALID, общий gate повторён после изменения API — PASS. Свежий промежуточный export gate у ведомого не состоялся; реконструкция явно помечена в QC_F1/REPORT.md, исходный rollback всего блока сохранён.\n';p.write_text(s,encoding='utf-8')
p=Path('wiki/database/retailcase_ni051_scoped_policy_20261014.md');s=p.read_text(encoding='utf-8');s=s.replace('Применена в dev; завершение storage-proof и положительного native release в работе.','Применена в dev; storage-proof и положительный native QC завершены.');s+='''

## Завершение

F1 исправлен и проверен ведущим: existing fullpal binding, DONE task, immutable same-identifier movement, exact qty/UOM/current version. Реальный SAP3EA → putaway1169 → fullpal1168 → bind → QC PLAN ready/audit1/replay; cleanup собственных P/H0, история сохранена. [Итог ведомого](../../reports/retailcase/2026-10-13/codex/QC_F1/REPORT.md).

Добавлен RRL_QC_EXEMPT_DOCUMENT_IX(DOCUMENT_ID), VALID. status_json возвращает weight_exemption_recorded только для текущих ST/signature. Этикетка освобождённой паллеты требует этот факт; GET не создаёт записи. apply включает007, rollback сохраняет additive index/history. installed_manifest.json фиксирует финальные SQL; первоначальный checkpoint не переписан. Оговорка о реконструированном промежуточном gate checkpoint явно сохранена в отчёте ведомого. Gate759/0/73,24теста/обаTS PASS после финального API.
''';p.write_text(s,encoding='utf-8')
p=Path('wiki/requirements/retailcase_joint_execution_20261014.md');s=p.read_text(encoding='utf-8');s='> Итог редакции72: назначенные блоки обоих исполнителей RELEASE. NI05.1 native positive/audit/label guard завершён; [сводка18 спринтов](../../reports/retailcase/2026-10-13/67-sprint-code-readiness.md) отделяет код от приёмки. Активных поручений ведомому нет.\n\n'+s;p.write_text(s,encoding='utf-8')
p=Path('coordination/retailcase-codex/TASK_CURRENT.md');s=p.read_text(encoding='utf-8');p.write_text('> RELEASE: назначенные блоки выполнены, включая NI08.1 и NI05.1 F1/native positive/recorded audit. Итог: reports/retailcase/2026-10-13/codex/QC_F1/REPORT.md. Владение runtime-файлами передано ведущему; активных задач нет. Ниже сохранено исполненное поручение.\n\n'+s,encoding='utf-8')
p=Path('reports/retailcase/2026-10-13/65-ni051-scoped-quality.md');s=p.read_text(encoding='utf-8');p.write_text('> Итог: реализация блока завершена, включая F1 и запись основания до этикетки. Подробности завершения — codex/QC_F1/REPORT.md. Промежуточные pending ниже отражают ход работы; полная внешняя приёмка не заявляется.\n\n'+s,encoding='utf-8')
p=Path('wiki/index.md');p.write_text('- [Итог совместного исполнения —18 спринтов](../reports/retailcase/2026-10-13/67-sprint-code-readiness.md): редакция72, назначенные кодовые блоки обоих исполнителей RELEASE; NI05.1 native audit/label guard и NI08.1 route/rest применены. Внешняя/независимая приёмка и performance NI02.2 отдельно.\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
with Path('wiki/log.md').open('a',encoding='utf-8') as f:f.write('\n- 2026-10-14: редакция72/report67: ведомый RELEASE NI05.1 F1/nativepositive/recorded status и NI08.1. Root интегрировал label guard409/200 и понятное основание, gate759/0/73,24теста/обаTS PASS. Ownfixture P/H0, audit1/replay. Все спринты полностью принятыми не объявлены; внешние/независимые условия и широкий ST performance сохраняются. Interim gate checkpoint реконструирован и явно отмечен; исходный migration rollback сохранён. GitHub не публиковался.\n')
