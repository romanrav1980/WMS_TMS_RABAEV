# Перемещение CASE без дополнительного legacy-права

17.10.2026. `2026-10-17-case-move-scope` APPLIED в dev. Свежий сквозной прогон CASE1154 выявил: prepare уже проверяет `RRL_CASE_TASK_ACCESS.assert_scope(...,'case_move')`, но execute пакета `RRL_STOCK_CASE_MOVE_CMD` дополнительно требовал flat `warehouse_task_execute`/`case_pick_execute`. Пользователь с действующей новой складской ролью получал403.

Заменена одна проверка execute на существующий authoritative `assert_scope` конкретного CASE. Он допускает текущую scoped `warehouse_task_execute` для склада задания и сохраняет прежнюю legacy-ветку с проверкой склада пользователя. Не менялись shared ACCESS_REV, release/config/stock locks, температура, физические остатки, версия состава, привязка к СТ и сканы назначения. Общие права оператору не выдавались.

Frozen kit: [миграция](../../db/migrations/2026-10-17_case_move_scope/README.md), manifest SHA256 `eeda00e5e99a37d8d0c40dbb46e9d2d5032757604bf811701eae3df0f60eae7f`; live1SHA/ERROR0/INVALID0/APPLIED. До изменения403 сохранён, после — реальное перемещение, exact replay, изменённое тело409, чужой склад403 и replay после отзыва403. CASE1154 затем прошла отгрузку/приёмку25EA, без изменения ответа прежнего перемещения. Доказательства: `reports/retailcase/2026-10-17/case-move-scope/`, `product-flow/delivery.json`, `product-flow/move-scope-denials.json`.

Итоговый readback включает53sources/17frozenkits. Slow SQL и API audit — `product-release/sql-review-final.json`; это dev-приёмка, не производственный нагрузочный норматив.
