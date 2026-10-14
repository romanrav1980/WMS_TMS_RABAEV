# Qwen078/079 — standalone loading/QC separation
Own native data only; author scripts ni052_single_fullpal_case.py,ni052_single_case_case.py,ni052_qc_separation_case.py.
1. Actual FULLPAL/ST/current signature -> one standalone physical load/current TT+vehicle+dock/P0H0/replay, no fake outer HU.
2. CASE12+8/current independent BOTH -> two direct CASE FK facts/no fake PP/two physical places/departure no second qty effect.
3. Keep legacy auto flag1: PLAN/SCAN/WEIGHT2 ready but P/H unchanged/shipped0/loading_required. Historical older shipped1 replay remains immutable, not counted as loading.
4. Stale composition/current version/wrong place/cell/vehicle/dock/foreign ST/overcapacity denies without partial effects; nested standalone requires whole HU.
5. Exact one physical owner CHECK/FKs/unique active pallet and CASE; direct fact/member mutation denied.
6. Concurrent count/QC/load/trip reassignment/departure: consistent current closure/actual-row order, one effect/outbox/replay.
7. ARM mode/preview/signature/scan/intent; known rejection can correct, uncertain retains original. No government ACK substitution.
8. Only own cleanup, longest SQL decision; legacy reconciliation/unloading/regulatory/independent sprint acceptance still open.
