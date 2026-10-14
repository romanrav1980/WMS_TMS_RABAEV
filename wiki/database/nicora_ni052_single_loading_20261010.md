# NI05.2 — самостоятельный CASE/FULLPAL и контроль без списания
10.10.2026.078/079 APPLIED RABAEV/orcl. Inventory shipping/P/H owner retained; transport physical fact/departure owner, root RRL_STOCK_POSTING_API one transaction.

LOAD_SHIPMENT загружает существующий физический CASE либо целую подтверждённую FULLPAL по existing ST. RRL_STOCK_LOADING_READ returns current source/snapshot/QC signature; expected_composition_signature and current version bind scan/manual SI to actual composition. Nested place must use whole upper HU, unbound legacy ST cannot select arbitrary stock by article. Same RRL_STOCK_SHIPPING_CORE executes stock effect, no second shipping engine.

RRL_TT_HU_LOAD_FACT has exactly one physical owner: ROOT_UID FK to actual pallet/container OR nullable ROOT_CASE_TASK_ID FK to actual CASE. Existing pallet FK/history retained, no backfill and no fictitious PP. Conditional unique CASE owner prevents double loading; same current TT/vehicle/dock/capacity/membership and departure rules077 apply. API /single-preview,/confirm-single; ARM selects upper HU vs standalone CASE/pallet by ST and persists exact intent.

079 removes quantity consumption from successful QC even when legacy SPIS_OTBOR_ON_SCAN_OPALL=1. SCAN/WEIGHT/WEIGHT2 grant current approval/CONTROLLED, return physical_loading_required, shipped=0; actual loading is separate. Old stored QC operation results are immutable and may truthfully contain historical shipped=1; replay does not reinterpret history. Raw QC screen no longer promises automatic shipping. Compatibility field preserved but is not authority to prove physical load.

## Evidence
Author ni052_single_fullpal_case: current actual FULLPAL3/ST whole relocation→standalone load/no outer HU/P0H0/replay; wrong scans and pending ST departure denied; same reassignment protections, separate departure no qty journal; own P/H cleaned. Final history assertion initially double-decoded a driver JSON dict (test-only); script corrected and actual departed snapshot9b15cf997d separately queried: root actual FULL.QA UID/quantity3.

Author ni052_single_case_case passed: native12+8 independent BOTH→two standalone CASE loads/direct CASE FKs/no fake PP/P0H0/replay→departure two places. ni052_qc_separation_case passed same flow retaining old auto flag1: QC ready/shipped0/loading_required; only explicit physical loading consumes. Own stock0, CASE/operation/load history retained. OpenAPI and JS syntax checked.

Full NI05.2 remains open: already logically shipped legacy reconciliation, confirmed physical unload/compensation, trip/staging/order-edit serialization, regulatory recipient/operation ACK, independent concurrency/marked/browser acceptance. No government ACK simulated. Backward rollbacks078/079 refuse unsafe old physical ownership/auto-shipment, forward repair preserves history. Checkpoints375–378 and versioned SQL retained.
[078](../../db/migrations/2026-10-10_ni052_single_load/apply.sql) · [079](../../db/migrations/2026-10-10_ni052_qc_separation/apply.sql) · [[nicora_ni052_loading_20261010]].

Slow SQL078/079: SingleREAD.preview_json gr2adrn2nbgy8 34.286ms/5, retain bounded actual ST/UID/200 legs; NI08 owner verifies volume/plan before index decisions. Metadata user_constraints/columns join8j9gd5wf9tndd8655.258ms/1 is tooling, avoid repeat/broad catalog join and use focused object queries. V$SQL_PLAN privilege unavailable; no runtime load claim.
