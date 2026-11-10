# C-0184 — T10: read-only resource Gantt load and SQL latency profile

Owner has asked to finish the remaining sprint work and explicitly allowed additional Claude Code tasks. C0183 is released. Register and acknowledge this independent, read-only T10 workload check. Do not restart API 8088/8093, write Oracle data, or alter shared `dist`.

Use the already running API 8093 and the two QA warehouses from C0181 (220793322 and 226192056). Read the current timeline route contract and authorization first. Profile bounded windows only (up to 6 hours), with sequential baseline and concurrency 4; maximum 3 rounds per warehouse. Keep the request count under 30 total. Use only GET calls and current read permissions. If an identity lacks access, record 403 and stop that warehouse; do not bypass permissions.

Capture status, response time, payload size, event/resource/assignment counts, and current API slow-SQL entries attributable to the run. Do not claim Oracle SQL attribution unless the log identifies it. Compare serial and concurrent results for equality of event/assignment IDs. If the route or environment cannot be safely queried, stop and report the exact blocker without changing data.

Do not make code changes unless the measurements establish a concrete, independently reproducible UI/API bottleneck and a narrow safe fix. If no such fix is justified, provide a short result with a decision (fix now / bounded query / index evidence needed / backlog with owner). Clearly mark REACHTRUCK/OTHER and nonadmin coverage as unavailable if the sources/identity are absent.

Allowed files: `reports/tradecase/2026-10-27/claude/C0184/**`, `coordination/retailcase-claude/RESULT_C0184.md`, and the registered bounded diagnostic script. No wiki edits, backend/SQL/Oracle writes, API restarts, credentials in files, GitHub push, or changes to other people's work. Save RESULT and RELEASE; include a final status of API processes and confirm zero writes.
