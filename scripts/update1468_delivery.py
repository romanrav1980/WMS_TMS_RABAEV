from pathlib import Path
import json
root=Path('.')
p=root/'coordination/retailcase-codex/TASK_CURRENT.md'
p.write_text('''# Поручение ведомому Codex — завершение NI05.1

Ведущий: /root. Ведомый: /root/codex_finance. Обмен: сообщения агента и эта папка. Общий план и интеграция остаются у ведущего.

NI08.1-R1 сдан: единый Oracle-расчёт маршрута с перерывами, preview и окончательное утверждение ручного/автоматического рейса. Отчёт: reports/retailcase/2026-10-13/codex/NI081/REPORT.md.

Текущая задача: устранить F1 независимого review — освобождение по штрихкоду хранения требует существующего подтверждённого PICK_PALLET_BIND_SHIPMENT, а не только целой исходной паллеты. Владение: exemption_json в db/migrations/2026-10-14_ni051_scoped_quality/002_reader.sql; собственные scripts/report. Применение reader ведущим разрешено, обязательно проверить live compilation.

Довести один положительный native сценарий: SAP receipt → физический whole-pallet pick → существующая привязка к СТ → QC PLAN → основание освобождения в том же Root. Повтор сохраняет исходный результат; неизвестное/частичное происхождение не даёт исключение. Использовать маленький собственный dev-набор и прежние команды, без копии базы. Не подделывать журналы. Сохранить точные P/H и ограничения результата; очистка своих остатков только через Root.

Root владеет API/UI правил, общими wiki/index/log/планом, quality gate и SQL страниц СТ. Общие файлы без handoff не менять. GitHub не публиковать.
''',encoding='utf-8')
p=root/'wiki/requirements/retailcase_delivery_v55/implementation_plan.json';d=json.loads(p.read_text(encoding='utf-8'));d['planRevision']=71;d['currentSprint']='NI05.1';d['firstChange']='NI05.1 scoped QC rules implemented; storage barcode proof and native positive release in progress. NI08.1 common native route/rest final approval delivered.';d['currentSprintMeaning']='Завершение адресных правил QC и основания освобождения; NI08.1-R1 сдан. Остальные готовые функции не переписываются ради прежних исторических next-записей.';d['parallelAssignment']['subordinateActive']='NI05.1 F1 storage proof + native positive QC release';d['parallelAssignment']['externalClaude']='C0018/C0021/C0020 RELEASE; C0023 completed by subordinate Codex'
updates={
'NI06.2':('reports/retailcase/2026-10-13/codex/NI062/report.md','Принятый возврат связан с точной очередью размещения; фильтр receipt_operation_id применяется до ограничения100. Повреждённые команды/сканы защищены. Внешние ACK и независимая приёмка отдельно.'),
'NI06.3':('reports/retailcase/2026-10-13/codex/FINAL_FOUR_SCOPE_20261014.md','LOSS WRITE_OFF уже реализован, повторная разработка не нужна. Приёмка физической передачи и независимая сверка держателей отдельно.'),
'NI07.1':('reports/retailcase/2026-10-13/codex/FINAL_FOUR_SCOPE_20261014.md','Периодные источники, нормативы, допрасходы, согласование, корректировки и счета реализованы. Нужны реальные финансовые mapping/ACK и коммерческие ставки; это отдельная внешняя приёмка.'),
'NI08.1':('reports/retailcase/2026-10-13/codex/NI081/REPORT.md','NI08.1-R1 реализован: общий native маршрут с REST, свежая дорога/окна/дневная занятость и финальное утверждение. Внешние нормативы, дорожный провайдер, предшествующая занятость и независимая приёмка отдельно.'),
'NI05.1':('reports/retailcase/2026-10-13/codex/QC_SCOPE_REVIEW_20261014.md','Правила склад/подсклад/магазин/категория, версии, журнал и UI реализованы. Завершить отдельное доказательство storage-barcode и положительный native QC с записью основания освобождения.'),
'NI02.2':('reports/retailcase/2026-10-13/53-ni022-st-page-index.md','Функции ограничений/типов/времени и страницы СТ реализованы; общий временной допуск NI08.1-R1 сдан. Широкая история имеет переменное время1.685–8.3с; постоянные<2с не доказаны, рабочий UI использует период/страницы. Не применять ухудшающий NL hint (6.631с).')}
for x in d['increments']:
 x['architectureGate']='shared_gate_759_running'
 if x['id'] in updates:x['latestDeliveryReport'],x['remainingDeliveryWork']=updates[x['id']]
 if x['id']=='NI08.1':x['deliveryCodeStatus']='implemented_native_route_rest_targeted_verified'
 if x['id']=='NI05.1':x['deliveryCodeStatus']='implemented_storage_proof_native_release_in_progress'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=root/'wiki/requirements/retailcase_delivery_v55/implementation_plan.md';p.write_text('> Редакция71: NI08.1 единый маршрут с перерывами реализован. Текущий NI05.1 — адресные правила и проверяемое основание освобождения; ведомый Codex завершает native positive. Актуальный остаток и отдельные статусы находятся в implementation_plan.json. Старые next-пункты ниже — история, не повторное поручение.\n\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
p=root/'wiki/requirements/retailcase_joint_execution_20261014.md';p.write_text('''# Совместное исполнение RETAILCASE — 14 октября 2026

Ведущий /root управляет контрактами, интеграцией, общим планом и приёмкой работы ведомого. Ведомый /root/codex_finance исполняет ограниченные задания с явным владением файлами. Канал: [coordination/retailcase-codex](../../coordination/retailcase-codex/TASK_CURRENT.md) и сообщения агента. Claude передал C0018/C0021/C0020; C0023 после его лимита завершил ведомый Codex.

| Ответственный | Выполненные блоки | Сейчас |
|---|---|---|
| Ведущий | NI03.2 цепочка/назначение, NI03.3 продолжение волны, NI04.1 дерево HU, NI04.2 short recovery, NI05.2 погрузка, NI07.2 полный реестр, NI05.1 связь контроля с рейсом и адресные правила | Интеграция NI05.1, конечные критерии, единый gate; решение по SQL страниц СТ |
| Ведомый Codex | NI01.1 ввод/сканы, NI04.2 draft, NI04.3 scans, NI05.3 акт, NI06.1 group recovery, NI06.2 точное размещение, NI07.2 keys, NI08.1 общий native маршрут/REST/final approval | NI05.1 F1: storage-identifier proof и один реальный native QC release |
| Claude Code | NI02.2 страницы/фильтры, NI06.3 тара, NI07.1 финансовый цикл и интерфейсы | Активных поручений нет, файлы переданы |

Все18 спринтов имеют работающие срезы; это не объявление полной приёмки. Конкретный открытый кодовый блок — NI05.1. У NI02.2 нет подтверждённого стабильного времени<2с по всей истории. Внешние SAP/государственные сервисы, оборудование и промышленная приёмка выделены отдельно и не блокируют разработку других функций.

Основания конечных критериев: [семь блоков ведомого](../../reports/retailcase/2026-10-13/codex/FINAL_BLOCK_CRITERIA_20261014.md), [четыре транспортно-финансовых блока](../../reports/retailcase/2026-10-13/codex/FINAL_FOUR_SCOPE_20261014.md), [реализация NI08.1](../../reports/retailcase/2026-10-13/codex/NI081/REPORT.md). Последний документ заменяет исторический R1-остаток второго.

Минимум80% усилий — функционал; проверки адресные. Общие файлы меняет один владелец, передача через ACK/RELEASE. Не создавать второй stock writer, allocator или систему идентификаторов. Публикация GitHub только по новому отдельному поручению.
''',encoding='utf-8')
p=root/'wiki/index.md';p.write_text('- [Совместное исполнение, редакция71](requirements/retailcase_joint_execution_20261014.md): NI08.1 native REST/final approval сдан; NI05.1 storage proof и положительный QC в работе. [Поручение ведомому](../coordination/retailcase-codex/TASK_CURRENT.md).\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
with (root/'wiki/log.md').open('a',encoding='utf-8') as f:f.write('\n- 2026-10-14: редакция71 устраняет устаревшие назначения. NI08.1-R1 сдан; scoped QC применён, F1 review требует отдельного storage proof/native release. UI recovery: одна history запись, правило отключеноv3, P3 сохранён, SQL1–13мс. Для широкого ST кандидат NL hint отвергнут:6.631с против1.685с существующего; постоянные<2с не заявляются.\n')
