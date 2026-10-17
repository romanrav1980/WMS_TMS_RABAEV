# Joint CASE / scale / time SQL review: 2026-10-15

Root completed the positive CASE1139 software TEST lifecycle and canonical compensation. A separate bounded collector then used a read-only Oracle transaction; it executed no API calls, business writes or DDL. [Raw observations](../../reports/retailcase/2026-10-15/joint-sql-review.json), [explicit decisions and evidence hashes](../../reports/retailcase/2026-10-15/joint-sql-review-decisions.json), [positive lifecycle journal](../../reports/retailcase/2026-10-15/n1939-positive-close/journal.json).

The63 API records69200-69262 have maximum observed335ms (actual TEST EMPTY capture). The51 locally correlated HTTP records include actual-time UI/read/retry calls; correlation uses explicit request_id, never wall-clock inference. The matching API slow-log entry is the original zero rejection58ms. No observed HTTP endpoint above500ms justifies an index/cache change in this sample; keep current scoped, bounded reads.

Relevant native V$SQL cursors show cumulative averages up to362.834ms for prepare and324.761ms for execute (two executions each). These are shared-cursor totals, not per-scenario timings, p95, worst cases or nested-statement completeness. Retain the existing native stock owner; reprofile using execution deltas under pilot concurrency for repeated500ms or any1000ms observation.

Two explicit follow-ups remain:

- Operations/schema verification owns the existing catalog backlog: named/batched dictionary reads and dictionary execution-plan/statistics investigation. Current retained slow rows include USER_CONSTRAINTS5911ms and RRL_WARES constraints1254ms. These are schema diagnostics, not picking latency; do not add stock indexes or weaken exact guards.
- Inventory replenishment continuation owns unpaired BACKGROUND transaction4867 at845ms. Its source already limits warehouse/status and200 pending rows. Preserve the bound; before pilot, instrument nested SQL/lock timing and examine the real plan if above500ms repeats or1000ms occurs. The record has no API identity, so it cannot be attributed to the GROUP proof or a particular HTTP request.

Direct CASE metadata close is separately logged BACKGROUND50ms with API_CALL_ID NULL. Its native success and physical compensation are in the positive journal; this collector does not invent an HTTP CLOSE call. Legacy Oracle wall timestamps differ from local UTC and remain unconverted. Bounds: latest501 slow-log rows,40 relevant cumulative native cursors, API IDs and local tail8MiB/max12000 lines. This is diagnostic review, not load or physical scale acceptance.

## Shift UI current-native follow-up

[Recorded21 HTTP rows and three slow entries](../../reports/retailcase/2026-10-15/shift-native-production-final/sql-review.json)
include the first interrupted proxy attempt and the completed second production
UI run. First attempt CASE tasks1469ms/navigation1244ms/waves1127ms/sessions1106ms;
second attempt CASE659ms/navigation51ms/waves748/742ms/sessions395ms/overview823ms.
This comparison does not isolate cold-cache, pool wait or database CPU as cause.
Native slow log has CASE queue transaction1021ms, recovery SELECT750ms and
overview transaction775ms, not timings of every nested statement. No p95/load
conclusion or new index is justified.

Explicit remaining work before pilot:

- Inventory owner: bounded CASE queue and recovery query. Instrument native
  SQL/lock/connection timing under concurrent desk opening, compare actual plans
  and execution deltas; retain existing limits. Recovery needs warehouse/native
  actor scope BEFORE limit: current legacy API has neither actor nor warehouse
  in its read port. This is both a correctness gap for selected-warehouse UI and
  a reason to avoid global join work; no client-only filter or new all-rights.
- Resources/fulfillment owner: overview batching stays50/concurrency2. Profile
  its four current readiness sources on the recorded single-wave case and
  pilot-sized batches; resolve repeated>500ms source work before load acceptance.
- Platform/access owner: measure navigation source/pool startup separately;
 1244→51ms does not establish an expensive persistent SQL plan. Keep the
  existing dictionary diagnostic backlog and exact-name release checks.

Read-only resource GET alone was379/75ms; production desk timeline409/637ms.
End-to-end page concurrency remains an acceptance condition, not solved by
passing isolated endpoint reads. Owners above are module responsibilities;
Codex owns backend continuation, Claude owns consumer UI after contract READY.
