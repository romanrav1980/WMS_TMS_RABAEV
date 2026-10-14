# NI03.3: рабочее место фактического исполнения волны

860–864 сохраняют существующие GET execution / POST finish-execution и native WAVE_EXECUTION_FINISH. Никакой второй реализации запуска/отгрузки/остатка не вводится.

Wave-execution controller, view и scoped intent разделены. Выбранная волна обновляет панель; прямой wave_id открывает исполнение даже вне первых100 строк очереди. Таблица причин содержит ссылки на реальные warehouse tasks. Потребность planning остаётся отдельно от отгруженного факта. Исторические причины у DONE подписаны как исторические; кнопки нового завершения запрещены.

Read responses сверяются с номером волны и actor/API scope; stale response игнорируется. Saved pending schema whitelist разрешает только wave, operation_id и допустимые disposition/reason. Пока есть pending, новый body/волна не создаются. Cross-tab raw compare и scope compare сохраняют исходник. POST success должен подтвердить ту же wave/operation/DONE/completed; потерянный/неподходящий ответ сохраняет исходный запрос. Повреждённый raw блокирует writes; архив сохраняет исходник до удаления и server reread.

Progress panel теперь показывает таблицу per-SKU BASE: demand/planned/confirmed/unfulfilled/pick remaining/capacity. Selection и identity guards, явный лимит50; отсутствие rows не объявляется исполнением заказа. Панели перенесены внутрь рабочего layout.

Фактический read859 / browser863 для защищённой wave403: DONE, warehouse839 DONE3, cancelled original order1930/line3415 planning1EA. Команды не отправлялись, данные не менялись. Screenshot11 — реальный браузер до финального CSS/подписи historical; не заявлять новый native end-to-end. JS861 PASS intent malformed/other-tab/context/archive. Разработчик, не независимая приёмка спринта.

SQL857 по последнему NI03.2 case: canonical projection17.832ms/136 buffers, cancel12.596ms, partial12.291ms/184 buffers; continuation2.783ms. Более старый projection102ms/241buffers: сохраняем bounded windows, владелец resources; при устойчивом>500ms проверить план/статистику. Новые индексы не обоснованы.

1092: bounded current wave read adds CASE currentcell/carrier/version and actual existing ST control identifier in same READONLY snapshot after scope. UI links to existing composition/QC, per-item picking history labelled separately from currentstock. No QC/stock/wave status writes; actual runtime/current source553 andbrowser next. Owner inventory, same existing Root finish command, no second quality module.

1098: native/currentHTTP1093 PASS; CASE20/13 sameQCversions, P20H20/553 notready. Browser34 waveactions/37 actualQC layout;1097 response/readonly/cross-tab/lateactor PASS. [Отчёт28](../../reports/retailcase/2026-10-13/28-wave-qc-workflow-report.md). No QC writes/greenadmission/hardware/independent closure. DamagedQC intent recovery next.
