# CASE1136: read-only preflight товарной компенсации

15.10.2026. Только bounded SELECT в RABAEV/orcl и чтение файлов. prepare/execute/domain helpers/commit/metadata DML не выполнялись. [Сохранённые live данные и USER_SOURCE](case1136-return-preflight.json). Это стратегия проверки перед решением root о количестве, не положительная товарная приёмка.

## Наблюдаемая исходная точка

CASE1136 / line1139 / wave567 / plan2199 / picktask2137, order2146, warehouse13583852. CASE IN_PROGRESS, version2, picked0, идентификатор090000000000008014. SKU REUSE.QA:cdbf4c0962 TYPE_W0, base EA1:1(policy1), planned1. Единственный HARD1863 принадлежит PICK_WAVE567/task2137:1EA.

REUSE.RETURN:e6c16d0bbd @QIPcdbf4c0962: P24/H1/version10; второй нулевой ряд@QRREe6c16d0bbd P0/H0/version2. CASE composition и ASM session отсутствовали. Источник уже имеет STOCK_ORIGIN_UID=300000034518661218 и CREATED_BY_STOCK_OP=REUSE.RECEIVE:e6c16d0bbd. Нельзя ожидать, что новый child origin станет REUSE UID.

## Проверенные guards и ещё нужный шаг

- Native CASE_PICK компилирует собственный HARD, проверяет stock snapshot/actor/assignment/scan/route/resource/assembly evidence и создаёт CASELOT child. Он не присваивает LEGACY_SBORKA_PALLET_ID.
- CPT_13583852 первоначально отсутствовал — обнаружен blocker. Root отдельно применил commissioning. Повторный read подтвердил существующий CPT, warehouse13583852, IS_SYSTEM1. BLOCKED_FOR_REMAINS/POPOLNENIE1 допустимы только для специального CASE_TRANSIT/CASE_EXIT пути: ordinary entry на него не разрешаем. Источник QIP открыт и имеет published CELL policy1.
- Штатный close_case_carrier проверяет все строки PICKED/SHORT_PICKED/CANCELLED, qty≤plan и точное совпадение physical lot totals; переводит WAIT_CONTROL без изменения товара. Он не создаёт legacy СТ и не устанавливает legacyID.
- Существующий bind_existing_case_shipment / case_shipment_binding.py — подходящий owner: после close связывает уже подготовленную СТ и ровно один fulfillment того же order, проверяет идентификаторы, WARE/version, CONDITION<2 и точный состав в BASE, затем записывает связь+fulfillmentPICKED+SHIPMENT_BOUND одной metadata TX. Новый binder и прямой UPDATE legacyID не нужны.
- На snapshot order2146 не имел fulfillment. Поэтому полный close→FINAL требует сначала отдельно разрешённый preparedST+fulfillment ровно1EA. Подготовка этого metadata fixture ещё не выполнена этим исполнителем. Root запросил plan владельца до создания.
- RETURN требует case_pick_manage +root current CASE scope, актуальные expected_content_version/scan_container; SHIPPED/CANCELLED/FAILED запрещены. Если legacyID есть, CONDITION≥2 запрещает возврат: до компенсации не выполнять shipment/QC posting, которое достигает этого состояния. FINAL/ASM finish сами по себе не являются разрешением отгрузки.
- Все положительные CASE lots должны вернуться в исходные клетки своих строк: destinations ровно по фактическим child UID. Чужой HARD запрещает возврат; собственный HARD снимается через единственное native ядро. Не использовать allow_empty после реального PICK1.

## Capacity: что доказано

QIP имеет правильный WARE, IS_SYSTEM0 и все три block flags0. LIMIT_WEIGHT/LIMIT_HEIGHT0; текущие CELL_WEIGHT/HEIGHT null. Pick face606 ACTIVE, MAX_VOLUME1, MAX_WEIGHTnull; source slot claims и receipt cell rule отсутствовали. В просмотренных live CASE_RETURN/TRANSFER/LOCATION/BALANCE путях нет обращения к LIMIT_WEIGHT/CAPACITY/MAX_VOLUME: ordinary target guard проверяет WARE и block flags, а не полный геометрический предел.

Следовательно, физическая вместимость не объявляется доказанной этим preflight. Возврат1EA восстанавливает прежний total24 на той же ячейке, но оставляет два lot UID; это не измеренное подтверждение двух HU/слотов. Root должен ограничить TEST quantity1, сохранить исходный physical footprint и отдельно принять эту границу либо отложить до capacity-owner проверки. Изменять capacity/policy ради теста не предлагается.

## Proof strategy без подмены истории

