# CASE/TASK metadata intent recovery — PREPARED

Owner resources; native authority remains existing CASE_ASSIGNMENT/WTASK_ASSIGN owners. Migration `2026-10-15-resource-metadata-intents` is **PREPARED, NOT APPLIED**. Python routes are not registered/composed/exported. No native fixtures/POST/DDL executed by author.

## Contract and compatibility

A separate explicit POST `/api/resources/metadata-intents/abandonments` carries `{operation_id,domain:CASE|TASK,task_id,reason,original_wire}`. The original string must equal the existing domain command builder's canonical bytes. Actor is obtained from authenticated server identity. Domain+original operation is globally unique, matching existing per-domain original receipt keys. A separate control operation cannot equal the original operation.

ABANDONED means the original metadata command has never recorded APPLIED **or REJECTED** and is fenced against all later execution. It does not cancel a task, release a reservation, change a resource assignment, reset time, or alter quantities. Original expected version/hash and actual current assignment version at abandonment are stored. A stale original expected version is recoverable; version equality is not fabricated as a prerequisite for proving absence.

Original receipts retain their exact old DTO/enum/canonical bytes. If the original receipt already exists, POST refuses RECORDED_READ_REQUIRED; UI can resolve the original exact ACK instead, without calling it ABANDONED. `GET /resolution` accepts domain/task/original operation/action/target/original uppercase SHA256 and returns RECORDED + original receipt, ABANDONED + original tombstone, or404 UNKNOWN. `GET /abandonments/{control}` reads immutable control ACK. Both paths recheck current authority and original actor. Revoked/foreign/reassigned/unsupported scope does not become an admin bypass.

## Native locking and source patches

New helper/table/context/append-only trigger. Only two existing owner spec/bodies are changed: a narrow current-authority/version wrapper and an execute hook **after exact old receipt lookup, before effects/recoverable rejection block**. Tombstoned original requests always fail unconfirmed409; no later APPLIED/REJECTED original receipt is created, even for changed body/task/actor.

Fresh clean begin_plan → ACCESS_REV SHARE → RELEASE S / CONFIG WAREHOUSE X → original OP10 (`CASE.RESOURCE:` or `WTASK.RESOURCE:`) and control OP10 (globally sorted by existing lock API) → metadata guard/WAVE/task/user ROW20. Under real task locks, source WAVE/document is rechecked and current authority repeated. Session readiness is not required to abandon an unavailable-session intent. The helper never starts another plan inside existing execute locks; its hook verifies the original OP lock. Failed lock acquisition clears only a plan successfully started by this helper, not an unrelated caller plan.

## Apply and rollback boundary

Before4 source SHA guards + own object namespace/ledger/errors/INVALID checks. After7 exact source guards + table/constraint/context/error/globalINVALID verification precede APPLIED ledger commit. Current RABAEV has no USER_CONTEXT/DBA_CONTEXT dictionary access; ALL_CONTEXT zero is not claimed global absence. CREATE CONTEXT must stop on collision; retain partial evidence and coordinate a forward completion, never auto-drop/retry.

Root alone applies DDL sequentially after review/quiescing metadata writers. It must preserve partial-failure evidence and verify exact sources/live errors. Rollback only with exact applied source set **and zero tombstone rows**; otherwise forward repair. It restores the four captured owner sources and drops new objects, then checks exact original sources/errors/globalINVALID. New HTTP composition must be disabled before rollback. No baseline/policy/Stock writer changes.

## Required native acceptance (root, not yet run)

- No receipt: create ABANDONED, exact control retry/read/resolution, changed actor/task/body/control conflict and unsupported scope deny.
- Existing APPLIED and existing REJECTED: authoritative resolution returns exact old receipt; abandon refuses; old original replay unchanged.
- Real two-session waits both orders: original transaction wins→abandon waits then refuses; abandon wins→late original waits then refuses with no original receipt/event/version change. Abandon rollback→original remains executable.
- Current revoke, SELF reassignment, source warehouse/current cells or TASK target change, task identity ABA/version guard; no stale scope fallback.
- Direct table UPDATE/DELETE/INSERT refused; dirty-Stock entry refused without clearing caller plan; lock timeout followed by clean pooled reuse.
- Caller rollback restores tombstone/task/source/assignment/version/event/resource histories; no Stock operation/clock/outbox/quantity changes. Frozen current-source snapshots and SQL attribution accompany the real proof.

Unloading START is explicitly outside this increment. Its unknown intent remains blocked until its own owner-specific fence/receipt contract is implemented. UI composition/recovery controls and native business acceptance are separate remaining work.
