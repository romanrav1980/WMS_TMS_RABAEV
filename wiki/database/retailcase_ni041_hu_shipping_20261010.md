# NI04.1 — атомарная отгрузка верхнего CASE-HU
10.10.2026.067 APPLIED в RABAEV/orcl. [[retailcase_ni051_case_control_20261010]].

HU_SHIP использует существующее SHIPPING_CORE.execute_resolved: каждый вложенный существующий СТ сохраняет собственные binding/CASE/customer fulfillment/резерв/марки и юридические ограничения. Количественная проводка не продублирована. Root сохраняет один неизменяемый план, operation/result и обязательный outbox; исполнители не подменяют RESOLVED_PLAN_JSON.

Первая версия принимает верхний контейнер с закрытыми CASE, включая промежуточные контейнеры. Каждый CASE обязан быть привязан к существующему СТ; посторонние обычные stock листья не принимаются. Все допуски проверяются до проводки и в существующем executor, состав/версии повторно проверяются под полным заранее объявленным closure. До200 nodes/allocations, depth16. Скан идентификатора и текущей ячейки обязателен. Отдельный SHIP_PALLET вложенного CASE отклоняется, QC сохраняется без автоматического отдельного списания.

Реальные ST блокируются по ID перед CASE по ID. Номера количественных leg глобальны внутри одной операции, offset для каждого ST; история двух документов не сталкивается. Все P/H/unit/journal/CASE/fulfillment/links/освобождение места находятся в одной Oracle транзакции. Commit только у root caller; исправление запасов не выполняется QC.

HU_SHIPPED_OPERATION у контейнера хранит operation; текущая ячейка очищается и claim освобождается, links деактивируются с сохранением истории. Check constraint различает активный и отгруженный контейнер; departure/container/link guards разрешают это только root HU_SHIP с ресурсами. API показывает неизменяемый composition_at_departure из сохранённого результата, помеченный historical_composition/SHIPPED, а не текущий запас. Откат кода сохраняет additive schema и историю; отгруженные goods автоматически не восстанавливаются.

API POST /api/warehouse-hus/ship: server actor, право stock_posting_shipping, operation_id/expected_version/scan_container/scan_cell. Existing ARM сохраняет immutable pending/retry и блокирует действия с историческим местом. Легаси внутреннее ядро сохраняет CLOSE_OTHOD_NAKLAD как альтернативное право; новый HTTP endpoint требует явное stock_posting_shipping.

Own scripts/ni041_hu_shipping_case.py passed: реальные wave/CASE12+8/две existing STs, независимый BOTH, nested standalone и неверный скан denied с20/H20, одна HU_SHIP→P0/H0/обе CASE SHIPPED, две реальные строки ST сохранены, active links0, cell освобождён, exact replay. Собственные fixtures очищены root; журнал/документы сохранены. Исторический API-service preview20/2 leaves и empty-line canonical contract прошли. Ошибка после первой выполненной внутренней части/конкуренция/marked upper-HU/browser acceptance ещё требуют независимого сценария.

Slow SQL: bounded ST JSON_TABLE selection4xhartvzr32fz ~2.49ms/3; existing planned ST lookupdcg3q7zp9xv8q ~1.22ms/23. Решение — bounded200/key lookups; без нового индекса. Эти timings не доказательство промышленной нагрузки.

Открыто: FULLPAL/обычные leaves с actual ST binding, route/dock consistency верхнего места, независимые partial-failure/concurrency/marked scenarios, multi-HU/cell и slotted unpack; NI04.1/NI05.1 целиком не закрыты.
