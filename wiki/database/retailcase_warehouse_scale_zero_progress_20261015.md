# Складские весы: подтверждение нуля перед загрузкой

Статус: **APPLIED**, root15 statements/0 errors; независимые5 sources/constraints/indexes EXACT, USER_ERRORS0/global INVALID0. [[retailcase_warehouse_scale_requests_20261015]], [[../components/retailcase_warehouse_opc_requests_20261015]]. Комплект `db/migrations/2026-10-15_warehouse_scale_zero_progress` перебазирован после APPLIED ASM_FINAL v3 forward: before queue SHA256 1d64ec22fa49a7fb7c39e10ffec9cb5b9c0d24ae54e1e329b43a0fb9f3a7d368, source guard LF/CRLF PASS, INVALID0; native ZERO применён с exact body SHA256 a384012e3557c3a87047b787d1812c939fe17fa80d1b386eaf49fbe2e2e66d6d.

## Задача

CLAIMED означает только захват намерения gateway. Оно не доказывает ноль платформы. UI прежде не мог достоверно сказать, когда поставить пустую тару либо полный CASE после проверки нуля. Новый запрос UI явно передаёт zero_progress_required=true; отсутствие флага сохраняет legacy payload и поведение. Capture DTO и canonical bytes не получают этого поля.

## Новый контракт

POST /api/inventory/warehouse-scales/gateway/requests/{request_id}/zero-confirmed, X-Scale-Protocol-Version=1.0; только warehouse_scale_ingest и native current dedicated sender. Тело: claim_id, device_id, zero_observed_at, zero_source_sha256, zero_evidence_json, profile_sha256, unit_namespace_uri, kg_unit_id, no_tare_mode. Масса загруженного груза и actor в тело не входят.

zero_evidence_json — исходный canonical JSON actual OPC zero.evidence: observed_at, values с семью DataValues current_weight/stable/center_zero/overload/underload/tare_mode/engineering_units. Каждый DataValue хранит value/status_code/variant_type/source_timestamp/server_timestamp. ZERO_OBSERVED_AT относится к current_weight.ServerTimestamp. Native сверяет SHA исходной строки, Good quality, Gross/Net/Tare0, stable/center_zero=true, отсутствие range flags, заявленный GROSS без device tare, reported profile units/mode и действующее окно claim. Статичные source timestamps могут быть старше claim; их не переписывают. Server timestamps и local observed_at должны быть свежими и принадлежать текущему claim.

Profile SHA и значения EUInformation/no_tare_mode — GATEWAY_REPORTED от зарегистрированного dedicated sender, как действующий raw trust model. Это не native аппаратная аттестация и не зарегистрированный commissioning catalog. Backlog owner integrations/modelcommissioning: отдельный реестр закреплённых моделей/профилей оборудования.

RRL_WH_WEIGH_ZERO — append-only, один факт на claim_id, исходное тело/evidence/SHA/profile/time/исходный sender и immutable receipt. Revision→CASE→device→request lock order сохраняется. Первое подтверждение требует current original operator/context/device/sender и действующую lease. Exact replay не переписывает факт; другой sender либо другое тело не получает исходную квитанцию.

POST response разделён: receipt — неизменяемое подтверждение исходного нуля; current — актуальная native проекция запроса. Historical receipt после expiry/stale не даёт инструкцию загрузить платформу.

## UI и producer

GET request добавляет measurement_stage WAITING_ZERO / ZERO_CONFIRMED / CAPTURED / INACTIVE, load_allowed, zero_confirmed_at, zero_source_sha256, claim_expires_at, server_now. load_allowed=true только для current CLAIMED/current context/unexpired claim с matching zero. UI гасит инструкцию также по истечении времени до следующего GET. CAPTURED сохраняет исторический факт и прежний admissible; он не включает новую инструкцию загрузки.

Producer: actual OPC zero → durable original zero event bytes → POST → strict immutable receipt плюс current envelope → ожидание фактического gross>0 → прежнее sample window → прежние canonical capture/raw bytes. Потеря ответа и restart используют те же zero bytes, а не новое измерение под старой claim. Идентификаторы/SHA/current zero/time/lease/UTC проверяются. Native first capture для flagged request требует сохранённый zero и точное zero_check_at; sample window не предшествует ему. Legacy без флага сохраняет прежнюю проверку; если zero event всё же существует, его связь тоже проверяется.

Сигнал нуля не подтверждает товар, качество, состав или final mass. Наличие Good OPC данных само по себе не доказывает аппаратный пилот.

## Подготовленная приёмка

