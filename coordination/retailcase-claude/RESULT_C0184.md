# C-0184 — T10: read-only load profile of the resource Gantt

## Contract and access
- `GET /api/resources/timeline?warehouse_id&start_at&finish_at` (`modules/resources/api/timeline_routes.py`): an aware window of ≤7 days, otherwise 422.
- Access: `RRL_ACCESS_API.allowed(actor,'resource_gantt_view','WAREHOUSE',ware)`, plus a per-source right (registry → resource_management_view, attendance → resource_shift_view, …). A source without the right is returned as FORBIDDEN, not as empty.
- Identity: admin (current rights, no bypass). All sources READY; there was no 403.

## Run
- Running API `127.0.0.1:8093`, window `2026-10-27T12:00Z–18:00Z` (6 h). Script `scripts/c0184_gantt_load.py`.
- Run 1: per warehouse 3 serial plus 1 round of 4 concurrent → `c0184-gantt-load.json`.
- Run 2 (`repeat`): 1 more concurrent round of 4 per warehouse, to check reproducibility → `c0184-gantt-load-repeat.json`.
- **Total 22 GETs** (cap 30), 2 rounds per warehouse (cap 3). All 200.

| Warehouse | Response | Serial ms (3) | Concurrent ×4, run 1 ms | Concurrent ×4, run 2 ms |
|---|---|---|---|---|
| 220793322 | 4570 B; resources 8 (CASE_PICKER 6, DOCK 2), events 3, assignments 3 | 984 (cold) / 169 / 210 | 222–314 | 1123–1207 |
| 226192056 | 1626 B; resources 1 (DOCK), events 0, assignments 0 | 119 / 119 / 133 | 865–1064 | 243–282 |

- **Equality:** the event_id and event>resource lists match in all 11 responses per warehouse (ids_hash 67bbe622… / a6830960…).
- **Slow SQL:** `RRL_SQL_SLOW_LOG` since the run started: 0 rows in both runs. No SQL attribution is claimed: the log points to no query.
- **API processes before = after:** 8088 PID 87992 (since 11:06:35), 8093 PID 24236 (since 17:05:40). Nothing was restarted.
- **Zero writes:** GET only; Oracle read only (`set transaction read only`). No fixtures created.

## Interpretation
- Serially, responses take 0.12–0.21 s; only the very first request was cold (0.98 s).
- In every run exactly one of the two concurrent bursts slowed to about 1 s for all 4 requests, and the other did not, regardless of warehouse and payload (1.6 KB and 4.6 KB). The slow log is empty.
- This points to a one-off cost when the first concurrent burst starts (likely opening extra connections or worker threads on the API side), not to SQL or data volume. The cause is not proven: there is no API-side pool metric.

## Decision
**Backlog with owner (Codex/API), no code fix now.** There is no reproducible bottleneck in the UI or in the query. The latency stays within ~1.2 s at concurrency 4. Data volume and SQL are not the cause, so there is no basis for a bounded query or an index.

To confirm, the API side would need the time to acquire a connection from the pool, and how many connections are open, at the start of a concurrent burst. If the pool's minimum size is below 4, raising it (or warming it up) is a decision for the API owner.

## Not covered
- REACHTRUCK and OTHER: absent from the source data of both warehouses (as in C0181).
- 226192056 had no events in the 6 h window (only its dock), so its load is minimal.
- Non-admin identity: none in the QA setup, so neither FORBIDDEN sources nor 403 were checked.
