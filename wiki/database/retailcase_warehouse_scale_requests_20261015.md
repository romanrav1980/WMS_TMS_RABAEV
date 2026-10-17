# Очередь складских измерений и lease шлюза — 15.10.2026

Статус: серверная очередь APPLIED,14 statements/0 errors,6 source EXACT/INVALID0. Узкий [SQL-boundary follow-up](../../db/migrations/2026-10-15_warehouse_scale_request_sql_boundary/) APPLIED5/0, native/HTTP приёмка ниже; полный аппаратный sprint ещё не закрыт. Комплект: [2026-10-15_warehouse_scale_requests](../../db/migrations/2026-10-15_warehouse_scale_requests/). Предшествующие подтверждённые контракты: [[retailcase_ni042_warehouse_scale_20261011]], [[retailcase_ni042_small_final_weight_20261011]], [[retailcase_assembly_recovery_20261015]]. Шлюз: [[retailcase_warehouse_scale_gateway_20261015]].

## Граница операции

Оператор создаёт неизменяемое намерение измерить, без массы: устройство, PICK/EMPTY_TARE/FINAL_GROSS, фактический CASE, content version, сканы. Для FINAL дополнительно необходимы архивная измеренная тара и текущая composition signature. SHIPPING_GROSS не поддерживается этим контрактом: финальный вес малого контейнера не является весом целой отгружаемой паллеты.

RRL_WH_WEIGH_REQUEST хранит исходное canonical JSON, автора, native snapshot JSON/SHA256, готовый массово-независимый capture context и окно 120 секунд. RRL_WH_WEIGH_CLAIM хранит sender, стабильный claim_id, exact JSON и неизменяемое окно до 30 секунд, ограниченное концом запроса. Не более пяти попыток на request. Завершение выводится из существующего архива RRL_WH_SCALE_CAPTURE; отдельного UPDATE «измерено» и второго writer нет.

claim_id используется как capture_id существующего пакета склада. request_id — идентичность намерения оператора, claim_id — идентичность единственной физической попытки шлюза. Перед считыванием шлюз сохраняет стабильный claim_id, повторяет claim POST с прежним телом при потере ответа, затем сохраняет точные байты capture в прежнем durable outbox. Lease не продлевается повтором. После истечения lease нельзя заново измерять под прежним capture_id: следует прочитать request/capture и получить новую claim только при подтверждённом отсутствии архива. Новая lease не разрешает поздний первый пакет старой попытки. Уже архивированный неизменный пакет возвращает исходный ACK, даже если lease истекла или оператор позже лишился допуска; текущий выделенный sender и исходный склад сохраняют прежнюю проверку.

## Native права и source fence

Актуальная авторизация остаётся в native. EMPTY_TARE допускается до claim/start: case_pick_execute по фактическому WARE, ASSIGNED_TO null либо текущий оператор; существующий RRL_CASE_RESOURCE_POLICY REPORT требует сессию только по своему действующему контракту и сохраняет manager exception. Указанная optional resource_session_id числовая. PICK требует назначенного текущего оператора, допустимое состояние сборки, строку и текущий ресурсный контекст.

Snapshot фиксирует assignment, CASE content/carrier/type version, resource IDs, фактические поля строки, device policy/calibration/sender/post/mode/basis. Null→actor при claim меняет snapshot: старый запрос STALE, требуется новое намерение. Неподтверждённый старый запрос не оживает при восстановлении старого назначения после нового запроса на том же устройстве: append-only supersession проверяется по более позднему intent. Исторический архивированный запрос не отменяется такой supersession.

FINAL для собственного assembly workflow возможен до finish_session: тот же CASE/device, собственная OPEN неистёкшая session, текущая content version/carrier, закрытый CASE, все steps APPLIED/CANCELLED, нет другой активной сессии. Такое измерение требует текущего case_pick_execute назначенного оператора; отдельный outgoing QC approval не подменяется измерением. Для FINAL вне собственного matching assembly сохраняется RRL_OUTGOING_QC_ACCESS. BLOCKED/чужая сессия/незавершённый step запрещают исключение. Производная assembly_session_id входит в frozen snapshot.

