# C-0188 · T06 manual NET CASE measurement

Registered C0188 in `coordination/tradecase-20261019/claude-budget.json` before delivery. Owner requests closure of all sprints; this is one bounded independent task. Read `TASK_C0188_T06_MANUAL_NET_CASE.md`. First ACK with the existing native-authority finding and exact owned files; wait for Codex review before editing. Preserve the electronic capture route. If there is no existing authoritative native path, report the exact native contract gap and stop before inventing or applying DDL. Do not restart APIs, write Oracle or publish to GitHub.

## REVIEW K-0211 — proceed, with these decisions

- Use `case_pick_execute`, matching the existing CASE line action. Do not require `case_pick_manage` for a picker entering their own measured fact.
- The existing immutable/idempotent `CASE_PICK_CONFIRM` operation record is sufficient; no separate measurement archive or DDL. Save the entered NET value, `KG`, and explicit `MANUAL_OPERATOR_ENTRY` provenance in canonical operation metadata. The server derives cumulative `fact_qty` from the current line quantity plus this NET value; never accept a client cumulative fact.
- Do not require a free-text reason. Do not categorically reject marking-required products; preserve existing marking scans and native rules where applicable.
- Keep electronic capture contract and generic legacy confirmation behavior unchanged. Make this explicit manual route usable only for a genuine KG NET line, after a fresh server-side read and normal actor/task/line checks. Don't invent scale precision: follow the current configured quantity precision and reject non-finite/non-positive input.
- Add route/contract tests for exact repeat, changed payload/actor/task/line conflict, another-line/missing-source denial and no second stock effect. Preserve unknown-outcome same-operation retry. Report whether the generic legacy confirmation path still admits the same product without provenance; do not silently expand this task to rewrite it.

Proceed with the owned Python/tests now; stop if the observed native behavior contradicts the ACK.
