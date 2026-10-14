# NI02.2: тип адресата и фактический тип сборки
14.10.2026 /1212–1219. Установлено в RABAEV/orcl.

## Общий источник планового типа
RRL_RECIPIENT_PALLET_POLICY читает существующий RRL_CUSTOMER_PALLET_TYPE_RULE. Приоритет конкретного магазина над общим клиентом, существующий IS_DEFAULT/id. Общие правила другого адреса не применяются. Планировщик и будущая генерация CASE используют один resolver, новый справочник не создан.

В legacy CASE creation сохранён прежний EURO fallback при отсутствии настройки; новый planner его не предполагает. UI явно показывает отсутствие настройки адресата. Это существующее несовпадение legacy fallback и планового unknown, не новый бизнес-default; изменить его следует отдельным согласованным правилом создания места.

## Подтверждение фактического типа
CASE_PALLET_TYPE_CHANGE — zero-quantity команда существующего Root; ожидаемая CONTENT_VERSION, текущий CASE/SSCC scan, действующий тип и причина. ROW20 CASE, HU30 CASE, штатные release/config fences и outbox70. Под row fence берётся физическая CASE-row NOWAIT, snapshot повторяется; версия растёт один раз. Только один executor меняет тип; отдельной проводки товара нет.

Разрешено до начала сборки для пустого NEW/ASSIGNED CASE без закреплённой тары, physical carrier lots, родителя HU, ячейки и привязки СТ. Уже собранное/связанное место нельзя менять переименованием — требуется существующий физический repack. UI показывает блокирующую причину и ссылку на закрепление/освобождение пустой тары. Это ограниченный сценарий; изменение заполненного CASE этим increment не объявляется готовым.

RRL_CASE_PALLET_TYPE_GUARD защищает UPDATE PALLET_TYPE_ID через private Root owner. Текущие права/склад/назначенный исполнитель проверяются; Root проверяет scope до replay. Журнал/результат/обязательный outbox прежние.

## Реальная проверка
Сохранённый empty CASE1133/wave557/WARE2318905.1215: наружный rollback, commit EURO→TROLLEY/version1, точный replay, другой body того же operation/stale version/direct DML отказаны; quantity events0/protected20/20.
1217: реальный terminal deep-link/POST TROLLEY→EURO/version2 и exact HTTP replay, ошибок страницы нет. Это empty fixture, не полная волна.
1219: readonly текущий UI desktop58/mobile59; исправлена видимость recovery при отсутствии pending.
Quality gate1216:712файлов/0cycles/76debt,24tests/обаTS PASS. Общий resolver после замены:1209 повтор PASS, query22.09ms/80buffers; retain bounded200ST/5000places/существующий индекс. Owner transport/inventory, пересмотр на release load.

[SQL](../../db/migrations/2026-10-14_ni022_case_type/apply.sql), captured source и recovery рядом; [отчёт40](../../reports/retailcase/2026-10-13/40-case-pallet-type-report.md).
