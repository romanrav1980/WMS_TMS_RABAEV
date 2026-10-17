# Список ожидаемых консолидаций склада

Dev APPLIED, live page/cursor проверены; отдельная scoped матрица ещё открыта. Продолжение [[retailcase_consolidation_manifest_20261016]]:
старший смены находит ожидаемые места до появления физической паллеты.

Владелец fulfillment. Новый pure `RRL_HU_CONSOL_LIST`, прежние metadata/quantity
owners не меняются. GET `/api/consolidation-plans?warehouse_id=...` требует
выбранный склад и текущий warehouse_task_view. Текущие области всех источников
и корня проверяет прежний assert_plan_scope; SQL can_view фильтрует до FETCH.
Скрытые планы не занимают места страницы и не участвуют в счётчике.

Выдача1–50 строк, default30, status ACTIVE/CANCELLED/ALL, default ACTIVE;
ключ after — plan_id в явном бинарном порядке. Один READ ONLY snapshot на страницу,
без общей блокировки прав и без обещания неподвижного набора между страницами.
При смене склада UI сбрасывает cursor. items содержат plan/version/status,
целевые склад/ячейку/идентификатор паллеты, expected_count и updated_at UTC.
Полнота и QC не вычисляются для всей страницы: детали открываются прежним GET.
has_more/next_after относятся только к доступным строкам, общего total нет.

Ошибочный размер/склад/cursor/status отклоняются; явно чужой склад403.
Native can_view скрывает только отказ20882 и исчезнувший план1403; остальные
ошибки не маскируются под пустую страницу. API actor только из действующей сессии.
Поведение legacy/global/group и отзыв остаются у RRL_ACCESS_API.

Fresh checkpoint: [5 sources/INVALID0](../../reports/retailcase/2026-10-16/consolidation-list/before/manifest.json).
Комплект: db/migrations/2026-10-16_consolidation_list, migration ID
`2026-10-16-consolidation-list`, SHA5b167933313312b1859ca8bf761aea48a93b51d7e9afaee5e644d0d1f221458e.
[Apply](../../reports/retailcase/2026-10-16/consolidation-list/root-apply.json),
[readback](../../reports/retailcase/2026-10-16/consolidation-list/root-readback.json):
7 source hashes совпали, USER_ERRORS0/INVALID0, ledger APPLIED. Старые пакеты
не изменены; парный rollback удаляет только новый read package после возврата
Python consumer. Quality gate1102/0циклов/debt72/tooling24/обаTS PASS.
[Live page/cursor](../../reports/retailcase/2026-10-16/manual-weight/http-read.json):
admin ALL limit1 возвращает CANCELLED future plan, следующий cursor — ACTIVE mixed
plan, has_more/next_after корректны;343/76мс. Никаких новых планов/запаса для этого
read не создавалось. Source scopes переиспользуют прежний assert_plan_scope;
это не новая полная scoped pagination/revoke/NLS matrix. SQL decision: выбранный
WARE, keyset/max50, доступ доlimit; объём кандидатов/бинарный sort проверить на
пилоте, без предполагаемого индекса. Массовый регресс/нагрузка сейчас не запускались.
