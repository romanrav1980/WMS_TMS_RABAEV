# Assembly Scale API v1 — UI contract (15.10.2026)

Backend owner Codex assembly agent; frontend owner Claude via root. Implemented names are `state`, not `status`, for session/step. Prefix `/api/inventory/assembly-scale`. Strict input DTO: `api/wms_api_server/app/modules/inventory/contracts_assembly_scale.py`. No browser mass input; gateway alone submits samples.

## Read and restore

`GET /context?task_id=<assigned CASE id>`:

```json
{
  "task_id": 1124,
  "task_state": "IN_PROGRESS",
  "content_version": 1,
  "scan_container": "physical identifier from server",
  "warehouse_id": 1,
  "lines": [{"case_line_id": 10,"article": "SKU","name": "Product","remaining_quantity": "2","base_uom": "EA","policy_state": "CONFIGURED"}],
  "stations": [{"device_id": "registered-device","post_cell": "post","confirmation_mode": "AUTO","device_mode": "TEST","device_policy_version": 1,"calibration_ref": "configured-ref","tare_captures": [{"capture_key": "64 uppercase hex","weight_kg": "0.5","measured_at": "UTC ISO timestamp"}]}],
  "active_session": null
}
```

Values above demonstrate shape only, never demo data for the live screen. `policy_state` CONFIGURED/UNCONFIGURED means explicit ordinary unmarked EA mass policy. Missing policy disables start, never estimates from order mass. `active_session` contains the same object returned by GET session below. Restore it before allowing a new session/step. Task list uses existing own CASE queue; opening an arbitrary or unassigned task is denied.

`GET /sessions/{session_id}` returns:

- session_id, task_id, device_id, post_cell, operator_id, warehouse_id, scan_container;
- state OPEN/BLOCKED/FINALIZED; confirmation_mode AUTO/BUTTON; content_version;
- tare_capture_key, tare_weight_kg, last_weight_kg, expires_at, block_reason;
- steps: latest <=50 step objects, including the active step. No next step while a previous step is unresolved.

`GET /steps/{step_id}` and `steps[]`:

- step_id, session_id, operation_id, sequence, case_line_id, article, quantity;
- state WAITING_BEFORE/ARMED/READY/APPLIED/DISCREPANCY;
- confirmation_mode, content_version, before_capture_id, after_capture_id;
- before_weight_kg, after_weight_kg, delta_kg (null until measured);
- min_delta_kg, expected_delta_min_kg, expected_delta_max_kg;
- consent_to_auto, button_intent, block_reason, stock_posted.

APPLIED comes only from native stock-transaction claim. READY is archived/admitted evidence, not a stock effect. On timeout retain the same step_id/operation_id and read status; never allocate a replacement. Dates shown briefly in local UI, timezone technical details in diagnostics.

## Operator commands

`POST /sessions`: session_id, task_id, device_id, expected_content_version, tare_capture_key, scan_container. Requires assigned operator and a fresh actual EMPTY_TARE archive for the same CASE/device. Id is generated and persisted before sending; exact retry reuses it.

`POST /sessions/{session_id}/steps`: step_id, operation_id, case_line_id, quantity (positive integer string), scan_source_cell, scan_product, scan_container, expected_content_version, consent_to_auto (default false). Physically scan identifiers. AUTO mode requires an explicit consent explaining this exact article/quantity will be posted after stable delta; no checked-by-default consent. Mode comes from station policy and cannot be switched mid-step.

`POST /steps/{step_id}/placed`: no mass/quantity/actor body. BUTTON intent may be recorded at ARMED before the after window or at READY; server posts only once the stable window and native admission exist. AUTO requires no second click after Stable.

`POST /sessions/{session_id}/finish`: final_capture_key. This must be a separate current FINAL_GROSS for the same CASE/tare/current content; does not copy W_after or bypass existing independent QC. Without actual final capture show the pending requirement.

Mutation responses include the current session/step state. Dedicated gateway AFTER may return an archive plus `step` and `posting`. UI polls GET session/step, not an unscoped gateway request list. HTTP503 retains archived evidence and reports outcome_confirmed=false/read_before_retry=true/operation_id; this is “Восстановление связи”, never success.

## Gateway (not operator UI)

