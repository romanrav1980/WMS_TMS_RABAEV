# Просмотр фактической погрузки по текущим областям

Решение16.10: transport owner переводит существующий status на additive legacy + current WARE/GROUP `transport_dispatch_view`. Перед чтением богатого состава определяется ограниченный набор фактических складов ST и load history; нужны права на каждый склад. Неизвестный/NULL склад не разрешается. Legacy home/global сохраняется; пустой рейс без фактического склада остаётся доступен только legacy-владельцу либо GLOBAL_ADMIN. Произвольное право одной области не открывает чужой составной рейс.

Это read-only изменение Python/Oracle predicate без миграции или новой записи товара. Auth dependency проверяет identity, authoritative scope проверяется через `RRL_ACCESS_API.allowed` в одном READ ONLY snapshot. Shipping/depart/driver SELF этим не разрешаются. Статус IMPLEMENTED,5 unit и11 live HTTP PASS; итоговый SQL review вместе с CASE return.

Источник: `modules/transport/infrastructure/loading_status.py`, `api/loading_routes.py`; прежняя проверка требовала flat transport_dispatch_view и home WARE. План — [[../roadmap/retailcase_finish_two_claude_20261016]].

Новый LS16 actor home1/flat view0 прочитал фактические рейсы33653/33654 по WARE/GROUP: свой200, чужой403, отзыв403, группа двух РЦ200/200, удаление первого склада403/оставшийся200. User/роль/группа отключены, assignments revoked, товар не менялся. `reports/retailcase/2026-10-16/loading-scoped-read/acceptance.json`. Требование всех областей составного рейса дополнительно проверено pure cursor matrix, но новый mixed-WARE физический рейс этим проходом не создавался.

Actual raw UI с отдельным UL16 actor shell-login1/legacy view/shipping0 и WARE ролью читает свой рейс33655, показывает scoped single-load форму и очищает rows/window после foreign33653/403.390px overflowfalse/JS0, native writes0; `ui-live/report.json`. Fixture нового рейса/403 очищает прежние данные до сети; durable window/load intents сохраняются. Итоговый SQL review включает86 actual pairs/max730мс, all-warehouse predicate/200rows сохраняются; transport owner проверяет планы на многоскладском пилотном объёме, не добавляет индекс без измерений.
