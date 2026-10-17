# Assigned inventory task scope — PREPARED

Package-only extension; no quantity table, new writer, role grant or fixture data.
Claim owns begin_plan -> rights REV -> CONFIG/metadata/task/actor locks, then
rechecks both inventory_task_execute and stock_inventory_count on actual WARE.
An unassigned task needs a WARE/GROUP grant; SELF covers the current assignee.
Scoped counts require an IN_PROGRESS assigned task, revision/warehouse and exact
cell/article; DONE accepts only the original count operation replay. Standalone
legacy counts retain flat permission and homeWARE/global-admin semantics.
Legacy task paths keep existing owner/domain/session/stock/marking invariants.
Canonical root rechecks before replay and after rights/config/row fences. Current
native inventory/short-recovery owners still perform all quantity and journals.
Lots/profile reads share a READ ONLY snapshot with native authority and bounds.
Revision creation and lot birth HTTP remain flat-gated; this is not permission
to create stock or global revisions using a SELF count role.

Before images and all dependent source hashes guarded; paired rollback restores
old package bodies then drops the stateless helper. It preserves all history,
quantities and assignments, while removing scoped-only execution capability.
Native positive task/recovery/HTTP/replay/revoke/concurrency and SQL acceptance
pending. Author review only; no hardware or independent acceptance claimed.
