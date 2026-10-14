# NI03.1 stock source eligibility — 2026-10-09-007

Target: existing RABAEV/orcl ACTIVE. Pure Oracle policy shared by preview, existing planners and locked execution.
Apply with scripts/stock_posting_apply.py .../apply.sql, then ledger.sql; verify.sql lists changed-object errors.
Source checkpoints were exported before replacements under checkpoint/. Rollback restores packages; restores original unit/promotion contracts from 220/219 checkpoints; keeps additive SOURCE_PICK_MODE data. Application rollback must restore the corresponding source revision. Rollback was prepared, not executed.

Column SOURCE_PICK_MODE belongs to existing warehouse SKU rule: AFTER_PUTAWAY default, DIRECT explicit PICK/ALLOCATE from receiving. Cell blocks still prohibit use. No stock/history reset.
Current runtime manifest includes schema startup before contracts and the current policy/component source.

Real dev case: scripts/ni031_eligibility_cases.py; uses tagged QA metadata and root commands. No production/SAP/state service calls.
Details and limits: wiki/database/nicora_ni031_stock_eligibility_20261009.md.
