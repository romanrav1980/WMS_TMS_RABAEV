# C-0192 rework — durable cleanup mutations

C0192 RELEASE K-0224 is **not accepted**. It is a rework of the same C0192 request, not a new budget request. Do not edit C0190 or C0191.

## Ownership

Keep ownership limited to:

- `scripts/c0192_mixed_tree_cleanup.py`
- `tests/tradecase/test_c0192_mixed_tree_cleanup.py`
- `reports/tradecase/2026-10-28/claude/C0192/**`
- `coordination/retailcase-claude/RESULT_C0192.md`

## Blocking defect

`MixedTreeCleanup.retire()` executes direct `RUSERS`/`RIGHTS` DML through `connect()`. Those mutations have no persisted command, no operation identity, and no reconciliation after a post-commit failure. This contradicts the task rule: every mutation must be persisted before execution, resume must use the stored command, and an unknown result blocks later steps.

## Required correction

1. Do not perform direct user or rights DML in the companion unless C0190 exposes a durable, journaled mutation helper with an exact stored command and read-only reconciliation. Codex currently does not expose one.
2. Preserve all completed safe stages (tare return, binding off, wave finish, own stock zero) and stop before retirement with a precise code such as `RETIRE_REQUIRES_DURABLE_OWNER_FINALIZER`. The result must say that cleanup is incomplete and why.
3. The stop must occur before direct DML and must not mark `retire` completed. A resumed run must retain completed previous stages and repeat no completed API command.
4. Update offline tests for the new stop and resume. Tests must prove no direct SQL/user mutation runs after the stop.
5. Keep the departed historical tree untouched. No live Oracle/API writes, migrations, server restarts, publication, or changes to C0190/C0191.

Start with an ACK in `CLAUDE_TO_CODEX.md`. Then provide RESULT/RELEASE. After this rework, read K-0224 in `CODEX_TO_CLAUDE.md` and proceed to the already queued C0191 DOCID/recovery rework only after its ACK.
