# UTC-свидетельство новой товарной операции

MIGRATION_ID `2026-10-15-stock-operation-clock`, **APPLIED**: 6 statements/0 errors; source2 exact/INVALID0. [Независимая native приёмка](retailcase_stock_operation_clock_acceptance_20261015.md):8 checks PASS, включая caller rollback и отсутствие backfill/replay clock. Владелец inventory,
потребитель resources/KPI. Основание: [[../concepts/retailcase_store_app_and_kpi_owner_20261015]].

Живой Oracle показал: RRL_CASE_PICK_EVENT.CREATED_AT, RRL_STOCK_OPERATION.APPLIED_AT,
RRL_RESOURCE_SESSION/SHIFT используют TIMESTAMP без пояса. Их нельзя молча считать
UTC или временем браузера. Обратного заполнения UTC нет; старые значения остаются
неопределёнными до доказанного происхождения времени.

Новая append-only RRL_STOCK_OP_CLOCK фиксирует только будущий переход native
RRL_STOCK_OPERATION в APPLIED. Один operation_id, исходные actor/command_type,
RECORDED_AT_UTC как TIMESTAMP WITH TIME ZONE и TIME_SOURCE=ORACLE_SYSTIMESTAMP.
Это момент наблюдения APPLIED **внутри транзакции**, не заявленное время COMMIT
и не физическое время укладки/доставки. Без commit строка невидима другим сессиям,
rollback убирает её вместе с операцией. Replay не создаёт новую строку/время.

Два новых trigger, без правки Posting API и без изменения старых столбцов. Запись
требует native Stock context с тем же TX/op и уже удерживаемого lock OP rank10.
Обновление/удаление clock запрещено. Чужой прямой APPLIED update теперь отклоняется,
а не создаёт доверенное временное свидетельство вне native writer. Не добавляет
резервы, движения, собственные проводки или outbox.

PK по operation_id достаточен для адресного чтения; временные/actor индексы пока
не добавлены без конкретного запроса/плана. Часы Oracle требуют эксплуатационной
проверки синхронизации. Это основа источников, не утверждение KPI: знаменатель
часов, атрибуция строки и момент фактической доставки ещё согласуются с владельцем.

Восстановление: paired rollback только при пустом архиве; непустая история
сохраняется и требует отдельного forward recovery. До apply — checkpoint объектов,
исходного INVALID и количества операций. После — caller-owned positive/rollback,
original replay/no backfill, direct DML rejection и проверка ошибок/INVALID.

Независимое ревью scale_protocol: ширина COMMAND_TYPE приведена к реальному VARCHAR2(80) источника. Перед rollback необходимо остановить всех stock writers: проверка пустоты сама не защищает от новых записей между проверкой и DDL.
