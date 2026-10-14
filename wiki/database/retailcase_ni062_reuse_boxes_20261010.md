# NI06.2 — исправный возврат полной коробки в отбор,107
2026-10-10-107-return-full-good-box-reuse APPLIED RABAEV/orcl,17 statements/0 errors plus refinement12/0. REC/PUT/reuse helper/replenishment policy/guards VALID. Existing typed return receipt permits REUSE; optional separate blocked REUSE receiving zone; immutable RRL_RETURN_REUSE_PROOF source.

Приёмка REUSE требует approved COMPLETE_GOOD_BOX, фактическое подтверждение комплектности/исправности, ШК именно BOX, целое число коробок и exact current BOX→BASE quantity equal approved quantity. Original SAP verified supplier batch/expiry retained; legacy unverified batch не допускается в reusable stock. Current minimum shelf life checked before birth and placement. Required marking still refuses this ordinary slice, never omitted.

Товар сначала рождается в отдельной недоступной для отбора/пополнения зоне. Existing MANUAL/PUTAWAY task/Root transfer preserves UID/source/batch/quantity; target is current configured SKU PICK_CELL (fallback legacy article cell) in same warehouse, usable OTBOR. Shared RRL_STOCK_REPL_ADMISSION.lot_key/assert_target preserves original mixing policy. Different SKU forbidden, other batches only when explicit ALLOW_PICK_BATCH_MIX; current and planned target occupants considered. Temp/min shelf/mass tested against current rules. Positive height/published slots still require later exact physical proofs; alternate picking address needs existing slotting configuration, not arbitrary scan override.

API existing receive adds optional full_box_count/complete_good_boxes, defaults excluded for earlier replay. New warehouse reuse-zone config uses original version/config fence. Existing warehouse ARM adds controls/BOX confirmation; placement queue shows current picking target.

## Actual author evidence
No eligible SAP-origin BOX source existed after earlier dev cleanup. [Fresh source fixture](../../scripts/ni062_reuse_source_case.py)/[original continuation](../../scripts/ni062_reuse_source_continue.py) used assumed ARTMAS10 and warehouse supply XML through existing import, ordinary BOX24, actual SAP receipt and existing putaway, existing whole picking/ST/nested load/departure/store acceptance24. Source tag cdbf4c0962, article REUSE.QA:cdbf4c0962, original SSCC300000034518661218, warehouse13583852. Actual source traces retained; hardware/SAP external ACK not claimed.

[Return case](../../scripts/ni062_reuse_boxes_case.py) PASS, tag e6c16d0bbd: approval24, assumed SAP return, current dedicated driver pickup, wrong box_count2 refused, actual blocked P24/H0 + immutable proof1x24/batch, existing putaway to QIPcdbf4c0962, physical P24/H0 and eligibility reason null, exact receive/task replay and one placement. Returned own stock24 retained for subsequent functional work, driver retired/binding inactive.

Actual flow uncovered existing SAP JSON native-list decoding and reserved :raw bind bugs; fixed existing integration rather than new importer, continued original source. [[incidents/oracle_native_json_sap_20261010]].

Slow proof SQL36.482/32.593/30.188ms. Retain PK and bounded warehouse queues100/planned occupants200, existing target/source-cell indexes. NI06.2 owner checks real occupied-cell plan at growing volume. Independent acceptance/mixed batch/marked/multi-place/final supplier transfer and disposal remain open.