Focused API/producer/durable tests:47 PASS. Encrypted localhost OPC→HTTP mock:6 сценариев (три legacy и три required EMPTY/FINAL/PICK), последний повтор после строгой проверки currentzero/UTC:6 PASS за49.82s. Это не actual Oracle и не физическое оборудование. Общий quality gate после этого изменения PASS:1033files/cycles0/debt72,24 tooling tests, оба TypeScript проекта.

План native acceptance (выполненный результат ниже): только отдельные новые empty QA wave/order/TYPE32 CASE/TEST label/device, admin manager exception явно не является qualified-operator proof. Не используются основной CASE1136/станция/товарные source и active ASM. Metadata создаётся штатными последовательными owners; canonical empty WAVE_CANCEL предварительно проверяется caller rollback. Никаких планов, строк отбора, резервов, PICK/TASK_COMPLETE либо weight capture commits. Zero intents/claims/events тестируются caller rollback, затем empty fixture отменяется native owner; label/operation/history остаются. Rollback DDL запрещён при наличии zero history либо flagged intent: требуется forward recovery.


## Фактическая native/HTTP приёмка и cleanup

[Native](../../reports/retailcase/2026-10-15/warehouse-weigh-request/zero-native.json):15 checks PASS, исходное zero.evidence получено настоящим encrypted localhost OPC read отдельного QA сервера/профиля/device. HTTP создаёт только durable mass-free request+claim; ZERO факт/receipt проверены native в caller-owned transaction и полностью rollback. Capture rows0, goods writes0. Source SHA исходной UTF8 строки и всего body подтверждены strict gateway ACK validator.

Проверены обязательный zero перед flagged capture, отказ ненулевого raw Gross/Net, flags/tare/unit/quality/hash/time, immutable exact receipt/payload conflict, append-only. Independent review добавил обязательное capture.zero_check_kg numeric0 при сохранённом zero; same timestamp с .001 отвергнут, другой timestamp с0 тоже отвергнут. Legacy без zero row сохраняет прежний validator. Истёкший первый ZERO POST actual HTTP409, load_allowed=false; ожидание expiry прошло без DB transaction. Фактический HTTP audit этого flow:5 вызовов, включая этот отказ.

[Старый frozen запрос](../../reports/retailcase/2026-10-15/warehouse-weigh-request/zero-legacy-frozen-replay.json): отдельный actual HTTP exact replay исходного MAIN EMPTY после нового DTO/server вернул прежний CAPTURED/key, current_context=STALE, required=false/load_allowed=false. Canonical bytes DTO точны исходному body, основной CASE1136 полностью неизменен, business writes0. Вместе с ZERO flow это6 реальных HTTP вызовов; не следует складывать их с прежними11 сценариями WH requests как новые distinct domain cases.

[Fixture](../../reports/retailcase/2026-10-15/warehouse-weigh-request/zero-fixture.json): только новые WAVE568/CASE1137/order2147/deviceWHZERO15.AK06.SCALE, пустые0lines/qty/reservations; TYPE32/TESTlabel. Prefix восстановлен точно. Native empty WAVE_CANCEL сначала caller rollback, затем canonical commit released_count0; synthetic CASE/header отменены guarded metadata owner, device неактивен. Label/request/claim/operation history сохранена. Это явно не production CASE cancellation и не qualified-operator proof. Основной CASE1136/его станция/OPCcontrol/товарные child units не изменялись.

На metadata stage исходный parent UID был P23/H0; затем независимый согласованный CRES owner зарезервировал1 (P23/H1), передал окно обратно. ZERO native и cleanup имеют точные собственные before/after P/H/version при этом текущем CRES baseline; возвратный child1 не менялся. Изменение H между стадиями не приписывается ZERO и не скрывается.

[SQL/API audit](../../reports/retailcase/2026-10-15/warehouse-weigh-request/zero-sql.json): confirm_zero11 executions avg27.558ms; bounded latest700 slow logs — один expected expiry409/21ms. HTTP241/142/49/61/81ms, все5 FINISHED local JSONL matched. Решение: PK CLAIM_ID lookup и7 фиксированных DataValues ограничены; новый индекс не нужен. Длинная device history supersession остаётся backlog inventory/platform до pilot; её нагрузочная ёмкость здесь не доказана.

После новых параллельных UI файлов последний общий gate: architecture1040/cycles0/debt72,24 tooling иadmin TypeScript PASS; terminal TypeScript остановился на AssemblyStage context prop mismatch, root/UI owner уведомлены. Предыдущий полный gate PASS был до этого UI изменения. Focused47 иencrypted6 PASS относятся к этому backend/gateway increment. Физический pilot и production UI zero instruction отдельно.

Rollback SQL после этой приёмки намеренно заблокирован retained flagged request history, даже при ZERO rows0: требуется forward recovery; историю не удаляют ради отката.
