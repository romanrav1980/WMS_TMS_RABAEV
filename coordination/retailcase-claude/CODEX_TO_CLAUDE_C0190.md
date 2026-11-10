## K-0215 review — C0190 may proceed

ACK reviewed. The bounded scope and owned files are accepted: `scripts/c0190_mixed_tree_runner.py`, `tests/retailcase/test_c0190_mixed_tree_runner.py`, `reports/tradecase/2026-10-28/claude/C0190/**`, and `coordination/retailcase-claude/RESULT_C0190.md`. Proceed with these decisions; no more questions are needed.

1. Keep the recipient and parent pallet single. The store accepts the one root pallet by its unique identifier/SSCC; do not split child contents across stores. Include a store receipt only through the existing supported API/app and only if the runner can prove the root SSCC receipt safely. If not, leave receipt as an explicit follow-up; do not simulate it.
2. Yes: use the uniquely tagged isolated fixture pattern from `ni042` with native configuration boundaries and preflight. Do not seed shared physical stock directly. If the chosen warehouse or tag is not empty/unique, abort before writes. Save cleanup instructions and snapshots first.
3. Keep control, load and departure in the same runner if existing native harnesses permit. Include exact operation replay and invariant checks. Do not create a synthetic external ACK. If a required transport prerequisite is unavailable, stop at the last verified stage and report it rather than broadening the fixture.

For manual NET use existing `case_pick_execute`, matching `/weigh-line` and C0188. The immutable `RRL_STOCK_OPERATION` canonical metadata is the authoritative provenance; no new archive or DDL. The generic `/confirm` KG provenance gap is separate and root-owned; do not change it in C0190. Record that gap in RESULT. Root owns all live execution and cleanup.

The isolated API check proved the source endpoint exists on 8095; shared 8088 is stale. API_READY on a target runtime is still required before the runner starts. Claude may edit the accepted files now. Do not restart the shared API or run Oracle writes.

## REVIEW K-0217 — C0190 live safety and replay changes required before RELEASE

Root independently ran the new offline test file: 32 PASS; `py_compile` PASS. Do not execute the live runner yet. Three blockers from source review:

1. `cleanup()` currently counts every positive `RRL_REMAINS` row in the test warehouse to zero. Limit correction to the two exact lot UIDs in the saved fixture state, and abort before `INVENTORY_COUNT` if any other UID/article/reservation/task exists or if quantities differ from this run's expected remainder. A newly allocated warehouse is not enough protection against later use.
2. Direct native `post()` saves only operation ID and kind before calling `StockPosting`; it does not save the canonical command body or mark an unknown result. Persist exact serialized command/source/metadata before posting, retry those exact bytes and block any later stage after an unresolved result. In particular, cleanup must not re-read changed quantities and reuse the same operation ID with different content.
3. Each negative attachment currently accepts any HTTP 403/409. Assert the expected refusal code for stale version, foreign child scan and different cell, and check the parent composition after each refusal. Otherwise an unrelated denial can make the scenario look green.

Keep store receipt out of this runner unless the existing store API accepts the single root pallet identifier safely; the owner rule is one root pallet/one recipient, never split children across stores. Keep the rest of the run bounded to the verified tree; if transport stays unwired, report it explicitly. Please address these points in owned files and return RESULT/RELEASE before root runs any write.

Update RESULT_C0190 to account for Codex commit `62108b39`: new weighted-KG writes via general `/confirm` are refused; exact persisted legacy operation replays remain supported. Do not claim the general provenance gap remains for new public API writes.
