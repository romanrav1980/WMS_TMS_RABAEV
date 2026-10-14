# Qwen: NI05.3/090 — исходный заказ и принятое количество
Read wiki/database/retailcase_ni053_order_delivery_20261010.md. Existing customer order/fulfillment/ST/source root shipment required; no second order/ST setup.

Verify actual partial3 shipped /2 accepted /1 missing, full3, and full3 with weight case. GET /api/customer-orders/{id}/delivery requires customer_fulfillment_view; exact separate SKU/BASE quantities. Original ORDER_QTY and warehouse FF SHIPPED fact must stay unchanged. Pending unshipped fulfillment visible; status for shipped volume must not claim whole original demand completion.

Original frozen customer owner from SHIP_PALLET/HU_SHIP/LOAD_SHIPMENT must match current source links. Missing/uncommitted/inconsistent provenance refuses. Historical inactive load links must retain original receipt after unloading; validate only through authorized existing actions.

Shared leaf with several original owners: partial acceptance remains unallocated, no pro-rata credit; full acceptance credits original shipped shares. Test real supported multi-owner source if available, keep pure domain fixture evidence separate. Different SKU/BASE never summed.

Read-only snapshot: a concurrent receipt should produce a coherent before-or-after report; no mixed partial projection. Bounds200 fulfillments/2000 legs explicit. Browser order detail table and late-response source change. Retain original immutable history; no P/H fixtures modified by reader. Largest SQL/decision recorded.
