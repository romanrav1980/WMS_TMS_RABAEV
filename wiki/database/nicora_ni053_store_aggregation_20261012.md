# NI05.3 / NI06.1: агрегационные сканы магазина

Native716/722 APPLIED, USER_ERRORS=[]/INVALID=[]. RRL_STORE_AGG_SCAN переиспользует существующий RRL_IW_AGG_SCAN: исходник рождения агрегации, текущая версия/режим карточки, состав и lifecycle. Код коробки/паллеты разворачивается в исходные единицы; решение ACCEPTED/REFUSED/DAMAGED распространяется на всю отсканированную агрегацию. Совпадение всех профилей одной штуки и точное количество по каждому товарному листу проверяет прежний RRL_STORE_MARK_CORE. Несколько кодов одной штуки не увеличивают товарный запас.

Прямой скан BOX/PALLET-профиля запрещён по exact physical key/current profile, а не по совпадающему имени профиля другого SKU. Скан чужого агрегата не проходит исходную матрицу выданных единиц. Сохраняются пределы1000 агрегатов/20000 развёрнутых сканов. Паллетный код означает исходную неизменённую агрегацию, а не произвольный родительский WMS контейнер.

722: нормализация приёмки магазина выполняется в verify_scans и передаёт validated_store_scans в server proof. Общий resolve_disposition сохраняет прежний путь для возврата, где агрегаты уже развёрнуты RRL_STORE_RETURN_UNIT_CORE. Это исключает повторное разворачивание и ошибочный запрет штатного возврата. Native spec change recompilation выполнена для трёх зависимых пакетов. Источники/SHA и rollback сохранены в миграции.

Actual717: context671 группа после принятой mixed warehouse receipt673, размещения702 и второго load711/depart712 принята магазином. Шесть исходных physical keys/девять профильных кодов; direct CRPT первого SKU, обе EGAIS BOX и CRPT PALLET второго. Оба исходных заказа: shipped3/accepted3/missing0/unreceived0. Exact native replay сохранён; P0 после load. Existing order projection, store facts и stock owner сохранены.

API718 DTO/normalization и прежняя форма поддерживают UNIT/BOX/PALLET, решения состава, source-scoped draft и неизменный pending body. Предыдущий UNIT draft мигрирует без удаления. Повреждённый draft блокирует новую команду. Full offline quality718 PASS24+оба TypeScript. Browser/hardware acceptance ещё не выполнена.

HTTP720: delivered2 подтверждён. Попытка повторить direct717 через HTTP даёт409 OPERATION_CONFLICT: HTTP удаляет пустые optional поля, исходный внутренний вызов сохранил их. Это другое canonical body, не успешный HTTP replay. Для независимой проверки новый приёмочный источник создавать через HTTP с самого начала.

719 не выполнен: private native package недоступен из anonymous PL/SQL; доступ не расширялся. 723 discovery отказал раньше на STORE_PLACE_ALREADY_RECEIVED, поэтому эти попытки не доказывают отрицательные ветки нового resolver. Положительный actual717 доказан до scope722; после scope722 native compilation и сохранённый outcome проверены, новый положительный источник нужен для независимого полного цикла.

SQL720 exact-key profile check16.237мс/75.5buffers (2 исполнения), прежний address14.289мс/7buffers. Решение: оставить ограниченное чтение с существующими индексами кода/единиц; delivery владеет проверкой плана и batching перед промышленными20000 сканов. Нет глобальной нагрузки.

[Миграция](../../db/migrations/2026-10-12_ni053_store_aggregation/apply.sql). Полная приёмка спринтов, реальные SAP/Gov ACK и физический терминал остаются открыты.