## Транзакции и совместное устройство

Порядок нового request/claim/claimed capture: RRL_ACCESS_REV SHARE → фактический CASE FOR UPDATE → device FOR UPDATE → request FOR UPDATE. Prehook захватывает CASE до прежнего device lock. Fresh-capture guard после прежней archive replay ветки проверяет actor/snapshot/lease/exact context и время наблюдения. После INSERT существующего архива повторно проверяются snapshot и фактическая квитанция. Контекст CASE lock привязан к Oracle transaction ID.

Request/claim отклоняются при активной чужой assembly session; PICK/EMPTY также при собственной. В fresh post-REC ASM body open_session под прежними CASE→device блокировками вызывает обратную проверку активных warehouse requests. Это не device→CASE lock: guard делает только plain source reads. Обычный legacy capture без активного нового request сохраняет прежнее поведение. Архивы и request/claim append-only; trigger разрешает INSERT только текущему private native write context с transaction ID.

## API и UI

Публичные exports inventory: warehouse_weigh_requests_router, warehouse_weigh_requests_service, build_warehouse_weigh_requests(gateway).

- POST /api/inventory/warehouse-scales/requests — только identity, strict mass-free DTO.
- GET /requests/{request_id} — текущий native допуск, REQUESTED/CLAIMED/CAPTURED/EXPIRED/STALE, nullable capture_key/reason; stock_posted=false.
- GET /devices?case_task_id=&purpose= — фактический склад, active/calibration/capacity/resolution/policy/readiness, connectivity=UNKNOWN.
- GET /gateway/requests?device_id= — только выделенный действующий sender, до 20 записей.
- POST /gateway/requests/{request_id}/claim — claim_id/device_id, capture_context без массы, абсолютный claim_expires_at.

Новые routes принимают X-Scale-Protocol-Version: 1.0. Неподдерживаемая версия/масса/actor/SHIPPING_GROSS отклоняются до сервиса. Payload conflict и неизвестный исход не подтверждают отказ исходного request; auth denial также не доказывает отсутствие записи. Потеря ответа требует exact retry/read, без смены request_id.

ASM context получает additive line.status, source_cell и product_codes из прежнего RRL_ARTICULS join (до четырёх непустых уникальных кодов). can_close — read-only preview тех же pending-short/open-line/quantity/physical-lot проверок существующего close owner. Writer close не изменяется и повторяет свои проверки. Количество из кода короба не выводится.

## Проверка и восстановление

16 focused HTTP trust-boundary tests PASS; architecture PASS; полный offline gate PASS (24 architecture/tooling, оба tsc). Это не native acceptance. До apply guard требует exact двух свежих baseline bodies WH/ASM (ASM после REC APPLIED), отсутствие нового namespace и global INVALID=0. После apply обязательны source readback/compile/ledger и caller-owned rollback native сценарии, затем реальные API/SQL evidence. Posting/stock effects не изменяются.

Rollback восстанавливает два исходных bodies и удаляет только пустую новую структуру. Непустая история request/claim останавливает rollback до любого DROP; нельзя удалять immutable intent/claim/capture для удобства отката. История применения и ограниченная приёмка зафиксированы ниже.


Уточнение review: исторический ACK требует исходного RECORDED_BY и для claimed capture исходного CLAIMED_BY; переназначенный sender не получает чужую архивную квитанцию. ACCESS_REV SHARE берётся до device также на replay, право ingest повторно проверяется под fence. Полное окно samples начинается после создания claim; свежесть предыдущей нулевой проверки остаётся прежним правилом packet validator. claim_active=false для STALE/CAPTURED/EXPIRED.


## Фактическое применение и приёмка

Первая apply остановлена до любого DDL: USER_SOURCE нормализовался без CR, multiline ожидаемые литералы OracleApply собирались с CRLF. WH длины14287/14415, firstdiff33 ASCII10/13; ASM51477/51950, diff39 ASCII10/13. Namespace0/ledger0. Исправлена только симметричная нормализация expected CR; exact исходные snapshots не переснимались. Guard отдельно выполнен с LF и CRLF: PASS. Повторное применение14/0,6 source EXACT, errors0/globalINVALID0, ledgerAPPLIED.

