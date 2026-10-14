# Store external dimensions — prepared native integration

14.10.2026. Bundle db/migrations/2026-10-14_ni022_store_access_dimensions prepared, NOT APPLIED by delegated agent. Root checkpoint PLAN_RULES preserved; fresh HU_LOAD_CORE/TRIP_DEPART_CMD bodies captured with SHA manifest. No new tables/rights or Python rule implementation.

RRL_STORE_ACCESS_RULES single read-only predicate uses store MAX_VEHICLE_OUTER_HEIGHT_MM/LENGTH_MM and current READY fleet.outer_height_mm/outer_length_mm. No cargo substitution. NULL store limit=no restriction; unknown/stale fleet for configured limit=draft warning/final refusal. Known exceedance rejects even draft; equality allowed. Inputs bound200, relevant destination set bound200, reads existing indexed keys; SQL latency pending actual apply/case.

Callsites verified against live USER_SOURCE: TRANSPORT_EDIT_API, TRANSPORT_PLAN_API prepare and TT_OPERATION_PLAN_API call check_vehicle(...,0); assignment/plan apply call(...,1). Modified check_vehicle returns store_access and warning/completeness. Actual physical owners separately enforce assert_members with CONFIG4: HU_LOAD_CORE.begin_load after current thermal check, before load effects; TRIP_DEPART_CMD.execute_command after current thermal check, before departure effects. Thus draft flags cannot bypass final current configuration. Native stock command journal/replay unchanged.

TIME_API/ROUTE_SCHEDULE unchanged; store_schedule owns V7 fleet+store source hash. Prepared scripts/store_access_native_case.py exercises actual planning rules and same final predicate on own metadata, including unknown/equal/exceed/stale/null. Setup commits separately from each existing owner command. Cleanup soft-deletes own fleet, marks own planning ST condition2, clears store limits through StoreProfile owner; immutable histories retained. No stock or actual physical shipment fixture claimed. Script must run only after root applies package bundle.

Root owns apply/verify, common gate and wiki index/log. Rollback restores three exact owners then drops helper. Native compile/behavior must not be claimed until actual application and case result.

## Root application and real native acceptance

Root applied8 statements Errors0. [native.json](native.json): own vehicle10105, store ACCESS.QA:25dea69e1e, ST641517. Actual native PLAN_RULES and final shared assert_members: empty draft/NULL deleted flag, unknown/stale warning versus refusal, equality, height and length exceedance, NULL limits all PASS. Cleanup through owners: own fleet soft-deleted, planning ST condition2, store limits cleared; immutable metadata histories retained. No stock/load/shipment was performed. Final load/depart callsites verified by bundle verify, so this is native predicate acceptance, not a claim of a new physical shipment.

SQL evidence identified unnecessary work in JSON_TABLE-driven lookups: ST95.628ms average/5312buffers per call; memberexist47.604ms/1135buffers. Readonly comparison using same keys and identical result: ST131.187→9.712ms, memberexist57.523→7.758ms with leading(inputs)/use_nl(p)/index(p). No new index. Existing ST_PAGE_KEYS and native ID index used as available candidates; DBMS_XPLAN access unavailable (no SELECT on V$SQL_PLAN), so actual plan is not claimed. [Comparison](lookup_comparison.json).

Only these two query hints added to001_access_helper after functional PASS; final helper reapply/compile coordinated with root. No need to repeat broad fixture or other subsystems. Other helper SQL: destinationrule18.383ms, member-address1.822ms. Decision implemented: bounded input drives existing indexes; no speculative DDL/cache.

Final RELEASE: root reapplied helper with both measured lookup hints, Errors0/verify0. Installed source hash and all four changed package owners VALID confirmed; final readonly own fixture check PASS. Manifest: reports/retailcase/2026-10-13/codex/STORE_ACCESS/installed_manifest.json. No pending code/apply in this block.
