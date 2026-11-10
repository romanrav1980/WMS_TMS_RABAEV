# API_READY_C0180 — T10 gate status

Backend and migration are available for Claude's live UI acceptance.

- Codex's local API is available on `127.0.0.1:8093`, using the current working tree and live Oracle. It is a temporary local process; do not stop or restart it. If it is unavailable, message Codex.
- Use the existing local authenticated QA session/configuration; credentials are intentionally not copied into coordination files.
- QA warehouse: `226192056` (`TRADECASE QA f7123876`); dock: `TR27D226192056`.
- Live acceptance evidence: `runtime/test-evidence/tradecase/2026-10-27/C0180-live-api.json`.
- Verified with real HTTP/API and Oracle: GET=200; BLOCK=200; exact BLOCK retry returns identical receipt; same operation ID with modified reason=409; GET reflects blocked; UNBLOCK=200; exact UNBLOCK retry returns identical receipt; GET reflects open; final Oracle `DOCK_IS_BLOCKED=0`.
- Oracle migration `2026-10-27-yard-dock-status` is applied. `verify.sql` passed; all current objects VALID and `USER_ERRORS` empty.
- Refusal codes: `YARD_DOCK_NOT_FOUND`, `YARD_DOCK_AMBIGUOUS`, `YARD_DOCK_STATUS_INVALID`, `YARD_ACCESS_DENIED`, `YARD_OPERATION_CONFLICT`; an unknown outcome retains the original operation ID/body for exact retry.
- Blocking changes only future dock assignments/plans. It does not cancel a current visit, plan, load, or shipment.

Run the UI checks requested in `TASK_C0180_T10_DOCK_STATUS_UI.md` at 1440/390 px with the real API, then publish `RESULT_C0180.md` and RELEASE through the file channel. Do not modify backend/SQL or shared `dist`; no GitHub push. Leave the test dock open after any live command.
