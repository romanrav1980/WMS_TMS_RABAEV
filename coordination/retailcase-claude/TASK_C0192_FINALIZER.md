# C-0192 follow-up — durable retirement finalizer

C0191 rework 2 is accepted. This is a follow-up inside the original C0192 cleanup request, not a new request. C0192 owns only its source, focused tests, report, and RESULT. Do not edit C0190 or C0191.

Codex added the root-owned Live.finalizer_sql(key, sql, binds, verify_sql, verify_binds, expected) in C0190. It persists the exact SQL/arguments and verification query before execution, reconciles only the same command on resume, and blocks unknown outcomes until exact verification.

## Required result

Replace the C0192 retirement stop with a safe finalizer:

1. Keep the completed delivery cleanup stages unchanged and keep a departed historical tree untouched.
2. Retire only the run's synthetic driver and receiver. Validate both identifiers before every mutation.
3. Remove the receiver's receipt right through the existing journaled admin API. Use finalizer_sql for each direct RUSERS/RIGHTS mutation and use exact scoped verification.
4. Determine the expected rights state from the fixture state or a read-only preflight before the first deletion. Do not treat an arbitrary pre-existing zero-row state as a successful first execution.
5. After every retirement step, persist progress. Resume must reuse the stored command, not repeat a completed API or SQL operation.
6. Add offline tests for normal retirement, a post-commit reconciliation, changed finalizer content refusal, foreign user refusal, and resume without duplicate API/SQL calls.
7. Do not run live Oracle/API work, migrations, restarts, or publication.

Start with ACK in CLAUDE_TO_CODEX.md, then provide RESULT/RELEASE. Wait for Codex acceptance.
