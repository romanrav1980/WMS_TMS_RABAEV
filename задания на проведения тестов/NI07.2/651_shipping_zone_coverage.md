# NI07.2 / 651: классификация грузовой зоны по опубликованной схеме

Для локальной Qwen; запуск/независимая приёмка не заявлены. Source wiki/components/nicora_ni072_shipping_coverage_20261012.md.

Проверить existing shipping-register/reconciliation на собственной временной topology и реальном остатке: каждую current WMS ячейку связывает ровно один active published recognised-role row. Полный каталог + пустые staging/gate/film-wrap/legacyexpedition => registered area empty at snapshot. Наличие stock/container/CASE => occupied и empty=false. Не объявлять весь физический склад обследованным.

Отказы полноты: нет published topology, новая/немаппированная legacycell, EMPTY/неизвестная роль, два alias rows (в том числе valid+invalid), чужой warehouse mapping, shipping cells отсутствуют, >500 shipping cells. Сообщение показывает≤20 проблемных ячеек; reconciliation open item остаётся. Исторический review replay сохраняет старый результат.

Одна read-only snapshot и текущие actor/WARE права обязательны. Не запускать641/642/643 source factories или650 повторно без собственной isolated fixture. Temporary metadata rollback должен оставить stock/old topology unchanged. Не закрывать день автоматически и не подделывать ERP/Gov ACK. Scoped SQL/bounds decision, без полного регресса/нагрузки.