Первая actual native request обнаружила ORA40573: PL/SQL JSON getter внутри SELECT пересекал SQL boundary. Попытка request/archive целиком rollback; структура оставалась APPLIED. Versioned follow-up заменил только24 SQL predicates на SQL JSON_VALUE с bounded CLOB/scalar return. Применён5/0, текущий queue body EXACT SHA256 1cb746e64d2258fa4983abbc2077a21bd3b18fba51e094f310b112846bc9aace, errors0/INVALID0. Исходный APPLIED комплект сохранён.

[Native20](../../reports/retailcase/2026-10-15/warehouse-weigh-request/native.json): exact intent/body conflict/original actor; dedicated gateway/device busy; fixed claim/no renewal; orphan/source mismatch/preclaim window rejection; существующий native архив и strict gateway ACK/sourceSHA; exact archive replay; transferred sender denial; revoked request-reader denial; append-only; caller rollback archive/request/claim/metadata + неизменные P/H/version. Два simultaneous claim дали одного победителя и409 второму. Реальные31 секунд expiry проведены без DB transaction: поздний первый пакет отвергнут, exact claim не продлена, новая fenced claim после подтверждённого отсутствия архива дала единственную EMPTY capture. Это software TEST, не физические весы.

[ActualHTTP11](../../reports/retailcase/2026-10-15/warehouse-weigh-request/http.json),12 запросов: operator/dedicated sender без admin-shell permission, protocol/масса/actor/ingest impersonation denial, scoped device UNKNOWN connectivity, exact request/claim/capture replay. После штатного CLAIM/START старое EMPTY остаётся state=CAPTURED +исходный capture_key, но current_context=STALE/admissible=false; источник не выдаётся за текущий. Current reader auth выполняется до проекции. Original native ACK остаётся неизменным. admissible — применимость сохранённого контекста, не QC approval и не товарное подтверждение.

Единая явно разрешённая QA fixture: WAVE567/CASE1136/LINE1139, WARE13583852, source REUSE.RETURN:e6c16d0bbd на исходной QIPcdbf4c0962. Новый face там же, demand1EA, никаких warehouse tasks/TASK_COMPLETE. Только canonical launch/release резервирование: P24/H0/V9→P24/H1/V10. TYPE32/label/тара/ресурс58/session54/shift63 — отдельная явно разрешённая software metadata stage, без goods PICK commit. Native WAVE_PICK_RELEASE проверен caller rollback, затем применён metadata release при точных неизменных P/H/V; coverage1/required1/missing0, replenishments[]. CASE scoped-proof и дальнейшая количественная фаза принадлежат отдельному согласованному increment. История и QA journal не удаляются. [Fixture state](../../reports/retailcase/2026-10-15/warehouse-weigh-request/fixture.json).

SQL/API review: [evidence](../../reports/retailcase/2026-10-15/warehouse-weigh-request/sql.json). Bounded latest700 SQL logs: один относящийся31ms expected403; V$SQL request avg49ms/claim54ms/status19ms/catalog22ms/pending15ms. HTTP первый history read301ms, остальные успешные59..94ms;12 FINISHED matched по локальному JSONL. Дублирующий индекс не нужен: DEVICE/EXPIRES request index + существующий UNIQUE DEVICE/CAPTURE. До крупного pilot backlog inventory/platform: bounded EXISTS supersession вместо COUNT длинной истории устройства, использовать эквивалентное expires ordering (TTL120) либо проверить plan/индекс DEVICE/CREATED_AT. Нагрузочный объём истории здесь не доказан.

