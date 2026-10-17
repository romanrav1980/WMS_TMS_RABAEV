# Контекст времени рейса для общего Ганта

Миграция2026-10-15-transport-time-scoped-view, APPLIED. RRL_TT_TIME_API.context использует native transport_dispatch_view по всемфактическим складам/владельцу пустого рейса. Private scope принимает view/edit, approve сохраняетedit и существующую metadata транзакцию; контекст READONLY. Native snapshot/source hash/проверка current approval не дублируются в Python. Старые approvals с SOURCE_CHANGED/LEGACY_SOURCE_CONTRACT не превращаются в действующий план Ганта.

[Apply](../../db/migrations/2026-10-15_transport_time_scoped_view/apply.sql), before/rollback/verify/checkpoint рядом. TargetRABAEV/orcl,INVALIDдо0,HEAD/SHA256доapply; поручениевладельца — общийГант и всеAK/KH. Данных рейсов/утверждений/остатков миграция не меняет. [[architecture/retailcase_resource_gantt_shift_supervisor]].

## Live verification

Oracle package/spec VALID, USER_ERRORS=0, общих INVALID=0. Native-only dispatcher view открывает свой time-context, чужой возвращает403 (общий dispatch HTTP9 PASS). Исторические33564/33570 SOURCE_CHANGED →0 projected operations: [результат](../../reports/retailcase/2026-10-15/resource-timeline/approved-clock-native.json).

ResourceTimeline использует один ORACLE_READ_ONLY снимок прав, approvals и исходных операций. aware план берётся только из native APPROVED context и original_operations с утверждённой зоной; повторная реализация хеша отсутствует. Не более50 trips с approval на окно, иначе409 с требованием сузить окно. Положительная current v7 route fixture теперь проверена отдельным caller-owned rollback сценарием ниже; старые v2 по-прежнему не считаются доказательством действующего плана. Пробные черновики откатились; на машине с floor profile обнаружен отдельный AK05-DRAFT01.

## Положительная v7 проекция · AK06-CLOCK01

[Скрипт](../../scripts/timeline_clock_positive_smoke.py), [evidence](../../reports/retailcase/2026-10-15/resource-timeline/approved-clock-positive.json): 7 native проверок PASS. Использован существующий собственный planning-only NI081 рейс33641 со складом9102 и уже настроенным depot. Явная `Asia/Tbilisi` взята из контракта исходной изолированной фикстуры, не выведена из браузера/магазина/склада. Road provider `NI081TEST`, свежие исходные плечи150/90мин; native route calculation учитывает обязательный отдых, issues пуст. Это synthetic planning fixture, не подтверждение физической площадки или реального дорожного времени.

Сначала `RRL_TT_TIME_API.approve` под admin создал текущую v7 редакцию в caller-owned транзакции: исходный package не содержит COMMIT, metadata begin/end также не фиксируют её. Native view-only пользователь без legacy/admin прав получил ровно две исходные операции со смещением `+04:00`; чужой склад отвергнут. Изменение dock штатным trip edit сделало approval `SOURCE_CHANGED` и убрало обе проекции; точное восстановление источника вернуло исходную проекцию. Отзыв view-назначения закрыл доступ к ранее разрешённому clock. В `finally` откатились approval, права, пользователи и изменения источника: хеш/версия равны исходным, запись операции и RUSERS фикстур отсутствуют. Строки остатков и physical admission не изменялись.

Публикация approval проверена под admin; это **не** доказательство native-only write для scoped dispatcher: общий metadata transaction всё ещё требует legacy permission, остаётся в очереди команд AK05/AK06. Отдельный historical READ ONLY smoke33564/33570 повторно PASS: оба SOURCE_CHANGED, операций0. В том же тесте положительный uncommitted approval виден собственной транзакции; новая самостоятельная READ ONLY транзакция после rollback уже не содержит этого approval.

Live package USER_ERRORS0/globalINVALID0. Native approve208.43мс; `RRL_SQL_SLOW_LOG` за час пуст, bounded `V$SQL` поиск по именованному NI081_ROUTE_LEGS не вернул метрик — это отсутствие evidence плана, не доказательство нулевой стоимости. HTTP API audit не генерировался, поскольку вызовы native. Решение transport/Codex: сохранить границы200 членов/операций и2000 строк источника; новых индексов не добавлять, при повторении >1000мс атрибутировать запрос и проверить план. AK06-CLOCK01 закрыт как положительная v7 native projection; совмещённый пилот общего Ганта отдельно.
