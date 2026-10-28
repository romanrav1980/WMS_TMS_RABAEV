# C-0191 — T06/T07: transport and store receipt of the mixed pallet (C0190 adapter)

## Files
- `scripts/c0191_mixed_tree_transport.py`: the adapter. On import it does no live work; it only loads the pure C0190 helpers. Entry point: `run(live, inputs)` after the C0190 TREE stage, using the C0190 `Live` object (state, journal, send/post/read/one/meta/composition/replay_equal).
- `tests/tradecase/test_c0191_mixed_tree_transport.py`: 25 offline tests.
- C0190 (Codex-owned) is not changed.

## Input contract (`validate_inputs`, listed in INPUT_REQUIRED:*)
| Field | Meaning | Nature |
|---|---|---|
| `store_address` | the one recipient (ST address and store receipt) | synthetic fixture |
| `vehicle_number`, `dock`, `driver_name` | trip master data | synthetic fixture |
| `shipment_date` | trip date YYYY-MM-DD | synthetic fixture |
| `pallet_type_id` | physical floor type of the root pallet and its tare | directory |
| `root_measurements{origin,gross_weight_kg,width_m,depth_m,height_m}` | measurements of the root at loading | `origin`: `SYNTHETIC_FIXTURE` or `OPERATOR_MEASURED`, explicitly |
| `qc{mode:SCAN\|WEIGHT[,gross_weight,wood_weight,origin]}` | outgoing quality of the ST | WEIGHT values with an explicit origin |
| `vehicle_geometry{cargo_*_mm,outer_*_mm,max_places}` | vehicle profile | synthetic fixture |
| `store_policy_expected_version` | current version of the store PAPER_COUNT policy | directory |
| `paper_reference` | paper receipt document | synthetic fixture |

A resumed run with different inputs → `TRANSPORT_INPUTS_CHANGED_AFTER_START`. All evidence/measurement/paper references are built by `evidence()`: `SYNTHETIC_FIXTURE_NOT_PHYSICAL:<what>:<tag>` or `OPERATOR_MEASURED:…`. Fixture values are not presented as physical measurements or external ACKs.

## Stages (every write goes through the C0190 journal: stored before sending, identical repeat, unknown outcome blocks the rest)
1. **SHIPMENT:**
   - one ST `<tag>.ST` / `<tag>.ST.PAL` for the one recipient: `RRL_SBORKA_PALLETS_ADD2`, two rows `RRL_SBORKA_PALLET_ROWS_ADD4` (KG = NET, EA = 4), two links `RRL_CUSTOMER_ORDER_FULFILLMENT` to both orders, inside `RRL_STOCK_METADATA_TX`;
   - for each CASE: `detach-case` (if in the tree) → `bind-shipment` to the one ST → `attach-case` back;
   - `tree_findings` of the tree after binding.
2. **TRANSPORT_TASK:** dock (config boundary), vehicle/driver/trip via `/api/admin/transport`, PATCH of the trip, the ST on the trip, synthetic vehicle profile with `floor_variants` for `pallet_type_id`.
3. **FLOOR_QC_TARE:** floor type of the root (`/api/inventory/pallet-floor-types`), outgoing QC of the ST (`/scan` with no codes for unmarked goods, or `/weight`), tare count plus a hold on the root (`place_kind=HU`).
4. **LOAD:**
   - `/api/transport/loading/confirm` of the one root (nested; the CASE children inside, no `physical_boxes`), with exact repeat;
   - checks: the sum of goods events = −(NET + 4); one APPLIED operation;
   - `expected_remainder_after_load` is saved for C0190 cleanup.
5. **TARE_HANDOVER:** a separate synthetic driver (RUSERS + rights, `driver-bindings`); offer from the warehouse, accept under the driver's credentials (two different participants).
6. **DEPART:**
   - `/api/transport/loading/{task}/depart` + exact repeat;
   - the load fact becomes DEPARTED; historical tree with `top_place_count=1`;
   - if `DOCUMENT_NOT_READY` comes back → stop **`EXTERNAL_TRANSPORT_DOCUMENT_REQUIRED`**; no synthetic document or ACK is sent.
7. **STORE_RECEIPT:**
   - exactly one address in `RRL_TT_HU_LOAD_ST` (`SINGLE_RECIPIENT_REQUIRED`);
   - synthetic receiver (RUSERS + group with `store_receipt_confirm`), `receivers`, policy `PAPER_COUNT`;
   - preview under the receiver: `root_scan_identifier` = the root, the address = the recipient, not `already_received`; `requires_marked_recipient_flow` → stop `STORE_MARKED_RECIPIENT_FLOW_REQUIRED`;
   - `confirm`: `scan_place` = the root, observations = each loaded STOCK leaf with `accepted` = the loaded quantity, synthetic `paper_reference`;
   - exact repeat; status `ACCEPTED`.

