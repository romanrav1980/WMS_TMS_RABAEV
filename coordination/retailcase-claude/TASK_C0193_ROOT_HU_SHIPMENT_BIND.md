# C-0193 — bind one root HU to one mixed shipment

This is a new independent T06/T07 implementation block. Do not edit C0190, C0191, C0192, live state, migrations, or restart/publish anything.

## Problem proved by the live run

The current case endpoint binds one complete physical CASE carrier to one ST. It rejects a second CASE when the ST contains the aggregate KG + EA composition. A parent HU with several CASE children must be bound to one ST and one recipient without splitting its children among STs.

## Result

Implement a supported API for binding one existing root HU to one existing prepared ST:

- public request includes operation_id, shipment_identifier, scanned_root, expected root content version;
- the root is a PALLET/BOX HU at one warehouse and must contain one or more closed CASE children;
- read the whole root composition and require exact base-unit equality with all ST rows;
- require exactly one prepared fulfillment per source customer order and one recipient address for all those fulfillments;
- atomically bind every included CASE task to the same ST and update each matching fulfillment with its own CASE composition/version;
- preserve the HU tree; do not detach/repack it;
- reject a root with a child already bound to another ST, a foreign/missing CASE, different recipient, changed root/child version, changed composition, or an ST already bound to another physical root;
- exact same operation and body must be idempotent; changed body under the same operation must conflict; no duplicate fulfillment/event effects.

Use the RETAILCASE module boundary: inventory API/application/domain/infrastructure as appropriate, with a public contract. Reuse existing composition/quantity helpers and supported metadata transaction boundaries. Do not create an API that directly updates stock or fakes a shipment.

## Acceptance

Add focused offline tests that cover a two-CASE KG+EA root, one recipient/one ST success, all listed refusals, exact replay, changed-body conflict, and source inspection showing no child/ST split. Provide RESULT/RELEASE and an ACK first. No live Oracle/API write.