Остаётся: положительный FINAL queue workflow собственной ASM и weighted PICK context; UI request workflow; автоматический gateway pending→claim→observe loop поверх существующего exact durable packet outbox. Нынешний warehouse worker отправляет готовый packet, но ещё не получает новое намерение через эту очередь. Текущие CASE permission/resource helpers сохраняют legacy правила; отдельный scoped-only CASE writer сам по себе не расширяет все вспомогательные measurement helpers. Физический OPC/весовой pilot отдельно. Shared CASE1136 передан root/CASE-author без дальнейших изменений этим исполнителем.

## Очередь: ограниченное окно последних намерений

Forward `2026-10-15_warehouse_scale_request_pending_window` применён root:5 statements/0 errors. Независимый readback: queue body EXACT SHA256 `3642aabe97e8a6ba6ff03bd31b897557a6e0015c91356365444bb485abd4f1c7`, USER_ERRORS0/global INVALID0/ledger APPLIED. Единственное изменение: `ORDER BY CREATED_AT DESC, REQUEST_ID DESC FETCH FIRST20` перед существующей native фильтрацией. Device serialization запрещает создание нового намерения при текущем REQUESTED/CLAIMED; более новое immutable намерение навсегда делает старые незавершённые намерения STALE. Поэтому текущее намерение, если существует, находится первым; стабильный tie не ослабляет fail-closed правило равных timestamps.

[BEFORE](../../reports/retailcase/2026-10-15/warehouse-weigh-request/pending-before.json) и [AFTER](../../reports/retailcase/2026-10-15/warehouse-weigh-request/pending-after.json):21 настоящих native request на новом rollback-only TEST device. Между ними менялась только версия нового device через действующий configuration owner;20 предыдущих намерений стали STALE. До исправления newest REQUESTED отсутствовал в pending; после присутствует ровно он. Capture rows0, исходная полная CASE1136 и source P/H/V неизменны, новые device/requests после caller rollback отсутствуют. Ранний вариант с дополнительной metadata resource plan был отвергнут strict plan guard до DML; guard сохранён, fixture сужена до read/lock существующей CASE и нового device.

SQL decision: ограниченное окно20 сохранено, исправлен порядок отбора; дополнительный индекс не вводился. Проверка длинной истории supersession остаётся указанной выше задачей inventory/platform до масштабного pilot. Новая приёмка доказывает starvation regression, а не нагрузочную пропускную способность.

## PREPARED: физический контекст CASE и платформы

Независимый audit обнаружил два admission gap прежнего device_free: активная CASE на другом device не блокировала новое EMPTY/PICK; истёкшая по lease, но всё ещё OPEN/BLOCKED ASM переставала блокировать WH request на той же платформе. Истечение lease не доказывает отсутствие груза. Root рассмотрел отдельный forward `2026-10-15_warehouse_scale_case_device_guard`: sameCASE/otherDEVICE OPEN/BLOCKED запрещает новое намерение; sameDEVICE OPEN/BLOCKED также блокирует без фильтра срока. Прежнее узкое own FINAL исключение сохраняет unexpired/currentowner/content/closedCASE/allsteps guards. До проверки live apply это PREPARED, не закрытая приёмка. Основная CASE1136/device/source этим исполнителем не изменялись.

Следом PREPARING zero progress: новое намерение zero_progress_required=true требует append-only gateway-reported OPC zero перед первым capture; legacy absent flag не меняет исходные bytes. Это UX сигнал готовности загрузить платформу в пределах текущей native lease/context, не товарное либо QC подтверждение. Profile SHA/units/mode — аттестация зарегистрированного gateway, не вымышленный hardware commissioning Oracle catalog. Owner integrations/modelcommissioning ведёт отдельный backlog native зарегистрированных OPC profiles.

Cross-device/expired-device forward затем применён root5/0; независимый queue body EXACT SHA256 `2dea0101e5f0e4cca193063fc9656930fb4138f7f981c7d8061c4897b8eb5328`, errors0/global INVALID0/ledger APPLIED. Runtime отрицательная проверка вынесена из параллельной основной физической фазы; исходная CASE1136 не менялась этим исполнителем. ZERO kit ещё PREPARED и должен быть перебазирован после отдельного ASM_FINAL v3 forward; PREPARED body с прежней shipping signature не может заменять более новый live source.