## Checks (commands)
- `python -m pytest -q -p no:cacheprovider tests/tradecase/test_c0191_mixed_tree_transport.py` → 25 passed:
  - input contract (complete and each missing field, WEIGHT QC);
  - synthetic labels;
  - LOAD body;
  - observations per leaf exactly once;
  - receipt of the one root by the one recipient;
  - stops: already received, marked flow, not PAPER_COUNT, another root/address;
  - refusal on incomplete inputs, an unverified tree, changed inputs;
  - DOCUMENT_NOT_READY → an explicit stop with nothing else sent;
  - stage resume; `run` reports the last verified stage;
  - stage order.
- `python scripts/retailcase_quality_gate.py` → PASS; `scripts/check-encoding.ps1` → PASS; `python scripts/check_architecture.py` → PASS.

## Limitations and integration
- **Not run against a live Oracle/API.** The contracts are taken from source (live_nested_shipping, prepare_transport_task, live_transport_documents, case380, route models), but on the non-trade C0190 warehouse the following are not confirmed:
  - binding a CASE to an ST created this way;
  - the outgoing-quality/loading requirements for a CASE tree without BOX containers;
  - departure without a trade trip binding (if it requires a document → an explicit stop);
  - `physical_unit_count=0` for registered lots (otherwise the store requires unit scans → stop).
- **Real external prerequisites:** a READY transport document from ERP (if departure requires it); SAP/SKM acknowledgements of the composition (trade order flow) are not used or simulated by this adapter.
- **C0190 cleanup integration (Codex):**
  - after LOAD the warehouse keeps only the unpicked halves: `transport.expected_remainder_after_load`. C0190 `cleanup()` currently expects the full registered quantity and will refuse; it needs to take that remainder;
  - after DEPART detaching the CASEs is no longer possible (the tree is historical).
- **Adapter cleanup is not implemented:** return the tare from the vehicle (offer/accept), zero the tare, `driver-bindings active=false`, retire the synthetic driver/receiver/group. NS23 `finish()` does it; it is a separate step for Codex.

## Rework K-0224 (the same C0191, after root's live run)
- **Cause:** SHIPMENT stopped in `RRL_SBORKA_PALLET_ROWS_ADD4`. The ST number `<tag>.ST` (16 characters) went into `DOCID VARCHAR2(15)`, giving `ORA-12899`. `ST_NUMBER` in `RRL_SBORKA_PALLETS` allows 50, which is why ADD2 had passed.
- **ST number:** `st_number_for(tag)` = `ST` + 13 characters of the tag's SHA-256 (exactly 15, upper case). Deterministic, so a resume gets the same value, and it works with any tag format.
  - Saved in the state once; a stored valid value (≤15) is kept.
  - Before the first write, a read-only check for foreign use: `ST_NUMBER` in pallets or `DOCID` in rows on another `PALLET_UID` → `ST_NUMBER_COLLISION`.
- **Identifiers unchanged:** the external identifier `<tag>.ST.PAL` and all journal operation_ids.
- **Metadata reconciliation:** every SHIPMENT write (ADD2, CONDITION=0, two ADD4, two fulfillments) goes through `metadata_step`:
  - a read-only check first; a found matching record is reused (`DONE/reconciled`);
  - otherwise the intent `SENT` is saved to the state, then the write, then the check must see the record;
  - after a post-commit failure the retry finds the record, so there is no second ST, row or fulfillment;
  - mismatching existing records → `ST_PALLET_MISMATCH` / `ST_ROW_MISMATCH` / `FULFILLMENT_DUPLICATE`.
- **The failed ST from before the rework** (number >15) → `EXISTING_ST_NUMBER_EXCEEDS_DOCID_15`, a stop for root's repair. The adapter does not repair the fixture.
- **Tests: 33 passed (+8):**
  - the ST number ≤15, stable, different for different tags, any format;
  - a single write with a bounded DOCID;
  - a post-commit failure of ADD2 or of ADD4, then a resume without duplicates;
  - a resume after completion writes nothing;
  - a long ST from before the rework → stop;
  - a foreign DOCID → collision;
  - a mismatching row is not reused.
- gate, encoding and architecture PASS. No live Oracle/API runs. C0190/C0192 not changed.
