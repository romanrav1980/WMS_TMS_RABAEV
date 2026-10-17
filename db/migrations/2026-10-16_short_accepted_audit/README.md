# Accepted-short inventory audit - PREPARED

CASE_SHORT_APPROVE ACCEPT_SHORT creates an automatic inventory task when the
existing policy enables it, but the old count owner required WAIT_INVENTORY
restoration state. This left ordinary accepted-short audits unfinishable.
The existing SHORT_RECOVERY owner now freezes explicit ACCEPT_SHORT/RESTORE
mode, rechecks source/task/line/state under old locks and completes the ordinary
audit without reopening the short line or creating replenishment. The RESTORE
transition remains unchanged. Same count/balance/unit writer, no table/data
changes, caller rollback and exact replay. Scope/assignee/session/qualification,
whole cell/SKU lot observation and count fences remain mandatory.

One guarded body/four current source guards, exact paired rollback. No journal
deletion or retrospective conversion of existing shortages. Author review only;
native positive count and RESTORE regression acceptance pending.
