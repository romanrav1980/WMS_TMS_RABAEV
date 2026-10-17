# GROUP-only CASE1138 quantity proof — PREPARED, NOT EXECUTED

Scope: one existing isolated CRES15.OP / CASE1138 / line1140 / wave569 / resource59 / session55. Current zero-picked CASE and active actual resource/session are mandatory. No new CASE, reservation, role, quantity commit, physical device or Oracle DDL. ROLE CRES15.CASE.EXEC stays active version3 and is never edited. No WARE/DC/global object or parent hierarchy mutation.

Runner: `scripts/case_group_quantity_proof.py`. Default `--plan` imports no Oracle and writes no journal. Execution and restore mode require both explicit root-reviewed and exclusive UI/cleanup-window environment flags. Preparation refuses a retired/closed CASE, actor/role changes, active OPEN/BLOCKED/HOLD ASM, changed source, unexpected existing proof namespace/history, or a window too close to18:25 MSK. This file and runner are proposals; no SQL/ACL was run by the author.

## Exact sequence after independent review and root release

1. Read bounded snapshots of CASE/line, parent REUSE.RETURN:e6c16d0bbd23/H1/version12 and returned CASELOT:E8EAB9A962B9D19BA5AC8FCEE19D8021895BD0:1 at1/H0, source lineage, reservations, CASE events, existing metadata receipts and actual warehouse object. Verify no orphan proof operation/clock/outbox/newlot/carrier/STEP_USE. Resource-fact TASK_ID1138 is only an additional warehouse-task-namespace guard, not a claimed CASE event source.
2. Require exactly the original CRES15.SELF and CRES15.WARE assignments, active role version3 and legacy flat CASE execute0. Freeze every metadata command and both original restoration intents, exact Stock request bytes and hashes in an atomic UTF8 journal; flush and fsync before ANY ACL mutation. No operation IDs or payloads are regenerated during recovery.
3. In independent canonical ACCESS owner transactions: create only private GROUP CRES15.GQP.WARE containing actual warehouse13583852; assign only CRES15.OP via CRES15.GQP.ASSIGN; canonically revoke the two original assignments with exact versions. Native original-revoke receipts are retained. GROUP grant expires no later than18:25 MSK.
4. Verify exactly one effective GROUP grant and no WARE/SELF/NETWORK/DC/global alternatives; flat execute0, native current scope1 and scoped_executor1. Open a fresh physical connection. Native prepare_command, then SAME-CURSOR GROUP-only/flat0 checks under the native access revision fence, then execute_prepared. Recheck same-cursor GROUP-only/native admission after execute. Observe APPLIED, picked1, parent22/H0 and new carrier lot, operation clock and outbox inside the transaction. Always rollback and reset in finally; no StockPosting.post or connection.commit exists in the physical phase.
5. Require exact before/after CASE/line/both-UID lineage/reservations/events/resource metadata receipts and absence of operation/clock/outbox/newlots/carrier/STEP_USE. Native refusal from current scale/physical policy is a failed proof with its actual reason, never a bypass.
6. Finally restore original effective WARE/SELF permissions and original validity through NEW frozen assignment IDs CRES15.GQP.RESTORE.WARE/SELF. Never reactivate revoked IDs. Restore only if the original is still its exact saved source/version+1 and the immutable ACCESS receipt proves OUR matching admin/hash original revoke; foreign or later concurrent revoke is not overridden. Always attempt retirement of the exact private GROUP grant/group, even if fixture checks or progress logging fail. No actor, role, CASE or session is reactivated.

## Recovery and boundaries

`--restore-only` loads the initially fsynced journal even when no proof result/report exists. Every command is reconstructed against hardcoded approved ACTOR/ROLE/GROUP/assignment IDs, actual WARE/SELF scopes, original validity and exact Stock target/quantity. A merely self-consistent changed hash does not authorize a retargeted journal. Original scope/validity is additionally checked against its immutable live assignment source before restoration.

A disk-full error in progress logging does not suppress already-fsynced canonical compensation attempts. Lost metadata ACK uses the same operation/body and native receipt. If database connectivity fails, role/actor was legitimately retired, a foreign revoke occurred, or saved journal is corrupt: stop, preserve all history and report pending compensation to root; never invent new IDs, broaden rights or delete history. Private group cleanup is attempted even when restoring original rights is blocked. Root must not begin18:35 fixture cancellation until this ACL window is explicitly released.

Expected persistent changes are ONLY ACCESS revision/audit/command history, revoked originals, equivalent new WARE/SELF assignments and retired private GROUP history. CASE/quantity/event/stock clock/outbox effects are rollback-only; sequence gaps are not reset. No real hardware or HTTP proof is claimed by this runner.

## Preparation evidence

- Author ran only py_compile and six pure mocked tests: hardcoded whitelist rejects rehashed retargeting, physical request cannot change, fixture/disk failure still reaches private cleanup, compensation is attempted despite disk failure, default plan is Oracle-free, foreign revoke without our native receipt is never undone.
- Parent supplied read-only schema checks in `group-proof-schema-read.json`; author did not execute SQL.
- Independent review: scale_protocol; actual runtime proof is NOT YET RUN.
