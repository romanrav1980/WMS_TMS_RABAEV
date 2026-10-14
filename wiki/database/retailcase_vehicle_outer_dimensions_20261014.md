# Fleet profile: external overall vehicle dimensions

Installed by root 14.10.2026 in RABAEV/orcl; native version/replay/bounds cases passed. [Bundle and root instructions](../../db/migrations/2026-10-14_ni022_vehicle_outer_dimensions/README.md).

Existing RRL_VEHICLE_PROFILE_API/HIST now has a prepared additive contract for OUTER_HEIGHT_MM/OUTER_LENGTH_MM; cargo dimensions remain internal space and cannot prove road access clearance. Nullable legacy values are unknown, not zero or inferred measurements. Existing CONFIG/permission/version/replay/history remain authoritative. Omitted request preserves current external value, explicit null clears it. Existing UI labels the dimensions separately and retains the original durable request on connection loss.

Native transport/store admission and source hash integration is a subsequent root-owned change; saving this metadata alone does not enforce store limits. Native compilation and targeted fixture passed; see applied result below. API contract and UI fixture (no real writes) evidence: [report](../../reports/retailcase/2026-10-13/codex/VEHICLE_OUTER/REPORT.md).

## Applied result

Root applied bundle (Errors=0); native fixture10104 passed set/read/replay/conflict/stale/preserve/null-clear. Own TEST vehicle soft-deleted, immutable three-version history retained. PK read1.381ms, insert5.72ms; no new index. [Evidence](../../reports/retailcase/2026-10-13/codex/VEHICLE_OUTER/native.json). Native admission integration remains root-owned.
