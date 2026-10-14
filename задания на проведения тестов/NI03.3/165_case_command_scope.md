# Qwen: native CASE scope и повтор после изменения доступа

MIGRATION_ID2026-10-10-165-case-current-warehouse. Проверь живые VALID RRL_CASE_TASK_ACCESS/RRL_CASE_RESOURCE_POLICY/RRL_STOCK_POSTING_API и current manifest. Не применять полный115bundle наACTIVE.

Запусти scripts/ni033_case_command_scope_existing_case.py и scripts/ni033_case_scope_wait_case.py. Первый временно меняет собственные права и uncommitted admin metadata, всегда rollback: own1031/foreign native scope, managerwithoutphysicalsession REPORT, inactive, old1030replay denied currentforeignWARE/restored exact/no events. Второй временно committed changes только Q134 fixtureWARE/manage-right и finally восстанавливает; блокирует нативный DBMS_LOCK CASE-mutex, наблюдает enq:UL wait, меняетWARE, снимает блокировку и ожидает20882 послеwait, OP отсутствует/P20H20.

Первый неудачный авторский вариант блокировалSQLbusiness-row, которую prepare не блокирует; актуальный тест использует реальный native resource mutex. Не выдавать SQLrowwait за подтверждённый.

Проверь текущее право после отзыва для CASE_CONFIRM, MOVE(rightsOR), RETURN/manage и SHORT_APPROVE/shortsource. При наличии ownSHORT используй исходныйid, не создавай fake posted history. Чтение164 повторно использует same native task scope; queue сохраняетwarehousefilter. Положительный полный HTTPCASEconfirm остаётся отдельным не пройденным сценарием. Результаты, SQL/ошибки и восстановление fixture приложить.
