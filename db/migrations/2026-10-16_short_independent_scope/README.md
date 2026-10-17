# Scoped independent shortage decisions - PREPARED

CASE_SHORT_APPROVE checks the original shortage CREATED_BY through the existing
RRL_ACCESS_API.assert_independent before replay and under Root locks. This
includes GLOBAL_ADMIN: a report author cannot approve their own report. Null
author fails closed. READY is readiness recovery, not a new approval, and retains
its original admission. Existing decision/policy/stock/recovery owners remain.

Only case_pick_short_approve gains the additive current role path for actual
CASE warehouse and server-resolved assignee. Legacy homeWARE/global semantics
remain; foreign flat alone remains denied. Current role is rechecked in the
writer. Root acquires rights REV before CONFIG/row locks for this command so
revocation cannot race a new decision or a replay.

No data or quantity model changes. Exact7 source guards, three body changes,
paired restore and compile/error/INVALID0 checks. Author review only; native
positive/negative/revoke/replay/concurrency and SQL acceptance still required.