1. После разрешения root собрать новый EMPTY_TARE0.5 и открыть ASM session, выполнить реальный протокольный BEFORE0.5→AFTER1.5 для1EA. До quantity approval это не запускать. Native должен дать ровно одну CASE_PICK_CONFIRM/STEP_USE/clock, source23 и CASE child1, total24; exact replay не меняет stock/version/journal повторно.
2. Close штатным owner; привязать подготовленную СТ штатным bind. Снять новый FINAL_GROSS1.5 со ссылкой на EMPTY_TARE и текущий frozen composition, завершить ASM. Это отдельные metadata/evidence результаты, не shipment. Между этапами сравнивать source/child P/H с последним подтверждённым состоянием.
3. Перед RETURN перечитать carrier lots, latest CASE version/scan, legacy condition и HARD set. Команда CASE_CARRIER_RETURN использует destinations={actual_child_uid:'QIPcdbf4c0962'} и новый один operation_id; exact retry этого тела неизменен. Native SOURCE/CASE_EXIT возвращает тот же child UID, не делает merge UID.
4. После RETURN требовать parent23/H0 +child1/H0 на исходной ячейке, положительный CASE/transit stock0, totalEA24; carrier membership удалён, CASE CANCELLED/legacyIDnull, текущий fulfillment PLANNED/FACT0, shipment-bound/pick/clock/raw история сохранена. Связь child доказывается CASE journal и CREATED_BY_STOCK_OP исходного PICK; STOCK_ORIGIN_UID остаётся300000034518661218. Не требовать parentUID P24 и не выполнять inventory count/ручной merge ради такого сравнения.
5. Затем штатные WAVE_CANCEL →PICK_PLAN_CANCEL. RETURN уже ставит PICK_TASK/PICK_WAVE_TASK CANCELLED; native wave release допускает NEW/ASSIGNED/CANCELLED и отклоняет прочие started states, plan cancel отклоняет IN_PROGRESS/DONE. До них проверить отсутствие активных/выполненных warehouse tasks. Собственные SOFT/HARD released, total24/H0 остаётся. Закрытие/возврат использованной тары выполняет отдельный tare owner по сохранённой booking identity, без удаления истории.
6. При каждом неизвестном stock исходе читать исходный operation и повторять тот же body; не начинать новую компенсацию. В acceptance сохранить source+child snapshots, immutable operations/movement/outbox/clock, CASE/fulfillment/tare states, native INVALID baseline и slow SQL.

Read-only discovery один раз обратился к несуществующей POLICY_ID (ORA-00904); после USER_TAB_COLUMNS запрос исправлен. Никаких изменений состояния этим отказом нет. Запросы ограничены конкретными CASE/wave/UID/USER_SOURCE names и строковыми окнами. Этот preflight не измеряет нагрузку; actual quantity-case должен отдельно анализировать SQL/SKV telemetry.

## Последующий разрешённый metadata stage

После данного read-only preflight root отдельно разрешил minimalTEST ST fixture. scripts/warehouse_prepared_st1136.py выполнил callerrollback с проверкой отсутствия header/row/fulfillment и неизменного source/CASE, затем один CONFIG metadata commit того же TEST.WHREQ15.PREPARED. Итог ST641520 / row16727999 / fulfillment190,1EA PLANNED/FACT0, CASE не привязан. [Отдельный отчёт](prepared-st1136.json) содержит trial IDs/sequence gaps, source SHA и первоначальную ошибку reservedbind в smoke-helper с полным rollback. Функции legacy не имеют COMMIT/stock вызовов; логистические массы/габариты оставлены NULL, DOCID NULL из-за отдельной ширины15.

Это устраняет отсутствие подготовленного metadata объекта; положительная close→bind→FINAL→finish→RETURN проверка ещё не выполнена этим исполнителем и quantity commit не разрешается автоматически. RETURN сохраняет ST/rows, переводит текущий fulfillment обратно PLANNED0 и снимает CASE link; удалять журналы/проводки/SHIPMENT_BOUND нельзя.

## Дополнительный caller-owned rollback proof

Root отдельно разрешил одну ordinary CASE_PICK_CONFIRM1EA внутри caller TX без commit. [Результат](compensation-caller-rollback.json): parent23/H0 +actualCASELOT1/H1/CPT, правильные rootorigin/createdoperation; pure validate_close_content и assert_matching_composition с реальным preparedST1EA PASS. Source-reviewed RETURN predicates (all-lots/originalcell/ownHARD/currentversion/notshipped) PASS. Изменять CASE status/legacy binding не потребовалось и не выполнялось.

RETURN.compile_command остался NOT_RUN_OWNER_BOUNDARY: фактический spec ACCESSIBLE BY(RRL_STOCK_POSTING_API). Второй prepare в грязной TX, новый wrapper и снятие ownership запрещены; такой компилятор не объявлен выполненным. После rollback source/CASE/line/events/op/child/outbox/clock совпали с исходным состоянием, новых объектов нет. Actual RETURN prepare/execute остаётся отдельной чистой транзакцией после решения владельца о bounded quantity commit.

Metadata ST stage longest logged block151ms. Решение: сохранить точечные CASE/UID/operation/identifier окна и короткую CONFIG TX; нового индекса/широкого сканирования не требуется для этого fixture. Это не оценка промышленной нагрузки. Актуальная quantity/compensation acceptance должна отдельно сравнить slow SQL/SKV и root journals.

## Живой шлюз EMPTY_TARE

После отдельного RELEASE выполнен новый actual encrypted localhost OPC→production warehouse request/claim→capture/raw EMPTY_TARE CASE1136. Native ARCHIVED +raw1.0 MATCHED, GROSS0.5, sourceP24/H1/version10 без изменений. [Отчёт](opc-empty-native-http.json). Это разрешённый metadata/evidence этап, не quantity approval. Тот же TEST OPC server удерживается1800секунд для дальнейшего отдельного решения root. Никакой ASM BEFORE/AFTER/stock posting этим driver не послан.