GET `/gateway/requests?device_id=` returns max1 item: session_id, step_id, capture_id, phase BEFORE/AFTER, device_id, device_policy_version, calibration_ref, confirmation_mode, expected_before_kg, min_delta_kg, expected_content_version, expires_at, case_task_id, scan_container. BEFORE for WAITING_BEFORE; AFTER for ARMED AUTO or BUTTON intent. Source capture IDs are preallocated by native step, not regenerated per poll.

POST `/captures`: exact AssemblyCapture DTO. Sender and business operator differ. The backend derives business actor only from persisted consent/current assigned operator, then uses a clean transaction of existing CASE_PICK_CONFIRM. Terminal never submits actor or numeric mass. Physical waiting is outside database transactions.

## UI sequence

Task → station and actual tare → physical scans/article/quantity + explicit AUTO consent if configured → “Подготовка весов” (WAITING_BEFORE) → “Положите товар” (ARMED) → “Проверяем вес” (READY transient) → “Укладка подтверждена” (APPLIED). BUTTON has “Положил” at ARMED. DISCREPANCY/BLOCKED blocks next placement and shows native reason; no silent reset/tare/reduction. Finish requires new final measurement, then existing QC.

Every control has title/help mapping. Device ids, raw NodeIds, certificates, policy versions and clock diagnostics belong in help/diagnostics; primary screen shows post/product/task and action.

Station policy requires explicit `cumulative_tolerance_kg` decimal string (no default/percent). Session freezes this value and returns it. Final reconciliation additionally requires `abs(final_gross − initial_tare − sum(APPLIED step.delta_kg)) <= cumulative_tolerance_kg`; failure requires reconciliation. Session `steps` contains latest50 and `has_older` explicitly reports older history.

## Recovery v1 (forward increment, not yet applied)

Operator first requests HOLD and waits for REQUESTED acknowledgement. Only after that remove unaccepted goods. Never auto-tare or remove previously accepted goods.
POST `/sessions/{sid}/reconciliations`: `{operation_id,step_id,expected_content_version,reason}`.
Response `{reconciliation_id:operation_id,session_id,step_id,state:"REQUESTED",requester_id,controller_id:null,expected_weight_kg,expected_content_version}`.
POST `/reconciliations/{id}/authorize`: `{operation_id,reason,unaccepted_goods_removed:true}`; controller confirms removal only after HOLD ACK. Distinct current controller with case_pick_manage required, even GLOBAL_ADMIN cannot self-authorize. Response same identity/state AUTHORIZED/controller_id. GET `/reconciliations/{id}` returns current state.

Only AUTHORIZED queues a measurement. Gateway request retains same fields and adds phase RECONCILE + reconciliation_id; actual initial tare_capture_key is preserved. Separate `AssemblyReconciliationCapture` DTO adds phase RECONCILE/reconciliation_id with unchanged other series fields; existing BEFORE/AFTER DTO/canonical bytes unchanged.
POST `/captures` response `{archive,step,session,posting:null}`. Immutable archive ACK includes all original capture identity/hash/weight/time/devicepolicy/calibration/stock_posted:false fields plus phase RECONCILE, reconciliation_id, state COMPLETED|DISCREPANCY. Native compares stable observed GROSS to last accepted weight within device resolution. Matching observation cancels only the unposted step (state CANCELLED), reopens session, preserves all evidence/sequence/current content and last accepted weight. Mismatch preserves evidence and leaves blocked; operator must create new intent/controller authorization.

No recovery may cancel canonical APPLIED/IN_FLIGHT operation or STEP_USE. Expired session, changed policies/calibration/source or revoked actors require separate handover; recovery never extends TTL or invents recent zero. Raw archive is a separate WAREHOUSE_ASSEMBLY_RECON protocol1.2, leaving old1.1 bytes unchanged.

Request immediately holds session BLOCKED under original stock OP fence. Session read includes `reconciliation` (latest intent object or null), including REQUESTED/AUTHORIZED/COMPLETED/DISCREPANCY after reload.

Recovery journal/read and archive ACK also include actual `case_task_id` (integer). New conflicting pending intent returns ASSEMBLY_RECOVERY_ACTIVE_INTENT_CONFLICT409; use same existing operation/body after uncertainty. Recovery validates unchanged current active SKU policy version as well as station/device policy.
