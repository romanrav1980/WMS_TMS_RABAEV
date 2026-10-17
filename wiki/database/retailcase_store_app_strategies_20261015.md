# Приложение магазина: стратегии и область

15.10.2026. APPLIED2026-10-15-store-app-strategies. По прямому решению владельца добавляется PAPER_COUNT к BARCODE/WEIGHT_PHOTO. Обязательны реквизит бумаги и явные counts всех физических STOCK листьев; существующий resolve_counts проверяет полноту, дубли, единицы и сумму accepted+missing+refused+damaged. Маркировочные проверки, физическая идентификация места, камера, разгрузка и независимые доказательства веса не обходятся.

Native require_receiver принимает explicit STORE assignment по SHA256 UTF8 адреса либо прежнюю пару legacy право+receiver binding. Чтение pure, command compile удерживает revision SHARE до результата. Старые группы/привязки не удаляются. Результат фиксирует receipt_mode/policy_version/paper_reference, исходное тело остаётся в каноническом журнале; второго writer нет.

[Apply](../../db/migrations/2026-10-15_store_app_strategies/apply.sql), before/constraint/checkpoint/verify/rollback рядом. Откат отказывается при настроенных PAPER_COUNT магазинах; молчаливой замены стратегии нет. [[concepts/retailcase_store_app_and_kpi_owner_20261015]], [[roadmap/retailcase_access_knowledge_plan]].

## Проверка порядка блокировок

Rollback-only положительный бумажный сценарий обнаружил DIRTY_TRANSACTION: revision SHARE до begin_plan создаёт транзакцию. Переделывать/ослаблять no-prewrite invariant нельзя. Follow-up2026-10-15-scoped-command-lock-order переносит revision guard внутрь оригинального prepare сразу после begin_plan, до policy/resource locks. Ранние проверки чистые, финальные после locks повторяются. [Apply](../../db/migrations/2026-10-15_scoped_command_lock_order/apply.sql), before/checkpoint/rollback рядом. Это исправление собственного нового guard; физическая приёмка при неудавшейся проверке не сохранилась, временная dev-стратегия возвращена.

Положительная фикстура на старом IW291 оказалась промежуточным плечом: существующий insert-trigger правильно отказал STORE_RECEIPT_INTERMEDIATE_LEG_NOT_FINAL. Чтение раньше его показывало. Follow-up2026-10-15-store-app-final-leg переносит тот же критерий в native preview и оба серверных списка ДО limit; trigger не ослабляется. Старое плечо не подменяется финальной поставкой. [Apply](../../db/migrations/2026-10-15_store_app_final_leg/apply.sql), before/rollback/checkpoint рядом. Проверки бумажной приёмки продолжаются на финальной dev-поставке.

Scoped STORE_RECEIPT проверяется до compile и повторно под revision guard, включая replay (2026-10-15-store-command-current-access). Отозванная роль не читает полный результат через POST. [Apply](../../db/migrations/2026-10-15_store_command_current_access/apply.sql), before/rollback/checkpoint рядом.

### Реальный эффект теста

Тест THERMAL1168.LOAD:f8e5e3b899 вызвал RRL_STOCK_NATIVE_API.post, который сам делает COMMIT. Поэтому PAPER.ROLLBACK:41005408317040d0b433353978c38d9a:2 является сохранённой DEV-приёмкой ACCEPTED, а не rollback-only. Имя ключа историческое и не переписывается. Режим Own full-pallet ST возвращён к BARCODE; изменение версии настройки сохранено. Журнал/факт не удаляются. Повторный warehouse stock не списан (native result warehouse_stock_consumed_again=false). Новые rollback-проверки используют prepare_command/execute_prepared с внешним владельцем транзакции. Ошибка теста сообщена владельцу.

## Текущее подтверждённое состояние

Миграции strategies → scoped-command-lock-order → final-leg → current-access APPLIED. Native packages VALID/USER_ERRORS0/INVALID0; проверка исходников сравнивает живые тела с последними SQL, а не с уже заменёнными ранними версиями. [Verifier](../../scripts/store_app_verify_oracle.py), [результат](../../reports/retailcase/2026-10-15/store-app/oracle-verification.json).

Store-only пользователь NONE/PRAVO_ADMIN_LOGIN0/безwarehouse с одной native STORE ролью: session/list/preview, чужой магазин403, wrong-password401, scoped cursor и отзыв — live API/native PASS. Через caller-owned prepare_command+execute_prepared выполнена полноценная dev BARCODE приёмка, затем подтверждён rollback обеих строк journal/receipt. [Проверка](../../scripts/store_receipt_native_rollback.py). NativeAPI.post для rollback-сценария больше не вызывается.

Оригинальная сохранённая PAPER_COUNT dev-приёмка дважды повторена под неизменным operation_id: тот же результат, одна receipt на load, другое paper_reference — OPERATION_CONFLICT. [Результат](../../reports/retailcase/2026-10-15/store-app/paper-native.json). Это отдельный сохранённый dev-факт, а не физическая приёмка реального магазина.

Самостоятельный UI /store/ проверен на390px реальным scoped пользователем: список и состав, no overflow/no browser errors/no POST/no password storage. Первый запуск3010 оказался старым установочным dev-проектом в tmp; root terminal.bat переключён на текущий terminal/wms_terminal_web. Полная приёмка после замечаний Claude, production build/PWA и offline ещё в работе.

Slow SQL4442–4444: поиск SEARCH_CONDITION_VC в Oracle USER_CONSTRAINTS занял2.4–5.5с, это миграционная диагностика, не runtime магазина. Решение: выполнять только при подготовке/verify миграции, ограничивать именем таблицы/constraint; SYS-индексы не добавлять. CASE/task queue4405/4413/4420/4422/4433 —0.55–0.67с на bounded выборке; явный склад и ранний фильтр сохранены, индекс без плана/повтора>1000мс не добавлять.
