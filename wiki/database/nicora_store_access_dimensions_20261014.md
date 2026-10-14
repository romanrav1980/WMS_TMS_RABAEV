# Native store access: external vehicle dimensions

Installed by root 14.10.2026 in RABAEV/orcl; native scenarios and focused independent source review passed. [Bundle](../../db/migrations/2026-10-14_ni022_store_access_dimensions/README.md), [report](../../reports/nicora/2026-10-13/codex/STORE_ACCESS/REPORT.md).

Single RRL_STORE_ACCESS_RULES predicate shared by existing planning vehicle checks and final physical load/departure owners. Current store profile limits compare only READY external fleet dimensions; unknown/stale blocks final, draft reports missing data. NULL limit means no new restriction. CONFIG fence remains original stock/config owner, no additional resource ranks or shadow Python rules.

Final callsites are RRL_STOCK_HU_LOAD_CORE.begin_load and RRL_STOCK_TRIP_DEPART_CMD.execute_command, not only check_vehicle(p_complete). Store/time snapshot integration is separate V7 work. scripts/store_access_native_case.py passed on isolated retained TEST metadata, without changing stock. Full physical/pilot acceptance is separate.

## Applied native result

Root applied8 statements/errors0; actual PLAN_RULES/final shared predicate passed unknown/equality/exceed/stale/null scenarios on own TEST metadata. No physical shipment claimed. SQL lookup hints prepared after same-result readonly comparison131→10ms and58→8ms; final reapply coordinated with root. [Evidence](../../reports/nicora/2026-10-13/codex/STORE_ACCESS/native.json).

Final RELEASE: root reapplied helper with both measured lookup hints, Errors0/verify0. Installed source hash and all four changed package owners VALID confirmed; final readonly own fixture check PASS. Manifest: reports/nicora/2026-10-13/codex/STORE_ACCESS/installed_manifest.json. No pending code/apply in this block.
