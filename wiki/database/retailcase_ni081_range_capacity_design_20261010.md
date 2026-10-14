# NI08.1 / NS59 — проверка существующего диапазона,145

Inventory read model extends143 in the same READ ONLY transaction. Original pick faces, mappings and canonical RRL_STOCK_REPL_CAPACITY.remaining_base_quantity are authoritative for remaining volume capacity; no independent Python stock/arrival volume rule.

Read distinct published SKU cells, max100, expose actual configured volume/weight and canonical remaining BASE capacity. Missing/ambiguous capacity is a per-cell refusal, not zero capacity. Existing P/H, incoming active warehouse tasks and remaining CASE lines are withdrawal blockers. Occupied cell cannot be proposed for immediate withdrawal. No active tasks retargeted.

Calculation may compare nominal whole-pallet additional quantity with known volume capacity; volume sufficiency is not physical admission. Missing weight/geometry/temperature/routing/cost/approval remain explicit. Shared cell counted once; original IDs retained; no replacement slot table, no mutation or stock writer. Author case original135 cell508 already has P20/H20 and expected zero remaining volume, cannot withdraw. Full NS59 approval/drain remains next.
