# Weekly destination windows in native route planning

Installed by root 2026-10-14 in RABAEV/orcl. OracleApply: 17 statements, Errors=0; compilation and 10 native resolver cases passed. Full route/hash scenario is in progress. Migration ID `2026-10-14-ni081-store-weekly-windows`.

[Bundle and behavior](../../db/migrations/2026-10-14_ni081_store_weekly_windows/README.md), [handoff report](../../reports/nicora/2026-10-13/codex/STORE_WEEKLY/REPORT.md).

Authoritative implementation: new read-only `RRL_STORE_WINDOW_RULES`, used by the existing `RRL_TT_ROUTE_SCHEDULE`; TIME_API source contract V7 includes store/fleet configuration. No stock writer, new commit, Python scheduling policy or independent approval path. CONFIG lock and exact replay remain owned by existing TIME_API.

Complete ST windows take precedence; missing both endpoints uses weekly defaults; partial/reversed intervals refuse. Intervals intersect across members and retain breaks. Weekly unloading must fit one interval. Missing day is STORE_CLOSED; same arrival-local service day is the explicit horizon, no silent overnight move. DST gaps/folds refuse ambiguous local times.

Fresh RABAEV/orcl sources checkpointed; source drift preflight and read-only Oracle timezone probes passed. Package compilation/native cases/final approval/slow SQL remain for root after dependent store/fleet migrations. This page records preparation, not live enforcement.

Root application used the saved fresh checkpoint and a successful source-drift preflight. Editable profile/fleet dependencies were installed first. This establishes native compilation/resolver behavior; it does not claim industrial acceptance.
