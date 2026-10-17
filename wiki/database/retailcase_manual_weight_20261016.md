# Ручной ввод веса с сохранением интеграции весов

Поручение владельца16.10: пока ввод пользователем, работающий API электронных
весов сохранить. Новые SHIPPING_GROSS hardware request/claim/capture/use не
являются условием выпуска текущего UI. Существующие интегрированные API остаются.

В погрузке уже действует measurements.origin=MANUAL_CONFIRMED с версией грузового
места. Используется прежняя native операция; масса не создаёт разрешение QC.
Для магазина добавляется manual_weight_kg в прежнее подтверждение приёмки.
Одновременно ручной вес и scale_capture_key запрещены. Новое поле отсутствует
в canonical body старых запросов, если пользователь его не передавал.

Владелец delivery, правила RRL_STOCK_STORE_WEIGHT_CORE, транзакция прежнего
StockPosting STORE_RECEIPT. Источник ручного веса MANUAL_CONFIRMED, оператор и
время фиксации из штатной операции/RECORDED_AT; аппаратный архив не имитируется.
Положительный GROSS KG сверяется с прежним frozen shipping gross и допуском.
Фотографии/акт расхождения и политика магазина сохраняются. Наличие фотографий
не превращает ввод пользователя в аппаратное измерение.

Таблица RRL_STORE_RECEIPT_WEIGHT: CAPTURE_KEY становится nullable, добавляется
MEASUREMENT_ORIGIN с default SCALE_CAPTURE. CHECK требует аппаратный ключ для
SCALE_CAPTURE и его отсутствие для MANUAL_CONFIRMED. Старые записи сохраняют
исходные ключи и FK. Rollback запрещён при сохранённой ручной истории.

Статус dev APPLIED; полная новая TEST приёмка/откат/replay проверены после persist fix.
Fresh4 native sources/INVALID0 и metadata до изменения:
[checkpoint](../../reports/retailcase/2026-10-16/manual-weight/before/manifest.json).
Комплект [SQL](../../db/migrations/2026-10-16_manual_store_weight/README.md),
MIGRATION_ID2026-10-16-manual-store-weight, frozen SHA
2cc38a999c87af9cd08caca7f587fa0cd66170796a3c046c45164a77842be67a.
[Apply](../../reports/retailcase/2026-10-16/manual-weight/root-apply.json) и
[readback](../../reports/retailcase/2026-10-16/manual-weight/root-readback.json):
6 source hashes совпали, USER_ERRORS0/INVALID0, ledger APPLIED. Schema verify
подтвердил12 колонок, nullable capture и ENABLED/VALIDATED source constraint.
Триггер прежнего Stock owner перекомпилирован, его исходник не изменён.

[Проверка](../../reports/retailcase/2026-10-16/manual-weight/functional.json):
7 checks — точный расчётный procedure из установленного body выполнен anonymous
в READ ONLY на историческом QA load/трёх исходных фото; ручной GROSS/допуск/источник,
двойной источник/ноль/акт при расхождении, старое canonical body и новый API field.
Это проверка расчёта/контракта, не новая сохранённая приёмка. Автор не выдаёт её
за независимую проверку или hardware. Ручной ASM этим изменением не реализован.

[Live8HTTP/8audit pairs](../../reports/retailcase/2026-10-16/manual-weight/http-read.json):
список/следующий cursor200, обе статические статьи200, новый manual field в OpenAPI,
прежние4 capture routes сохранены, invalid/dual source422, уже принятая поставка409.
Новых receipts/manual evidence/quantity effects0. Quality gate1102/0циклов/debt72,
tooling24/обаTS PASS. На этом раннем checkpoint новая STORE_RECEIPT ещё была открыта;
результат последующего полного сценария и исправления приведён ниже.

SQL:0 slow records. Максимум1093мс относится к OpenAPI schema, не бизнес-операции;
list343/76мс, static help24/29мс, ошибки receipt31/38/92мс. V$SQL cumulative native
helper average18мс, другие текущие list cursors15–142мс; не endpoint p95 и не
доказательство причины первого вызова. Сохраняются photo3..12, boxes200 и текущие
PK lookup. Владелец fulfillment проверяет binary-sort/scope plan на пилотном
объёме: limit50 не ограничивает все предварительно отфильтрованные кандидаты.
Индексы/кеш без повторяемого bottleneck не вводятся.

## UI и простые ссылки

Обычные страницы уже доступны на API origin: `/help/manual-weight.html` и
`/help/consolidation-plan.html`, секции enter/confirm/store/integrated/retry и
save/refresh/cancel/conflict. StaticFiles обслуживает только docs/help/public,
не wiki/reports/конфигурацию. Никаких ARTICLE_SAVE/PUBLISH в этом инкременте.
Существующий Oracle editor/help остаётся совместимым.

