# C0194 — strategic analysis: physical pallet type for a root HU

No code, no tests, no Oracle/API writes, no edits outside the report.

The live mixed root HU cannot use the current pallet-floor endpoint: it supports only a `HU_KIND=STOCK` carrier with own `RRL_REMAINS`; the root is a `CONTAINER` holding CASE children. Analyze the existing Oracle/API contracts and propose the smallest supported design that lets a warehouse operator confirm the physical pallet type for one root HU before QC/load.

Required report: `reports/tradecase/2026-10-28/claude/C0194/root_hu_floor_design.md`.

Address source of warehouse/cell, root version and scan checks, idempotency, how the type is stored, how loading reads it, refusal conditions, compatibility, and which existing packages/routes can be extended. Do not claim implementation or acceptance.
