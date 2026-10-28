# Multi-order root-HU shipment

This migration makes `RRL_STOCK_SHIPPING_CORE` ship one root pallet that contains CASE children from several customer orders of the same recipient. It keeps the physical rule: one root pallet, one shipment, one recipient. It never turns CASE children into separately issued store pallets.

The compiler assigns each allocation to its customer order, fulfillment and CASE. Execution locks each slice, consumes its own reservation, projects its own fulfillment fact and marks only that CASE as shipped. The root branch requires the `HU_SHIP` operation and runs outgoing QC on the resulting composite domain. A final-weight CASE raises the QC policy; the whole-pallet exemption is not used for the composite plan.

The implementation is private to `RRL_STOCK_SHIPPING_CORE`. Protected stock-effect, CASE-carrier, fulfillment and placement packages already permit this caller, so no `ACCESSIBLE BY` list is widened.

Before Oracle application: take the migration-only checkpoint, run `000_preflight.sql`, compile with `apply.sql`, run `verify.sql`, then prove an isolated mixed KG/EA fixture, exact repeated `operation_id`, rollback sources and a competing shipment refusal. The migration is not evidence of any of those checks by itself.