[C0116 UI](../../coordination/retailcase-claude/API_READY_SINGLE_CLAUDE.md) передан
в CODEX_TO_CLAUDE по новому поручению владельца. ACK K-0064/C0116 получен,
Claude сообщил IN_PROGRESS и занятые frontend файлы.
Codex не меняет frontend файлы этого пакета до RELEASE. Hardware SHIPPING_GROSS
сохранён в backlog, не блокирует текущую реализацию ручного ввода.

## Новая поставка: проверка сохранения

Поручение продолжено после запуска Claude владельцем. Свежий TEST склад11323734,
3EA через обычный full-pallet PICK → TOP/BOX → ручная погрузка → departure,
3 синтетических фото и штатный unloading start. Все команды/метаданные сохранены
до вызова в committed-case/journal.json; исходный fixture setup переиспользован
без прежних дополнительных матриц/переписывания товарных состояний.

Caller-rollback новой приёмки обнаружил runtime ORA-40573 в persist line73:
PL/SQL JSON method использован внутри SQL VALUES для measurement origin.
Транзакция откатилась; успешный native calculation не доказывал этот INSERT.
Исправление package-only: извлечь origin в scalar до SQL. DTO/права/электронный
capture API не меняются. Fresh3 source checkpoint/INVALID0:
[persist-fix](../../reports/retailcase/2026-10-16/manual-weight/persist-fix/before/manifest.json).
Kit2026-10-16-manual-weight-persist, SHA4b36fee8ccbd65a9628f3e91ffa8fb18f15b6bcc51a752b231a91232e4fd57ef,
APPLIED с paired rollback/history guard. [Apply/readback](../../reports/retailcase/2026-10-16/manual-weight/persist-fix/root-readback.json):
3 source hashes совпали, USER_ERRORS0/INVALID0, ledger APPLIED. Source/DTO
электронных API не менялись. Первые ошибочные attempts сохранены; отсутствие
receipt/weight/stock operation после rollback подтверждено persist-failure.json.

[Полный сценарий](../../reports/retailcase/2026-10-16/manual-weight/committed-case/receipt-v3.json):
внутри caller TX существовала ручная weight row; rollback убрал её и business
receipt/operation. Затем та же сохранённая команда принята настоящим HTTP:
ACCEPTED3EA, origin MANUAL_CONFIRMED, capture_key/device_id=NULL, recorded_by=admin.
Точный replay вернул тот же ACK; изменение веса10→10.1 с прежним ID409.
Weight row одна, warehouse P/H0/0, прежние склады6667491/20220394 не изменились.
Custody освобождена самим штатным receipt owner. Новая волна576 завершена native
finish-execution; не SQL-перезаписью состояния. Test metadata/history сохраняются.
Это авторская software acceptance; физических весов/доставки/независимого review нет.

[SQL review](../../reports/retailcase/2026-10-16/manual-weight/committed-case/sql-review.json):
11HTTP/11local pairs/0slow. Receipt203мс, replay77мс, конфликт67мс.
Самый длинный запрос HTTP — погрузка1791мс; конкретный SQL-виновник не установлен.
Shared EXECUTE_PREPARED average56/144мс, INSERT weight3.9мс, photo lookup0.46мс;
это cumulative cursors, не endpoint p95. Решение: scalar bind, прежние PK,
photo3..12/boxes200; delivery/transport owner разбирает prepare/execute/audit
фазы при повторении loading>1000мс на пилотном объёме. Без индекса/кеша по одному TEST.


## C0116 integrated result

Claude RELEASE K-0065/K-0066: [report](../../coordination/retailcase-claude/RESULT_C0116.md). Terminal manual/electronic selector, immutable pending body and origin-aware act; existing loading payload preserved; expected-plan editor/list/navigation delivered. Root fixed terminal dev `/help` proxy and removed fixed identity overlay over mobile data. Both frontend production builds PASS (existing chunk-size and leaflet-draw warnings remain).

Root live UI [continuation](../../reports/retailcase/2026-10-16/claude/C0116/root-integration-v3/result.json): own future plan CP.20220394.20261016.76d88fa1 saved through UI then cancelled, stock_changed=false; real store production `/store/` displays committed MW16.RECEIPT.ab42b67239 act with manual10kg, null device/capture. Mobile390 has no outer horizontal overflow and identity is in normal header. No repeated receipt or stock mutation. Harness strict-selector timeouts preserved before bounded continuation; no duplicate plan created. Screenshots reside beside result.

[Root SQL](../../reports/retailcase/2026-10-16/claude/C0116/root-sql-review-v2.json): live UI PUT/cancel and populated CASE denial,3HTTP/3local pairs/0slow/max266ms. Retain bounded200 membership updates and native current source/target rights; no new cache/index. Full gate1112files/0cycles/debt72/24tooling/bothTS PASS; encoding PASS. Hardware/remaining sprint gates are not closed by this integration.
