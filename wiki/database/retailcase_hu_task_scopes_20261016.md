# Назначаемое перемещение HU и прямые CASE по области склада

Статус основной миграции dev APPLIED/10SHA/ERROR0/INVALID0. Migration `2026-10-16-hu-task-scopes`; frozen SHA `636315e0ac3c5201b3e0424578d2be9b6218ecc52877c247cadf8a4d984c1da8`.

Новый HT16.c31efb0e6c, WARE40799215,3EA, actor home1/flat execute0: создание/вложение/план перемещения и ASSIGN/START/COMPLETE задания1192 PASS. Первоначальный COMPLETE безопасно откатился на вторичном legacy-only preflight. Отдельный forward-only fix `2026-10-16-hu-task-policy-scope` APPLIED/2SHA, SHA `ecda7a453c83be46b8127e4e197080ffd386c9c8bb0a1ec8297d99485dfd6954`: policy делегирует разрешение назначенного HU в `RRL_WAREHOUSE_TASK_ACCESS.assert_completion`, сохраняет resource/shift/session/equipment. Повтор исходной команды завершён после исправления; старый kit не изменён.

Native `RRL_HU_EXEC_ACCESS` дополняет basic HU: HU_PLAN_MOVE проверяет текущие фактические исходную/целевую ячейки; HU_TASK_COMPLETE — исходную/целевую ячейки собственного задания. Прямой HU_ATTACH/DETACH для CASE дополнительно проверяет фактический склад CASE. `RRL_CASE_TASK_ACCESS.case_move` принимает текущую warehouse_task_execute роль по складу CASE. Legacy ветки сохраняются.

Назначение/START/COMPLETE с новой ролью допускаются только для точного существующего HU-контракта: MANUAL/WAREHOUSE_HU/PUTAWAY/HU/PALLET/qty1, контейнер, текущий исполнитель, обе фактические области. STOCK-ограничения прежних методов не снимаются. Resource qualification/session, сканы, версии, task/closure и проводка листьев остаются в прежних owners. Root recheck до replay и под блокировками; REV fence добавлен для plan/complete.

API plan-move/attach-case/detach-case переходят на identity-only вход; решение о праве принимает Oracle до компиляции богатого состава. Это не объявление готовности остальных manager/slot/repack/shipping/driver/finance сценариев. SELF-only доступ к планированию/контейнеру не утверждён этим инкрементом; основная матрица WARE/GROUP.

SQL `db/migrations/2026-10-16_hu_task_scopes`;10 source checkpoint,6 body changes; paired source-guard rollback. Результаты — `reports/retailcase/2026-10-16/remaining-command-scopes/flow/`: задание1194 и14HTTP replay/group/revoke/foreign PASS; caller rollback и REV ORA54 PASS. Прямой attach CASE1148 прошёл current GROUP, отказ после revoke и replay после восстановления в отдельном nested flow. Остальные manager/shipping/driver/finance роли не объявляются принятыми.

См. [[retailcase_hu_scoped_execute_20261016]], [[../roadmap/retailcase_finish_two_claude_20261016]].
