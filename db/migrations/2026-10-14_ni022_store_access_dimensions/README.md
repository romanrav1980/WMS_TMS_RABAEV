# Store access / external vehicle dimensions — applied by root; lookup hint follow-up

Prerequisites: ni051_store_profile and ni022_vehicle_outer_dimensions installed. No tables/columns/rights added here. Fresh checkpoints for PLAN_RULES (root) and final HU_LOAD_CORE/TRIP_DEPART_CMD (agent), SHA manifest attached.

One read-only helper RRL_STORE_ACCESS_RULES checks only configured store outer limits against current READY fleet profile.outer_height_mm/outer_length_mm. NULL store limit has no effect; unknown/stale required dimension yields draft incomplete/warning, final refusal. A known exceeded limit rejects even draft; equality passes. Cargo dimensions are never substituted. Native IDs/ST lists max200, relevant addresses bounded200; helper reads by existing store/address and vehicle-version keys.

PLAN_RULES.check_vehicle delegates and adds store_access material/warning. Existing manual/edit/operation planning p_complete0 remains draft. Existing assigned/apply p_complete1 refuses unknown. Actual physical load uses HU_LOAD_CORE.begin_load, departure uses TRIP_DEPART_CMD.execute_command: both call assert_members unconditionally after existing thermal current check and before effects, so p_complete0 cannot bypass them. assert_members requires existing CONFIG shared lock(mode4); CONFIG writers use6, including absent profile creation. No new lock rank or network work added.

Root apply: compare checkpoints with current owner bodies, then `python scripts/stock_posting_apply.py db/migrations/2026-10-14_ni022_store_access_dimensions/apply.sql`; inspect Errors0/USER_ERRORS/INVALID, run targeted native script once prepared. Rollback restores three bodies then drops helper, preserves all metadata/history. No TIME_API/ROUTE_SCHEDULE or source-hash code touched; store_schedule owns V7 current fleet/store hash integration.

Native compilation/scenario/latency pending root apply; not claimed from source alone. No speculative index. After native case inspect helper SQL and retain/bound/index only on observed evidence. Common gate/index/log owned by root.

Root initialapply8/errors0 and native functional case PASS. Two bounded lookup hints added after measured same-result reduction131→10ms and58→8ms; reapply001helper+verify coordinated with root. See reports/nicora/2026-10-13/codex/STORE_ACCESS.

Final RELEASE: root reapplied helper with both measured lookup hints, Errors0/verify0. Installed source hash and all four changed package owners VALID confirmed; final readonly own fixture check PASS. Manifest: reports/nicora/2026-10-13/codex/STORE_ACCESS/installed_manifest.json. No pending code/apply in this block.
