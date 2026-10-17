# Права: где проверяются и есть ли в RIGHTS

Маршрутов: 686; различных прав в API: 124; в живом RIGHTS: 157.

| Право | Групп в RIGHTS | Маршрутов | Чтение/изменение | Примеры |
|---|---|---|---|---|
| `api_audit_replay` | 1 | 0 | legacy/БД |  |
| `api_audit_view` | 1 | 3 | RW | GET /api/admin/api-calls; GET /api/admin/api-calls/{api_call_id}; POST /api/admin/api-calls/replay |
| `bom_approve` | 1 | 1 | W | POST /api/bom/{bom_id}/approve |
| `bom_block` | 1 | 2 | W | POST /api/bom/{bom_id}/block; POST /api/bom/{bom_id}/archive |
| `bom_edit` | 1 | 6 | W | POST /api/bom; PATCH /api/bom/{bom_id}; POST /api/bom/{bom_id}/lines |
| `bom_make_primary` | 1 | 1 | W | POST /api/bom/{bom_id}/make-primary |
| `bom_use_alternative` | 1 | 0 | legacy/БД |  |
| `bom_view` | 1 | 4 | RW | GET /api/bom; GET /api/bom/default; GET /api/bom/{bom_id} |
| `calc_tt_price` | 10 | 4 | W | POST /api/finance/expense-allocation; POST /api/finance/logistics-costs/calculate; POST /api/finance/logistics-costs/transport-costs/conduct |
| `case_pick_execute` | 8 | 19 | RW | POST /api/case-pick/tasks/{task}/sscc-label; GET /api/case-pick/tasks/{task}/sscc-label; POST /api/case-pick/tasks/{task}/sscc-label/confirm |
| `case_pick_manage` | 1 | 4 | W | POST /api/case-pick/waves/{pick_wave_id}/ensure; POST /api/case-pick/tasks/{case_pick_task_id}/transfer; POST /api/case-pick/pallet-types |
| `case_pick_short_approve` | 17 | 9 | RW | POST /api/inventory/shorts/{short_id}/investigation; GET /api/case-pick/tasks/{task_id}/partial-shipment-layout; POST /api/case-pick/tasks/{task_id}/partial-shipment-layout |
| `case_pick_view` | 7 | 6 | R | GET /api/case-pick/tasks/{task_id}/pallet-type; GET /api/inventory/recovery-shorts; GET /api/case-pick/tasks |
| `change_addr` | 1 | 0 | legacy/БД |  |
| `change_articul` | 1 | 0 | legacy/БД |  |
| `change_route` | 1 | 0 | legacy/БД |  |
| `change_tt_dock` | 1 | 0 | legacy/БД |  |
| `change_voditel` | 1 | 0 | legacy/БД |  |
| `check_weight` | 4 | 0 | legacy/БД |  |
| `create_fake_pal` | 1 | 0 | legacy/БД |  |
| `create_route` | 1 | 0 | legacy/БД |  |
| `create_tt_price` | 7 | 6 | W | POST /api/finance/logistics-costs/rates; POST /api/finance/logistics-costs/rates/monthly; POST /api/finance/logistics-costs/warehouses/{ware_id}/period-policy |
| `create_vycherk` | 3 | 0 | legacy/БД |  |
| `create_wares` | 1 | 0 | legacy/БД |  |
| `customer_edit` | 1 | 3 | W | POST /api/customers; PATCH /api/customers/{customer_id}; POST /api/customers/{customer_id}/addresses |
| `customer_fulfillment_view` | 1 | 3 | R | GET /api/customer-orders/{order_id}/delivery; GET /api/customer-orders/{order_id}/execution; GET /api/customer-orders/{customer_order_id}/fulfillment |
| `customer_order_import` | 2 | 3 | W | POST /api/integrations/sap/store-orders/{order_id}/prepare-st/automatic; POST /api/integrations/sap/store-orders/{order_id}/prepare-st/automatic/resolve; POST /api/customer-orders/import-legacy/{legacy_order_id} |
| `customer_order_view` | 1 | 7 | RW | GET /api/integrations/sap/store-orders/{order_id}/preparation-readiness; POST /api/integrations/sap/store-orders/{order_id}/preparation-layout; POST /api/integrations/sap/store-orders/{order_id}/automatic-layout |
| `customer_rule_edit` | 2 | 4 | W | POST /api/customers/{customer_id}/product-rules; POST /api/customers/{customer_id}/shelf-life-rules; POST /api/customers/{customer_id}/stack-rules |
| `customer_rule_view` | 1 | 4 | R | GET /api/customers/{customer_id}/product-rules; GET /api/customers/{customer_id}/shelf-life-rules; GET /api/customers/{customer_id}/stack-rules |
| `customer_view` | 1 | 2 | R | GET /api/customers; GET /api/customers/{customer_id} |
| `delete_route` | 1 | 0 | legacy/БД |  |
| `delete_st` | 1 | 0 | legacy/БД |  |
| `divide_st` | 2 | 0 | legacy/БД |  |
| `driver_return_accept` | 18 | 2 | RW | POST /api/delivery/store-return-custody/pickup; GET /api/delivery/store-return-custody/driver |
| `edit_bill_tt` | 8 | 9 | RW | POST /api/finance/logistics-expenses/report; GET /api/admin/transport/billing/orders/{order_id}/export/1c; GET /api/admin/transport/billing/orders/export/1c |
| `external_outbox_retry` | 1 | 0 | legacy/БД |  |
| `external_outbox_view` | 1 | 6 | RW | GET /api/integrations/regulatory/runtime; GET /api/admin/event-outbox; GET /api/admin/event-outbox/{event_outbox_id} |
| `finished_goods_batch_view` | 1 | 1 | R | GET /api/finished-goods/batches |
| `finished_goods_edit` | 1 | 2 | W | PUT /api/finished-goods/skus/{articul}/receiving-policy; PATCH /api/finished-goods/skus/{articul} |
| `finished_goods_export` | 1 | 0 | legacy/БД |  |
| `finished_goods_stock_view` | 1 | 1 | R | GET /api/finished-goods/remains |
| `finished_goods_view` | 1 | 4 | R | GET /api/sku-quality-weight/{warehouse}/{article}; GET /api/finished-goods/skus/{articul}/receiving-policy; GET /api/finished-goods/skus |
| `internal_move` | 5 | 0 | legacy/БД |  |
| `interwarehouse_receive` | 5 | 8 | RW | POST /api/inventory/interwarehouse/unload; POST /api/inventory/interwarehouse/receive; POST /api/inventory/interwarehouse/group-receive |
| `inventory_task_execute` | 12 | 1 | W | POST /api/inventory/tasks/{task_id}/claim |
| `inventory_task_view` | 12 | 2 | R | GET /api/inventory/shorts/{short_id}/investigation; GET /api/inventory/tasks |
| `komplect` | 2 | 0 | legacy/БД |  |
| `load_st` | 2 | 0 | legacy/БД |  |
| `mes_production_complete` | 1 | 1 | W | POST /api/mes/production-orders/{production_order_id}/complete |
| `mes_production_edit` | 1 | 2 | W | POST /api/mes/production-orders; POST /api/mes/production-orders/{production_order_id}/issue-raw |
| `mes_production_view` | 1 | 4 | R | GET /api/mes/production-orders; GET /api/mes/production-orders/{production_order_id}; GET /api/mes/production-orders/{production_order_id}/genealogy |
| `mes_raw_supply_calculate` | 1 | 1 | W | POST /api/mes/production-orders/{production_order_id}/raw-supply/calculate |
| `mes_raw_supply_view` | 1 | 4 | R | GET /api/mes/production-orders/{production_order_id}/raw-supply; GET /api/mes/raw-transfer-tasks; GET /api/mes/raw-transfer-tasks/{task_id} |
| `mes_raw_transfer_cancel` | 1 | 1 | W | POST /api/mes/raw-transfer-tasks/{task_id}/cancel |
| `mes_raw_transfer_confirm` | 1 | 1 | W | POST /api/mes/raw-transfer-tasks/{task_id}/confirm |
| `mes_raw_transfer_create` | 1 | 1 | W | POST /api/mes/production-orders/{production_order_id}/release-to-production |
| `mes_wms_bridge_apply` | 2 | 3 | W | POST /api/inventory/trace-manifests/mes-context; POST /api/mes/production-orders/{production_order_id}/apply-wms; POST /api/mes/movements/{movement_id}/retry |
| `op_change` | 1 | 0 | legacy/БД |  |
| `op_delete` | 1 | 0 | legacy/БД |  |
| `outgoing_pallet_check` | 46 | 7 | RW | GET /api/outgoing-quality/{identifier}; GET /api/outgoing-quality/{identifier}/control-label; POST /api/outgoing-quality/{identifier}/scan |
| `outgoing_pallet_edit` | 5 | 3 | W | POST /api/customer-orders/{order_id}/prepared-layout/move-row; POST /api/inventory/interwarehouse/group-onward; POST /api/inventory/interwarehouse/prepare-onward |
| `pick_plan_cancel` | 1 | 1 | W | POST /api/picking/plans/{pick_plan_id}/cancel |
| `pick_plan_create` | 1 | 2 | RW | GET /api/picking/order-rows/{row}/weighted-box-options; POST /api/picking/plans |
| `pick_plan_view` | 1 | 2 | R | GET /api/picking/plans; GET /api/picking/plans/{pick_plan_id} |
| `pick_reservation_view` | 1 | 1 | R | GET /api/picking/reservations |
| `pick_route_admin_edit` | 1 | 1 | W | POST /api/admin/pick-routes/build |
| `pick_route_admin_publish` | 1 | 1 | W | POST /api/admin/pick-routes/{pick_route_id}/publish |
| `pick_route_admin_view` | 1 | 1 | R | GET /api/admin/pick-routes |
| `pick_shortage_view` | 1 | 2 | R | GET /api/picking/shortages; GET /api/picking/plans/{pick_plan_id}/shortages |
| `pick_topology_edit` | 1 | 9 | W | POST /api/inventory/slotting/warehouses/{ware_id}/articles/{article}/recommendations; POST /api/inventory/slotting/warehouses/{ware_id}/articles/{article}/recommendations/{proposal_id}/cancel; POST /api/inventory/slotting/warehouses/{ware_id}/articles/{article}/recommendations/{proposal_id}/approve |
| `pick_topology_view` | 1 | 7 | RW | GET /api/inventory/slotting/warehouses/{ware_id}/articles/{article}/recommendations/{proposal_id}; POST /api/inventory/slotting/warehouses/{ware_id}/articles/{article}/scenario; GET /api/picking/routes |
| `pick_wave_audit_view` | 1 | 1 | R | GET /api/picking/waves/{pick_wave_id}/audit |
| `pick_wave_calculate` | 1 | 1 | W | POST /api/picking/waves/{pick_wave_id}/calculate |
| `pick_wave_cancel` | 1 | 1 | W | POST /api/picking/waves/{pick_wave_id}/cancel |
| `pick_wave_create` | 1 | 2 | W | POST /api/picking/waves; POST /api/picking/waves/{pick_wave_id}/plans |
| `pick_wave_launch` | 1 | 8 | W | POST /api/inventory/minimax/{warehouse}/reconcile; POST /api/picking/waves/{wave_id}/finish-execution; POST /api/picking/waves/{wave_id}/release-picking |
| `pick_wave_release_reserves` | 1 | 1 | W | POST /api/picking/waves/{pick_wave_id}/release-reservations |
| `pick_wave_settings_edit` | 1 | 0 | legacy/БД |  |
| `pick_wave_settings_view` | 1 | 0 | legacy/БД |  |
| `pick_wave_view` | 1 | 14 | R | GET /api/inventory/minimax/{warehouse}; GET /api/inventory/replenishment-progress; GET /api/inventory/stock-posting/source-availability |
| `plan_tt_time` | 1 | 0 | legacy/БД |  |
| `print_op_passport_unlimit` | 1 | 0 | legacy/БД |  |
| `quality_batch_edit` | 1 | 1 | W | PATCH /api/admin/product-shipment-settings/{articul} |
| `quality_batch_view` | 1 | 1 | R | GET /api/admin/product-shipment-settings |
| `raw_material_edit` | 1 | 1 | W | PATCH /api/raw-material/skus/{articul} |
| `raw_material_export` | 1 | 0 | legacy/БД |  |
| `raw_material_stock_view` | 1 | 1 | R | GET /api/raw-material/remains |
| `raw_material_view` | 1 | 2 | R | GET /api/raw-material/skus; GET /api/raw-material/warehouses |
| `regulatory_adapter_retry` | 1 | 0 | legacy/БД |  |
| `regulatory_adapter_view` | 1 | 0 | legacy/БД |  |
| `resource_dispatch_manage` | 1 | 1 | W | POST /api/resources/warehouse-tasks/{task_id}/dispatch-nearest |
| `resource_gantt_replan` | 1 | 0 | legacy/БД |  |
| `resource_gantt_view` | 1 | 0 | legacy/БД |  |
| `resource_management_edit` | 1 | 2 | W | POST /api/resources/equipment; POST /api/resources |
| `resource_management_view` | 1 | 5 | R | GET /api/resources/{resource_id}/qualifications; GET /api/resources/warehouse-tasks/{task_id}/candidates; GET /api/resources/types |
| `resource_session_manage` | 1 | 6 | W | POST /api/resources/sessions/login; POST /api/resources/sessions/tsd-login; POST /api/resources/sessions/{session_id}/heartbeat |
| `resource_session_view` | 1 | 1 | R | GET /api/resources/sessions |
| `resource_shift_edit` | 2 | 7 | W | POST /api/resources/reach-shifts/{base_shift_id}; POST /api/resources/workload/norms; POST /api/resources/workload/attendance |
| `resource_shift_view` | 2 | 5 | RW | GET /api/resources/reach-shifts/{base_shift_id}; GET /api/resources/workload/warehouses/{ware_id}; GET /api/resources/workload/warehouses/{ware_id}/attendance/{plan_id}/history |
| `rights_admin_edit` | 1 | 12 | W | POST /api/admin/rights/groups; POST /api/admin/rights/groups/{group_id}/rights; DELETE /api/admin/rights/groups/{group_id}/rights/{right_name} |
| `rights_admin_view` | 1 | 6 | R | GET /api/admin/rights/users; GET /api/admin/rights/groups; GET /api/admin/rights/groups/{group_id}/rights |
| `sap_article_import` | 1 | 2 | RW | POST /api/integrations/sap/artmas; GET /api/integrations/sap/artmas/{inbox_id} |
| `sap_return_import` | — | 1 | W | POST /api/integrations/sap/store-returns |
| `sap_store_all_ware` | 1 | 0 | legacy/БД |  |
| `sap_store_decision_import` | 1 | 1 | W | POST /api/integrations/sap/store-decisions |
| `sap_store_order_import` | 2 | 0 | legacy/БД |  |
| `sap_supply_import` | 1 | 3 | W | POST /api/integrations/sap/receipt-events/acknowledgements; POST /api/integrations/sap/receipt-events/{event_id}/retry; POST /api/integrations/sap/supply-orders |
| `sap_supply_view` | — | 6 | RW | GET /api/integrations/sap/receipt-events; GET /api/integrations/sap/supply-orders; GET /api/integrations/sap/supply-orders/by-receipt-document/{document_id} |
| `second_ch_wood` | 1 | 0 | legacy/БД |  |
| `slow_sql_view` | 1 | 4 | R | GET /api/admin/slow-sql; GET /api/admin/slow-sql/top; GET /api/admin/slow-sql/oracle-top |
| `stock_compatibility_admin` | — | 1 | W | POST /api/inventory/stock-posting/compatibility-setting |
| `stock_inventory_count` | 13 | 5 | RW | GET /api/inventory/stock-posting/inventory/{revision_id}/lots; POST /api/inventory/stock-posting/inventory/counts; POST /api/inventory/stock-posting/inventory/revisions |
| `stock_manager` | 2 | 0 | legacy/БД |  |
| `stock_posting_manual_move` | — | 2 | W | POST /api/inventory/stock-posting/manual-moves; POST /api/inventory/stock-posting/compatibility/manual-moves |
| `stock_posting_shipping` | 12 | 9 | RW | GET /api/inventory/pallet-floor-types; POST /api/inventory/pallet-floor-types; POST /api/warehouse-hus/ship |
| `stock_receipt_reverse` | — | 1 | W | POST /api/inventory/stock-posting/receipt-documents/{document_id}/reverse |
| `stock_reservation_edit` | 1 | 6 | W | POST /api/inventory/soft-pools/{warehouse}/{article}/allocate; POST /api/stock-reservations; POST /api/stock-reservations/{reservation_id}/promote-to-hard |
| `stock_reservation_view` | 1 | 6 | R | GET /api/inventory/soft-pools/{warehouse}/{article}; GET /api/inventory/stock-posting/status; GET /api/inventory/stock-posting/operations/{operation_id} |
| `stock_ship_pallet` | 1 | 0 | legacy/БД |  |
| `store_case_investigate` | 4 | 3 | RW | POST /api/delivery/case-work/{case_id}/finding; GET /api/delivery/case-work/mine; GET /api/delivery/case-work/{case_id}/investigation |
| `store_case_manage` | 1 | 2 | RW | POST /api/delivery/case-work/{case_id}/assign; GET /api/delivery/case-work/{case_id}/management |
| `store_loss_confirm` | 4 | 3 | RW | POST /api/delivery/case-work/{case_id}/loss; GET /api/delivery/case-work/{case_id}/loss-review; POST /api/delivery/case-work/{case_id}/close |
| `store_receipt_confirm` | 13 | 10 | RW | POST /api/delivery/store-photos/upload; GET /api/delivery/store-photos/list; GET /api/delivery/store-photos/{photo_id}/content |
| `store_return_approve` | 5 | 10 | RW | POST /api/delivery/store-returns/{receipt_id}/approve; GET /api/delivery/store-returns/{receipt_id}; GET /api/delivery/store-returns/{receipt_id}/reuse-preview |
| `store_return_handover` | 2 | 2 | RW | POST /api/delivery/store-return-custody/handover; GET /api/delivery/store-return-custody/store |
| `store_return_transport` | — | 3 | RW | POST /api/delivery/store-return-transport/plan; GET /api/delivery/store-return-transport/eligible; GET /api/delivery/store-return-transport/trips/{task_id} |
| `store_scale_ingest` | 12 | 1 | W | POST /api/delivery/store-scales/captures |
| `storno_prihod` | 1 | 0 | legacy/БД |  |
| `tare_accept` | 12 | 1 | W | POST /api/inventory/tare/accept |
| `tare_adjust` | — | 1 | W | POST /api/inventory/tare/count |
| `tare_damage` | 3 | 1 | W | POST /api/inventory/tare/damage |
| `tare_loss_report` | 4 | 1 | W | POST /api/inventory/tare/loss-report |
| `tare_offer` | 10 | 2 | W | POST /api/inventory/tare/offer; POST /api/inventory/tare/offer-cancel |
| `tare_plan` | 2 | 2 | W | POST /api/inventory/tare/book; POST /api/inventory/tare/book-cancel |
| `tare_view` | 14 | 13 | R | GET /api/inventory/tare/warehouses/{ware_id}/availability; GET /api/inventory/tare/warehouses/{ware_id}/bookings; GET /api/inventory/tare/assembly/catalog |
| `tare_writeoff` | 4 | 2 | W | POST /api/inventory/tare/loss-decide; POST /api/inventory/tare/writeoff |
| `trace_manifest_import` | 2 | 3 | RW | POST /api/inventory/trace-manifests; GET /api/inventory/trace-manifests/warehouses/{ware_id}; POST /api/inventory/trace-manifests/aggregations/invalidate |
| `traceability_view` | 1 | 4 | R | GET /api/receiving/pallets/{pallet}/composition; GET /api/inventory/trace-manifests/warehouses/{ware_id}/pallets/{origin}/aggregations; GET /api/trace/entities/{entity_type}/{entity_id}/forward |
| `transport_dispatch_close` | — | 3 | W | POST /api/delivery/store-receipts/load-custody/release; POST /api/transport/loading/{task_id}/depart; POST /api/admin/transport/tasks/{task_id}/close |
| `transport_dispatch_edit` | 7 | 40 | RW | POST /api/finance/day-reconciliation/reviews; POST /api/finance/day-reconciliation/reviews/resolve; GET /api/inventory/interwarehouse/source-loads/{load_id}/group-composition |
| `transport_dispatch_view` | 22 | 89 | RW | GET /api/delivery/store-receipts/cases; GET /api/delivery/store-receipts/cases/{case_id}; GET /api/finance/day-reconciliation/warehouses/{ware_id} |
| `transport_fleet_edit` | — | 7 | W | POST /api/admin/transport/vehicle-profiles; POST /api/admin/transport/vehicles; PATCH /api/admin/transport/vehicles/{vehicle_id} |
| `vehicle_type_edit` | 1 | 1 | W | POST /api/vehicle-types |
| `vehicle_type_view` | 1 | 1 | R | GET /api/vehicle-types |
| `view_adress` | 2 | 0 | legacy/БД |  |
| `view_billing` | 5 | 0 | legacy/БД |  |
| `view_pall_hist` | 2 | 0 | legacy/БД |  |
| `view_route` | 8 | 0 | legacy/БД |  |
| `view_tt_billing` | 1 | 0 | legacy/БД |  |
| `view_vesov` | 8 | 0 | legacy/БД |  |
| `warehouse_day_inspect` | 1 | 0 | legacy/БД |  |
| `warehouse_receipt_confirm` | — | 4 | RW | POST /api/receiving/supply-orders/{order_id}/labels; GET /api/receiving/labels/{label_id}; POST /api/receiving/labels/{label_id}/confirm |
| `warehouse_receipt_reconcile` | — | 2 | W | POST /api/receiving/supply-orders/{order_id}/close; POST /api/receiving/supply-orders/{order_id}/reopen |
| `warehouse_return_dispatch` | 5 | 5 | RW | POST /api/inventory/return-disposal/report; GET /api/inventory/return-disposal/warehouses/{ware_id}; POST /api/inventory/supplier-handover/record |
| `warehouse_return_place` | 1 | 2 | RW | GET /api/inventory/store-return-putaway/warehouses/{ware_id}/pending; POST /api/inventory/store-return-putaway/plan |
| `warehouse_return_receive` | 3 | 4 | RW | GET /api/inventory/store-returns/warehouses/{ware_id}/pending; POST /api/inventory/store-returns/receive; GET /api/inventory/store-returns/warehouses/{ware_id}/pending-page |
| `warehouse_scale_ingest` | 35 | 2 | W | POST /api/inventory/warehouse-scales/captures; POST /api/inventory/warehouse-scales/final-captures |
| `warehouse_settings_edit` | 1 | 27 | RW | PUT /api/delivery/store-receipts/policy; POST /api/delivery/store-receipts/receivers; PUT /api/delivery/store-scales/devices/{device_id} |
| `warehouse_settings_view` | 1 | 6 | R | GET /api/inventory/quality-policies/warehouses/{warehouse}; GET /api/receiving/warehouses/{warehouse}/settings; GET /api/receiving/warehouses/{warehouse}/skus/{articul}/placement-rule |
| `warehouse_task_assign` | — | 1 | W | POST /api/receiving/putaway/{task_id}/replan |
| `warehouse_task_edit` | 2 | 2 | W | POST /api/receiving/st-deferrals/waiting-tasks; POST /api/warehouse-tasks/{task_id}/cancel |
| `warehouse_task_execute` | 14 | 21 | RW | POST /api/warehouse-tasks/{task_id}/full-pallet-shipment; POST /api/inventory/interwarehouse/group-placement; POST /api/receiving/putaway/{task_id}/complete |
| `warehouse_task_force_assign` | 1 | 0 | legacy/БД |  |
| `warehouse_task_view` | 14 | 10 | R | GET /api/warehouse-tasks/{task_id}/full-pallet-shipment; GET /api/warehouse-tasks/{task_id}/scan-context; GET /api/receiving/st-deferrals/waiting-tasks |
| `warehouse_topology_edit` | 1 | 32 | W | POST /api/admin/warehouse-map/canvases/{canvas_id}/archive; POST /api/admin/warehouse-map/warehouses/{ware_id}/canvases; POST /api/admin/warehouse-map/canvases/{canvas_id}/cameras |
| `warehouse_topology_publish` | 1 | 1 | W | POST /api/admin/warehouse-topologies/{topology_id}/publish |
| `warehouse_topology_view` | 1 | 11 | RW | GET /api/admin/warehouse-map/warehouses/{ware_id}/canvases; GET /api/admin/warehouse-map/warehouses/{ware_id}/state; GET /api/admin/warehouse-map/canvases/{canvas_id} |
| `wms_admin_login` | 7 | 2 | R | GET /api/admin/auth/login; GET /api/admin/auth/me |