# NI01.1: внутренний идентификатор паллеты при SAP-приёмке

Checkpoint683–686, 12.10.2026. Основание — AGENTS.md: поля идентификатора паллеты принимают стандартные SSCC и внутренние/legacy WMS значения.

До изменения SAP receipt DTO и Python planner требовали только18 цифр с GS1 check digit. RRL_SAP_RECEIPT_API затем записывал физический UID и SSCC одинаково, хотя PALLETS.SSCC имеет32 байта. Live683: PALLETS.UID_PALLET50 CHAR, SAP receipt/task/unit/claim UID200 BYTE; для общего маршрута принят предел50 символов и150 UTF-8 байт с учётом существующих native scanner variables. Непечатные символы/пробелы отклоняются.

Новое имя входа pallet_identifier и прежнее sscc принимаются через alias; конфликт двух значений отклоняется. Сканерные GS1 префиксы нормализуются по прежнему правилу. Числовой18-значный код всё ещё требует корректного check digit. Canonical metadata использует прежний ключ sscc для стабильного operation replay; generic UID и регуляторный SSCC различаются по значению и отдельным полям.

Root quantity executor, планирование, резервы, исходные SAP order/line, unit birth и outbox остаются прежними. Wrapper сохраняет PALLETS.SSCC только для доказанного GS1 SSCC; у внутреннего UID оно NULL. PUTAWAY.SSCC тоже NULL для внутреннего UID; UID_PALLET содержит настоящий идентификатор. Response pallet_identifier всегда содержит физический UID, sscc содержит только валидный GS1 либо NULL. Прежний receiving UI получил общее название поля.

Регуляторный parent по отдельному скану PALLET продолжает определять ReceivingMarks/receipt_regulatory_parent125. Внутренний UID не создаёт фиктивный CRPT SSCC или внешний ACK.

Live body684 сохранён с SHA и paired rollback в [миграции](../../db/migrations/2026-10-12_ni011_internal_receipt_identifier/checkpoint.json). Подготовлено, application/VALID/actual new internal receipt ещё ожидают; native decoder check-digit классифицирует метаданные, количества не считает. Старые остатки/записи не переписываются. [[nicora_ni043_internal_identifiers_20261010]].

## Actual687–689
686 применена2/0; USER_ERRORS=[]/INVALID=[] live. Contract687: старый SSCC и новый pallet_identifier, одинаковые GS1 aliases, конфликт/длина/пробел/ошибочный check digit проверены.

Actual688: отдельный новый SAP supply по существующему private SKU669/WARE, новая паллета UID47 символов, CRPT direct UNIT3 + EGAIS BOX3. Root SAP_RECEIPT/P3H0/три новых физических единицы/шесть кодов, оригинальный PUTAWAY DONE. PALLETS.SSCC=NULL/TASK.SSCC=NULL/CRPT parent отсутствует. Exact HTTP birth replay сохранён. Исходник669 и group671 не пересоздавались; новые единицы не являются повторным рождением старых.

Первый XML fixture688 имел OrderNumber39 символов и был отклонён до импорта; сокращён до17 в том же durable NEW-контексте. Supplier order и receipt response сохраняются до последующих assertions. context688.stage=DONE; не повторять source creation, только сохранённый replay/чтение.

Actual689: старый уже отгруженный SSCC receipt669 повторён по его сохранённому CANONICAL_REQUEST, HTTP201 выдаёт точный прежний RESULT_JSON; old shipping P0/H0. Новый alias не меняет старый canonical body.

Slow689 native header insert22.989ms/667buffers, old child11.279ms/499buffers. Решение inventory: retain single bounded header insert/document lookup; увеличение длины UID не добавляет SQL или quantity writes. Индекс без плана не добавлять; native trigger/metadata plan profiling — owner inventory перед промышленным fanout. Широкая нагрузка не проводилась.

Полный внешний SAP/Gov ACK, аппаратные barcode/print checks и независимая приёмка остаются отдельными. Новый internal UID не является государственным SSCC.
