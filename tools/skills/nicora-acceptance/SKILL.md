---
name: nicora-acceptance
description: Verify NICORA business scenarios through pytest, real Oracle/API and Playwright evidence. Use for isolated fixtures, quantity invariants, errors, concurrency and acceptance decisions.
---

# NICORA acceptance

Read wiki/index.md, the requirement/NSxx card, wiki/runbooks/evidence_driven_process_testing.md and wiki/runbooks/slow_sql_review.md. As independent reviewer derive expected results from requirements before examining implementation.

- Confirm fixture isolation before mutating tests: RABAEV connectivity is not isolation. Define ownership, cleanup and before/after quantities; preserve unrelated shared data.
- Reuse applicable pytest/SQL/Playwright runners. Doubles prove contracts, not Oracle commit, real ERP or physical device behavior.
- Check free/physical stock, soft/hard reserves and composition with lot/location rules. Parent/child scans must not double-count contents or physical load units.
- Select relevant denials, state errors, wrong SKU/location/load unit, duplicate key with changed payload, timeout after commit, worker crash and concurrent claims on one resource.
- ARM/TSD must match Oracle/API. Save stage screenshots and reports in runtime/test-evidence per runbook. Preserve failure evidence; never change business expectations to make tests green.
- Report skips, mocks, missing endpoints and hardware limits. Zero-INVALID gates remain unmet while the recorded baseline is unresolved; do not redefine acceptance silently.
- After meaningful cases/load/pilot rehearsal review longest SQL/SKV and record rewrite, bounded window, batching, cache, index/migration, statistics/plan check or owned backlog decision.
- Run scripts/check-encoding.ps1 for affected Russian text, focused diff hygiene and relevant regression. Repeat only after changes or unresolved failures.

Report requirements, data, code/environment, exact commands, measurements and limitations. Author checks, independent review and owner acceptance are different evidence.
