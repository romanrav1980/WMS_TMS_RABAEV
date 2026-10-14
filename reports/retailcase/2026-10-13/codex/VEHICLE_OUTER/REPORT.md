# Fleet outer dimensions — prepared RELEASE

14.10.2026. Runtime API/UI and migration bundle prepared; Oracle NOT APPLIED by this agent.

[Bundle](../../../../../db/migrations/2026-10-14_ni022_vehicle_outer_dimensions/README.md) (repository path: db/migrations/2026-10-14_ni022_vehicle_outer_dimensions). Fresh body checkpoint and invalid baseline captured. Nullable integer outer height/length in existing history; preserved CONFIG/version/replay; omitted preserves, null clears, unknown not inferred from cargo. Native helper prevents external dimension smaller than internal cargo dimension. Old historic results not rewritten.

API strict integer/range/null-versus-absent: scripts/vehicle_outer_contract_case.py PASS. Existing React UI adds separate external labels and immutable pending body fields. Browser fixture with simulated lost response: two exact same requests, same operation and outer values; PASS. [Screenshot](profile.png) viewed; [browser evidence](browser.json) explicitly fixture, no live Oracle mutation.

Native acceptance script scripts/vehicle_outer_native_case.py prepared, not run before apply. Root must apply/compile/verify and execute the bounded rollback fixture, then coordinate API restart and common gate. No new unbounded query or index; native performance decision follows actual case. Root owns index/log updates and later store-access/time integration. No commit/push.

## Applied native acceptance — final RELEASE

Root applied bundle with OracleApply Errors=0. Initial acceptance script incorrectly created the fixture and called configure inside one dirty transaction; existing CONFIG correctly refused DIRTY_TRANSACTION and root rolled it back. Runtime was not changed for the test.

Corrected script commits only its TEST vehicle setup, then performs each configure in a separate clean transaction. Native fixture vehicle10104 / OUTERd18a63335a: set/read, exact replay, changed-body conflict, stale-version conflict, omitted preserve, explicitnull clear one dimension, smaller-than-cargo refusal all PASS. Three immutable versions retained. Cleanup through existing RRL_TR_VEHICLE_DEL under CONFIG soft-deleted only this own vehicle. No physical vehicle, stock or shipment affected; history was not forged/deleted. [Native evidence](native.json).

Total scenario320.8ms. New native history INSERT5.72ms average/3 executions; exact PK outer read1.381ms/3. Decision: retain existing history PK(VEHICLE_ID,VERSION_NO), no extra index/cache/broad test. Final status supersedes prepared-only statements above. Only testscript/reports updated in this step; API/native/UI unchanged.
