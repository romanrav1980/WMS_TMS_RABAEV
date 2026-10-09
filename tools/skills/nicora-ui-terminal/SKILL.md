---
name: nicora-ui-terminal
description: Build NICORA React and TypeScript ARM workstations and terminal PWA flows. Use for warehouse scanning, tasks, server-confirmed states and connection recovery.
---

# NICORA ARM and terminal

Read wiki/index.md, wiki/concepts/ui_interaction_rules.md, the relevant workplace/process requirement and NSxx card. Reuse existing admin React and terminal PWA projects after inspecting API contracts.

- Use config/project.defaults.json and support helpers. Prefer serv.bat, front.bat and terminal.bat locally; keep the configured admin port 3000 rather than adding 3001.
- Label pallet input Идентификатор паллеты; accept SSCC and permitted internal/legacy codes. Do not impose SSCC-only validation universally.
- Server rights, state and physical facts stay authoritative. Distinguish pending, confirmed and rejected scans; optimistic display does not prove completion.
- Reconcile/retry connection loss using operation correlation and approved command contracts. Do not replay stale stock decisions or fabricate offline completion.
- Preserve scanner focus; distinguish source, SKU, load unit, quantity and target. Derive duplicate/wrong-location/order/resource behavior from requirements.
- Follow project help/tooltip rules and visibly identify unavailable/future controls. Use tms-playwright DOM, console/network evidence and ARM/TSD screenshots.
- Validate full role scenarios against real API/Oracle states, reload and connection recovery. Build affected frontend and run focused UI/regression checks. Browser emulation does not prove actual scanners, scales, printers or cameras.
