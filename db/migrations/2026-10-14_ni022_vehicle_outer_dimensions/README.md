# Vehicle outer dimensions — APPLIED by root

Migration ID: 2026-10-14-ni022-vehicle-outer-dimensions.

Adds nullable OUTER_HEIGHT_MM/OUTER_LENGTH_MM (positive integer mm, max1000000, >= corresponding cargo dimension when known) to existing immutable RRL_VEHICLE_PROFILE_HIST. Existing history remains null/unknown; no backfill or cargo inference. No new owner/table/rights. Configure optional omitted dimension preserves previous head value; explicit JSON null clears to unknown. Headversion, CONFIG lock, native permission, replay actor/body check and source hash remain existing. New configure result/describe profile expose both fields; original saved replay result is not rewritten. Existing cargo/thermal/floor contracts preserved.

## Root application

1. Check 000_checkpoint.json against current RRL_VEHICLE_PROFILE_API body; checkpoint captured fresh live RABAEV/orcl, INVALID baseline empty. If owner changed, regenerate/rebase this patch before apply.
2. API/UI code is prepared; coordinate migration before server restart/use of new fields. No source/time/admission rule changed in this bundle.
3. Run `python scripts/stock_posting_apply.py db/migrations/2026-10-14_ni022_vehicle_outer_dimensions/apply.sql` through existing OracleApply. Inspect Errors=0 and USER_ERRORS/INVALID. DDL is nontransactional: failure requires rollback/recompile, not an assumption that prior ALTER vanished.
4. Run prepared bounded `python scripts/vehicle_outer_native_case.py`: own TEST native vehicle/profile, set/read/exact replay/conflict/stale/omitted preserve/null clear/belowcargo refusal, setup committed separately; each native configure in a clean transaction; own vehicle soft-deleted and immutable history retained. Script requires installed columns and never applies schema.
5. Restart API via serv.bat when root coordinates, then check existing profile API/UI and native integration separately. One root quality/encoding gate; no duplicate broad run from this agent.

## Rollback

Apply rollback.sql restores the fresh previous package body and marks ledger ROLLED_BACK. It intentionally retains nullable columns/constraints and immutable history: no evidence deletion. Revert API/UI alongside rollback; old owner does not accept new input fields. Before rollback after later owner changes, rebase the checkpoint rather than overwrite unrelated newer implementation. SQL rollback was not executed because forward migration is intentionally not applied yet.

## Evidence before apply

API contract script passes omission versus explicitnull and strict positive integer checks. Browser fixture (not Oracle acceptance) passes separate labels and exact pending request replay after lost response; screenshot reports/retailcase/2026-10-13/codex/VEHICLE_OUTER/profile.png. Root applied migration with Errors=0. Native fixture10104 passed set/read/replay/conflict/stale/preserve/null clear and belowcargo rejection; see reports/retailcase/2026-10-13/codex/VEHICLE_OUTER/native.json. There are no new list queries/indexes; history lookup is existing PK(VEHICLE_ID,VERSION_NO). Measured native history insert5.72ms and PK outer read1.381ms; retain existing history PK, no new index needed.
