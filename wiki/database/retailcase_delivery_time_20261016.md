# Плановое окно и прибытие машины

Статус: dev APPLIED,9 source SHA/ERROR0/INVALID0. Migration `2026-10-16-delivery-time`, frozen SHA `39e1c7d52fef39692ed7650a8262e7814f3c0078745821f182eb93fe16ce5644`. Первое применение остановилось только на проверке видимости ALL_CONTEXT после успешного DDL; повторного DDL не было. Completion `db/migrations/2026-10-16_delivery_time_completion` SHA `359092a75a7806816db27a03cd44213658fd3fd9a8a89e363ba115716f907844`: exact source guard, native trusted-owner probe и запрет внешнего set_context, ограничения/индексы, затем ledger. Исходная ошибка сохранена.

Новая CASE1147/WARE20790457: BOX24+EA1, ручной QC, одиночная погрузка LOAD_SHIPMENT, поездка33653, план до выезда, aware ON_TIME и PAPER_COUNT25EA/FULL PASS. Replay/conflict/foreign403 и запрет переноса окна после выезда проверены actual HTTP. Статус старого «грузового дерева» /confirm не используется для одиночной ST: нужен штатный /confirm-single с composition signature. В приложении магазина добавлена отдельная отметка прибытия с durable прежним временем/operation_id и статической справкой; браузерная приёмка ещё впереди.

SQL review:33 HTTP/audit pairs, max1304мс;11 slow-log строк. Наибольший native SQL2.55с — dictionary USER_CONSTRAINTS на DDL gate, не KPI/складская операция: владелец operations/schema verification должен заменить общий dictionary scan точными named constraints/проверкой плана до массовых миграций. QC read829мс — backlog inventory: разложить access/admission/source read на pilot объёме, проверить план/статистику; не добавлять speculative index/cache. KPI остаётся bounded31день/500доставок; profile cohort/JSON warehouse extraction до нагрузочного pilot. Shared V$SQL averages не объявляются endpoint p95.

`RRL_DELIVERY_TIME_API` сохраняет версии планового окна до выезда и отдельное подтверждённое пользователем прибытие машины. Все моменты — timestamp with time zone. План после выезда неизменяем; прежние записи не исправляются. Повтор прежнего operation_id с тем же каноническим телом возвращает прежний результат, другое тело отклоняется. Текущая область проверяется и для повтора.

Окно задаёт диспетчер фактического склада погрузки. Прибытие подтверждает текущий диспетчер, привязанный водитель рейса либо приёмщик магазина. Магазин берётся из замороженного состава погрузки. Метаданные не проводят товар. REV и CONFIG защищают полномочия, блокировка погрузки сериализует план с выездом. Вставка только через доверенный native owner; UPDATE/DELETE запрещены триггерами.

Таблицы `RRL_DELIVERY_WINDOW` и `RRL_DELIVERY_ARRIVAL` — журнал плана и прибытия; не заменяют рейсы, складские проводки и приёмку. При отсутствии плана возвращается NO_PLAN; даты legacy без пояса не восстанавливаются предположением.

API `/api/delivery/timing`: POST window, POST arrival, GET place, GET kpis. KPI ограничен одним разрешённым складом и периодом до31дня/500доставок. Вовремя — прибытие внутри включительных границ окна. Полностью — native приёмка ACCEPTED без недостачи, отказа, повреждения и расхождения строк. Ожидающие факты показаны отдельно; проценты по наблюдённым фактам имеют явный знаменатель.

SQL: `db/migrations/2026-10-16_delivery_time/`; результаты — `reports/retailcase/2026-10-16/delivery-time/`. Перед DDL проверяются target, исходные SHA, пустое пространство имён и отсутствие INVALID. Rollback разрешён только без сохранённой истории; затем нужен forward recovery.

См. [[concepts/retailcase_kpi_passports_20261015]], [[roadmap/retailcase_finish_two_claude_20261016]].
