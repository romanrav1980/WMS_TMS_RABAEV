# HU thermal admission — PREPARED

Existing RRL_RECEIPT_SKU_RULE / RRL_RECEIPT_CELL_RULE remain the only normative
temperature model. New pure bounded helper returns intersection, target range,
status and explicit policy_only/observed_temperature_c=null. No sensor fact is
invented. Reuses existing RRL_INTERWARE_THERMAL.assert_cell under writer fences.

All-unknown existing trees remain UNSPECIFIED (not thermally approved); a known
range mixed with unknown SKU or disjoint ranges rejects. A known range requires
the entire target cell range inside the common product interval. Invalid or
missing cell/SKU ranges reject; empty packaging has no product requirement.
Future strict consolidation manifests can require known policy explicitly.

CASE_CARRIER_MOVE, HU_ATTACH, whole HU_MOVE and HU_SHIP compile native admission, then
recompute/compare under existing CONFIG/cell/stock/CASE locks before effects.
DETACH stays possible as remediation. No quantity writer, new table or change
to existing transfer/CASE/ST/tare owner. Native mode read is pure SELECT; no
locks, sequence, commit or context mutation. Python HU preview adds the policy
inside its existing READ ONLY scope snapshot; archived departures are not
evaluated against current policy or relabelled as observed cold-chain facts.

2MiB per node JSON input/200 combined nodes; source identities are existing
resolved server snapshots, never client-supplied admission. Source/hash/rollback
kit preserves history. DB rollback requires reverting Python consumer to its
saved before image before dropping the helper. Author review only; native
policy matrix, real isolated move/pack/closure-change/concurrency and SQL pending.
Mixed manifest, CASE-aware interWARE, subtree handover and SHIPPING_GROSS remain.
