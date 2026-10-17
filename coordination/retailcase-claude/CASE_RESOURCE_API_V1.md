# CASE resource metadata commands v1 — APPLIED, native/API PASS

Native kit APPLIED17/0; independent nine-source/schema/default/index/ledger/INVALID0 verified. Dedicated CASE1138 acceptance:12 native caller-rollback +10 actual HTTP +5 own-session guard groups PASS. QA actor/session55/BOOK/H1 remain active on root UI HOLD until18:30–18:45 release; UI C0113/hardware and cleanup remain separate. Owner: sprint_empty_trip resources CASE domain. Existing legacy claim/start APIs remain compatible; new strict route supports scoped roles.

POST /api/case-pick/tasks/{task_id}/resource-commands
Authenticated actor only; browser actor is forbidden extra field.
```json
{"operation_id":"terminal-durable-id","action":"CLAIM","expected_assignment_version":0,"resource_session_id":54,"resource_id":58,"equipment_id":null,"reason":"Take my assigned picking work"}
```
`action`: CLAIM|START. operation_id 1..100 ASCII identifiers; expected_assignment_version integer>=0; resource_session_id required positive; resource_id/equipment_id optional positive and must match actual session. reason 8..500 chars. Persist exact request before first send; retry immutable operation/body. No quantities.

GET /api/case-pick/tasks/{task_id}/resource-context
```json
{"task_id":1136,"warehouse_id":13583852,"status":"IN_PROGRESS","assignment_version":2,"content_version":2,"assigned_to":"WHREQ15.OP","resource_id":58,"resource_session_id":54,"equipment_id":null,"started_at_instant":"2026-10-15T12:00:00.000000+00:00","started_shift_time_zone":null,"current_actor":"WHREQ15.OP"}
```

Command response / GET /api/case-pick/resource-commands/{operation_id}
```json
{"operation_id":"terminal-durable-id","action":"CLAIM","task_id":1136,"warehouse_id":13583852,"actor":"WHREQ15.OP","assigned_to":"WHREQ15.OP","resource_id":58,"resource_session_id":54,"equipment_id":null,"status":"ASSIGNED","assignment_version":1,"content_version":2,"changed":true,"started_at_instant":null,"stock_posted":false}
```
Exact replay returns saved result after current authorization; new operation with no actual transition returns changed:false and emits no duplicated event. Versions derive from every actual assignment/resource/session/equipment/status/start mutation by all owners. Clients cannot set/rewind assignment_version directly. START immutable original server instant; unknown original shift zone remains null, do not invent zone.

Native-only CLAIM of unassigned work requires actual warehouse/group/network execute grant: SELF alone cannot claim it. Already assigned own work may use SELF. Native START requires currently assigned own work. Actual own ACTIVE qualified CASE_PICK physical session in actual CASE warehouse mandatory. First increment ordinary unmarked EA only, no active HU/ASM; no cross-actor transfer. Legacy manager behavior stays on existing branch/API. 403 current access denied; 409 stale version/physical resource/context conflict; 503 uncertain connection outcome requires exact retry/read receipt, not fresh ID.

Mounted public composition: resources.public.build_case_resource_service(gateway=None); resources.public.case_resource_router. New resources contracts_case_resource.py + api/case_resource_routes.py; metadata owner native RRL_CASE_ASSIGNMENT_API, append-only RRL_CASE_RESOURCE_COMMAND. Root public exports/main registration are loaded in the running API. Terminal may use existing known physical session identity; no global session enumeration is added.

## Frozen terminal receipt semantics

Server canonical request = every DTO field including `resource_id:null`/`equipment_id:null` defaults, keys sorted lexicographically, UTF-8 JSON without ASCII escaping or spaces. Persist the normalized full DTO. ACK `request_sha256` is uppercase SHA256 of those bytes. Validate operation/action/task/authenticated actor AND this digest before confirming any outcome. Native response is validated before metadata transaction commit; malformed/mismatched ACK is503 and keeps intent.

Successful response adds `outcome:"APPLIED"`, `request_sha256`, `outcome_confirmed:true`, `may_create_corrected_operation:false`, `error_code:null`. A recoverable domain refusal is committed as immutable `outcome:"REJECTED"`, same identity/hash, `outcome_confirmed:true`, `changed:false`, `stock_posted:false`, `may_create_corrected_operation:true`, `error_code:"CASE_SHIFT_UNAVAILABLE"` (example). POST returns409 with that ACK as the top-level body; GET receipt returns200 with the exact same saved object. Case status/content_version in REJECTED may be null if source state is unknown; never invent an applied state from it.

Only after validating that durable REJECTED ACK may UI clear this intent and let the user explicitly correct input/create a new operation. No automatic POST/new nonce. Late original request always replays REJECTED, even if qualification/session/policy is later corrected. Auth403/revoke, raw exception409, DB/transport503 and unknown failures are NOT definitive receipts: error detail has outcome_confirmed:false/read_before_retry:true; preserve original intent. Native whitelist catches exact known20886 domain reasons after all current auth and native fences; unknown/system exceptions never become REJECTED.

ASSIGNMENT_VERSION comes only from trigger old+1 on actual assignment/resource/session/equipment/status/start changes for all owners. Any direct explicit version SET/rewind is refused, including trusted metadata owner. One actual transition = one event; replay/no-op emits none. New ordinary-only eligibility is checked after current authorization + saved receipt lookup, so known receipts remain readable after workflow advancement while new unsupported actions still fail closed.

Native-only CLAIM/START cannot replace an existing non-null session/equipment binding even before first pick; use explicit transfer owner. Existing flat legacy route behavior remains unchanged. After a terminal receipt, refresh resource-context before creating any corrected intent. CASE event includes actual resolved resource/session/equipment; no warehouse CURRENT_TASK_ID is assigned from a CASE identifier.

Scoped CLAIM also requires an OPEN shift within its actual start/finish interval; old legacy planned CLAIM remains unchanged. Native INSERT normalizes NULL/zero assignment_version to zero for ROWTYPE compatibility, rejects nonzero; explicit UPDATE of version always fails.

## Own physical session choices (READY, root composition)

GET `/api/case-pick/tasks/{task_id}/resource-sessions` authenticates current identity, calls native task_context in the same READ ONLY transaction, selects ONLY own ACTIVE sessions in the actual CASE warehouse. Maximum20; excess is explicit409, not silent truncation. It invokes existing RRL_CASE_RESOURCE_POLICY.context_json per own session; no copied qualification/shift/business rule. Domain refusal appears on that own item as ready:false/reason; auth/unknown DB errors fail the whole read.

Response: `{task_id,warehouse_id,current_actor,action:"CLAIM"|"START",items:[{resource_session_id,resource_id,equipment_id,resource_code,ready,reason}],command_revalidates:true}`. Readiness is advisory: tare, trigger conditions and changed versions are still authoritative at command time. No arbitrary/global session list and no need for extra resource_session_view permission. Actual native plus HTTP own CRES15.OP/session55 PASS; native current role denial, foreign actor, PAUSED projection and revoked qualification caller-rollback evidence recorded separately.

Coverage: actual CLAIM/START HTTP paths prove WARE+SELF. GROUP/NETWORK/DC pure-read native admission PASS10 caller-rollback groups, including CURRENT member/parent removal, inactive/foreign/expired/revoked denial; metadata commits0. No CLAIM/START after dirty ACCESS TX, so GROUP/NETWORK/DC command execution/hardware is not claimed.
