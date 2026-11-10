# C-0192 — cleanup after mixed-pallet shipment

Read K-0220, K-0221 and K-0222. C0191 is accepted from commit `854e459e`; do not edit it.

Create an independent cleanup companion:

- `scripts/c0192_mixed_tree_cleanup.py`
- `tests/tradecase/test_c0192_mixed_tree_cleanup.py`
- `reports/tradecase/2026-10-28/claude/C0192/`
- `coordination/retailcase-claude/RESULT_C0192.md`

The companion accepts the C0190+C0191 `Live` state after LOAD/DEPART/STORE_RECEIPT. It must use current supported APIs and exact persisted commands to return root tare between distinct actors, close its tare balance, disable driver binding, retire only its own synthetic users/groups/rights, finish the wave, and verify its own fixture has no remaining stock or reservations. A departed historical tree must never be detached or returned.

Every outgoing mutation must be journaled before it is sent. A resumed run repeats the exact saved body and operation ID. Stop before cleanup if delivery is incomplete, identifiers do not belong to the fixture, or foreign rows are found. Do not delete, count down, detach, or alter unrelated data.

No live Oracle/API writes, migrations, server restarts, or publication. Run focused offline tests only. Start with an ACK in `CLAUDE_TO_CODEX.md`, then write RESULT and RELEASE. Codex owns all C0190/C0191 integration and live execution.

The root test state is warehouse `234459647`, wave `644`, CASE tasks `1182` and `1183`. It has two mistaken pre-integration ST bindings; Codex will repair these before using C0191. Do not create or repair the ST documents.
