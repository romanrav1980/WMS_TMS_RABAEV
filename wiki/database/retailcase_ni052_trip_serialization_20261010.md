# NI05.2 — единое назначение СТ и конкуренция с выездом
10.10.2026.080 APPLIED RABAEV/orcl. Transport owns membership; existing RRL_TT_ADD_PALL retained as sole normal writer. No stock effect and no duplicate assignment model.

Existing function previously updated ST before TT and swallowed failures as err2; unassign checked a stale snapshot in separate transactions; cancel changed ST before taking TT lock. Corrected function discovers bounded actual members, locks distinct old/new TT ascending, then actual ST IDs ascending, rechecks membership, rejects shipped/loaded/foreign-trip members and propagates failures. No commits inside function. PAY_ORDER_ID=0 remains the legacy absence-of-bill value; only positive billing ID prevents editing.

Python assign/remove/cancel share the same TT -> actual ST ID order and existing writer. Cancel refuses physical loads and bounded >200 members, releases only current unshipped membership, then marks existing TT deleted in the same transaction. The unrelated vehicle lock used by physical loading precedes TT and is never acquired later by membership writers.

RRL_TT_MEMBERSHIP_WRITER_GUARD prevents direct assigned inserts/changed membership. Secure RRL_TT_MEMBERSHIP_CTX_API is accessible only by actual legacy function, binds exact ST ID/target/transaction, clears context on success/failure; guard performs no quantity effect or extra row locking. Explicit existing CONFIG maintenance is preserved only with actual transaction/global CONFIG X fence; posting uses shared fence. New ordinary assigned inserts must create unassigned ST then use the legacy function. Existing loaded-ST guard remains independently effective.

Author scripts/ni052_assignment_serialization_case.py passed actual assign/remove, foreign-trip denial, a second Oracle session blocked on TT then rejected deleted trip without changing membership; direct write refusal and cancellation also passed. Own metadata fixtures unassigned/retired, no P/H/journal fixture created. Function/context package/body/guard verified live VALID. This is bounded author evidence, not full independent stress acceptance.

Versioned migration [080](../../db/migrations/2026-10-10_ni052_trip_assignment/apply.sql), original function source checkpoint retained. Rollback refuses reintroducing unlocked membership; forward repair preserves history.

Slow SQL: inventory lot read 7jtwv7x4r440w 7.561ms/6; existing region lookup39fu865r4fk4h7.457ms/4. Keep 201-row read limit and actual PK locks; no speculative index. Deliberate short TT wait is a correctness assertion, not a performance benchmark. NI08 owner must review ST_NUMBER/TT cardinality/actual plans on realistic volume; V$SQL_PLAN read remains unavailable in current account.

Remaining NI05.2: historical logical shipping reconciliation, confirmed unloading/compensation, real staging linkage, regulatory applicability/required ACK and independent cases. This slice does not close the full sprint.
