# CASE transit WARE13583852 · 15.10.2026

Статус APPLIED координатором: 1 statement/0 errors. Независимая read-only verify.sql PASS: exact cell/key v1 LOCK_ID900074177/ledgerAPPLIED, P24/H1/V10+zeroV2 без изменений, active USER_ERRORS0/globalINVALID0. Старые recycle BIN$ errors учтены отдельно, не являются active-object errors. [Migration +paired empty-only rollback](../../db/migrations/2026-10-15_case_transit_13583852/). Это metadata repair, не количественная операция.

Настоящий scoped CASE callerrollback остановлен `POLICY_KEY_NOT_PUBLISHED`: canonical CASE_PICK_CMD использует CPT_13583852, но ни ячейки, ни CELL policy key для нового склада нет. Ключ `313A32343A43454C4C31323A4350545F3133353833383532`. Quantity transaction откатан. Четыре resource guard и sender/foreign CASE denial прошли до этой остановки; после metadata repair положительный scoped stock callerrollback и revoke-concurrency прошли, без goods commit.

Ранее transit материализовал PREPARED-only global script 165_case_transit_cells.sql, policy публиковал ACTIVE-safe 004_transit_fences.sql. Runtime create-transit owner не найден. Новый ограниченный kit использует существующий RRL_STOCK_CONFIG_API.begin_change(admin,warehouse_settings_edit), проверяет current GLOBAL_ADMIN, release ACTIVE/PREPARED, точный WARE/CASE1136/context, отсутствие ASM, исходные P24/H1/V10 и историческую zero-row V2, отсутствие transit cell/stock/key. Создаёт одну system ячейку OTBOR0/blocked remains+replenishment и один published policy key с range/exclusive policy table guard. Stock release и количественные таблицы не изменяются. Rollback отказывает при любом transit stock/history или picked/legacy CASE на этом складе и не удаляет использованную историю.

**Backlog: inventory owner.** Инициализация нового WARE должна штатно атомарно материализовать/публиковать CASE transit через metadata owner до первой волны: operation receipt, current warehouse settings scope, exact config conflict, CONFIG fence, idempotent repeat. Глобальный PREPARED seed не покрывает появившиеся позже склады; этот kit намеренно чинит ровно один согласованный склад.

[[retailcase_case_scoped_write_audit_20261015]].
