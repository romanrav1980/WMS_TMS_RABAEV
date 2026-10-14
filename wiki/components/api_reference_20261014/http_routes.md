# HTTP API: опубликованные маршруты

Источник: OpenAPI работающего API на дату выпуска. Полные request/response schemas, required поля и ссылки — в [openapi.json](openapi.json). Авторизация и предметные права дополнительно проверяются серверными зависимостями; наличие маршрута не предоставляет право.

| Метод | Путь | Назначение / summary | operationId |
|---|---|---|---|
| GET | `/api/resources/{resource_id}/qualifications` | List Qualifications | list_qualifications_api_resources__resource_id__qualifications_get |
| PUT | `/api/resources/{resource_id}/qualifications` | Save Qualification | save_qualification_api_resources__resource_id__qualifications_put |
| POST | `/api/resources/sessions/{session_id}/position` | Confirm Position | confirm_position_api_resources_sessions__session_id__position_post |
| GET | `/api/resources/warehouse-tasks/{task_id}/candidates` | Nearest Candidates | nearest_candidates_api_resources_warehouse_tasks__task_id__candidates_get |
| POST | `/api/resources/warehouse-tasks/{task_id}/dispatch-nearest` | Dispatch Nearest | dispatch_nearest_api_resources_warehouse_tasks__task_id__dispatch_nearest_post |
| POST | `/api/integrations/sap/store-orders/{order_id}/prepare-st` | Prepare St | prepare_st_api_integrations_sap_store_orders__order_id__prepare_st_post |
| POST | `/api/integrations/sap/store-orders` | Receive Order | receive_order_api_integrations_sap_store_orders_post |
| GET | `/api/integrations/sap/store-orders` | List Orders | list_orders_api_integrations_sap_store_orders_get |
| PUT | `/api/integrations/sap/store-orders/warehouses/{warehouse}/stores/{store_code}/calendar` | Configure Calendar | configure_calendar_api_integrations_sap_store_orders_warehouses__warehouse__stores__store_code__calendar_put |
| GET | `/api/integrations/sap/store-orders/{order_id}` | Get Order | get_order_api_integrations_sap_store_orders__order_id__get |
| GET | `/api/integrations/sap/store-orders/warehouses/{warehouse}/stores/{store_code}/calendar-context` | Calendar Context | calendar_context_api_integrations_sap_store_orders_warehouses__warehouse__stores__store_code__calendar_context_get |
| POST | `/api/integrations/sap/store-orders/calendar-exceptions` | Calendar Exception | calendar_exception_api_integrations_sap_store_orders_calendar_exceptions_post |
| POST | `/api/integrations/sap/store-orders/{order_id}/prepare-st/resolve` | Resolve Preparation | resolve_preparation_api_integrations_sap_store_orders__order_id__prepare_st_resolve_post |
| GET | `/api/customer-orders/{order_id}/execution` | Execution | execution_api_customer_orders__order_id__execution_get |
| GET | `/api/finished-goods/skus/{articul}/receiving-policy` | Get Receiving Policy | get_receiving_policy_api_finished_goods_skus__articul__receiving_policy_get |
| PUT | `/api/finished-goods/skus/{articul}/receiving-policy` | Save Receiving Policy | save_receiving_policy_api_finished_goods_skus__articul__receiving_policy_put |
| GET | `/api/inventory/minimax/{warehouse}` | Preview | preview_api_inventory_minimax__warehouse__get |
| POST | `/api/inventory/minimax/{warehouse}/reconcile` | Reconcile | reconcile_api_inventory_minimax__warehouse__reconcile_post |
| GET | `/api/resources/reach-shifts/{base_shift_id}` | Read | read_api_resources_reach_shifts__base_shift_id__get |
| POST | `/api/resources/reach-shifts/{base_shift_id}` | Create | create_api_resources_reach_shifts__base_shift_id__post |
| GET | `/api/inventory/shorts/{short_id}/investigation` | Read | read_api_inventory_shorts__short_id__investigation_get |
| POST | `/api/inventory/shorts/{short_id}/investigation` | Review | review_api_inventory_shorts__short_id__investigation_post |
| PUT | `/api/inventory/cctv-viewpoints` | Configure | configure_api_inventory_cctv_viewpoints_put |
| GET | `/api/inventory/cctv-viewpoints` | Camera Settings | camera_settings_api_inventory_cctv_viewpoints_get |
| GET | `/api/inventory/soft-pools/{warehouse}/{article}` | Preview | preview_api_inventory_soft_pools__warehouse___article__get |
| POST | `/api/inventory/soft-pools/{warehouse}/{article}/allocate` | Allocate | allocate_api_inventory_soft_pools__warehouse___article__allocate_post |
| GET | `/api/sku-allocation/{warehouse}/{article}` | Get Policy | get_policy_api_sku_allocation__warehouse___article__get |
| PUT | `/api/sku-allocation/{warehouse}/{article}` | Set Policy | set_policy_api_sku_allocation__warehouse___article__put |
| POST | `/api/integrations/sap/artmas` | Receive Artmas | receive_artmas_api_integrations_sap_artmas_post |
| GET | `/api/integrations/sap/artmas/{inbox_id}` | Get Artmas | get_artmas_api_integrations_sap_artmas__inbox_id__get |
| GET | `/api/integrations/regulatory/runtime` | Runtime | runtime_api_integrations_regulatory_runtime_get |
| POST | `/api/integrations/sap/supply-orders` | Import Supply | import_supply_api_integrations_sap_supply_orders_post |
| GET | `/api/integrations/sap/supply-orders` | List Supplies | list_supplies_api_integrations_sap_supply_orders_get |
| GET | `/api/integrations/sap/supply-orders/by-receipt-document/{document_id}` | Supply By Document | supply_by_document_api_integrations_sap_supply_orders_by_receipt_document__document_id__get |
| GET | `/api/integrations/sap/supply-orders/{order_id}` | Supply Detail | supply_detail_api_integrations_sap_supply_orders__order_id__get |
| POST | `/api/integrations/sap/supply-orders/{order_id}/pallet-plan` | Supply Pallet Plan | supply_pallet_plan_api_integrations_sap_supply_orders__order_id__pallet_plan_post |
| GET | `/api/integrations/sap/supply-orders/{order_id}/receipt-history` | History | history_api_integrations_sap_supply_orders__order_id__receipt_history_get |
| GET | `/api/integrations/sap/receipt-events` | List Receipt Events | list_receipt_events_api_integrations_sap_receipt_events_get |
| POST | `/api/integrations/sap/receipt-events/acknowledgements` | Receive Ack | receive_ack_api_integrations_sap_receipt_events_acknowledgements_post |
| POST | `/api/integrations/sap/receipt-events/{event_id}/retry` | Retry Receipt Event | retry_receipt_event_api_integrations_sap_receipt_events__event_id__retry_post |
| GET | `/api/receiving/pallets/{pallet}/composition` | Pallet Composition | pallet_composition_api_receiving_pallets__pallet__composition_get |
| POST | `/api/receiving/putaway/{task_id}/replan` | Replan Putaway | replan_putaway_api_receiving_putaway__task_id__replan_post |
| POST | `/api/receiving/supply-orders/{order_id}/labels` | Issue Label | issue_label_api_receiving_supply_orders__order_id__labels_post |
| GET | `/api/receiving/labels/{label_id}` | Read Label | read_label_api_receiving_labels__label_id__get |
| POST | `/api/receiving/labels/{label_id}/confirm` | Confirm Label | confirm_label_api_receiving_labels__label_id__confirm_post |
| GET | `/api/receiving/warehouses/{warehouse}/settings` | Get Settings | get_settings_api_receiving_warehouses__warehouse__settings_get |
| PUT | `/api/receiving/warehouses/{warehouse}/settings` | Save Settings | save_settings_api_receiving_warehouses__warehouse__settings_put |
| PUT | `/api/receiving/warehouses/{warehouse}/skus/{articul}/placement-rule` | Save Sku Rule | save_sku_rule_api_receiving_warehouses__warehouse__skus__articul__placement_rule_put |
| GET | `/api/receiving/warehouses/{warehouse}/skus/{articul}/placement-rule` | Read Sku Rule | read_sku_rule_api_receiving_warehouses__warehouse__skus__articul__placement_rule_get |
| GET | `/api/receiving/warehouses/{warehouse}/cells/{cell}/placement-rule` | Read Cell Rule | read_cell_rule_api_receiving_warehouses__warehouse__cells__cell__placement_rule_get |
| PUT | `/api/receiving/warehouses/{warehouse}/cells/{cell}/placement-rule` | Save Cell Rule | save_cell_rule_api_receiving_warehouses__warehouse__cells__cell__placement_rule_put |
| POST | `/api/receiving/supply-orders/{order_id}/close` | Close Supply | close_supply_api_receiving_supply_orders__order_id__close_post |
| POST | `/api/receiving/supply-orders/{order_id}/reopen` | Reopen Supply | reopen_supply_api_receiving_supply_orders__order_id__reopen_post |
| POST | `/api/receiving/supply-orders/{order_id}/pallets` | Receive Pallet | receive_pallet_api_receiving_supply_orders__order_id__pallets_post |
| POST | `/api/receiving/putaway/{task_id}/complete` | Complete Putaway | complete_putaway_api_receiving_putaway__task_id__complete_post |
| POST | `/api/inventory/stock-posting/manual-moves` | Manual Move | manual_move_api_inventory_stock_posting_manual_moves_post |
| POST | `/api/inventory/stock-posting/compatibility-setting` | Set Compatibility | set_compatibility_api_inventory_stock_posting_compatibility_setting_post |
| POST | `/api/inventory/stock-posting/compatibility/manual-moves` | Compatibility Manual Move | compatibility_manual_move_api_inventory_stock_posting_compatibility_manual_moves_post |
| POST | `/api/inventory/stock-posting/receipt-documents/{document_id}/reverse` | Reverse Receipt | reverse_receipt_api_inventory_stock_posting_receipt_documents__document_id__reverse_post |
| GET | `/api/inventory/stock-posting/inventory/{revision_id}/lots` | Inventory Lots | inventory_lots_api_inventory_stock_posting_inventory__revision_id__lots_get |
| POST | `/api/inventory/stock-posting/inventory/counts` | Inventory Count | inventory_count_api_inventory_stock_posting_inventory_counts_post |
| POST | `/api/inventory/stock-posting/inventory/revisions` | Create Inventory Revision | create_inventory_revision_api_inventory_stock_posting_inventory_revisions_post |
| POST | `/api/inventory/stock-posting/inventory/lots` | Register Inventory Lot | register_inventory_lot_api_inventory_stock_posting_inventory_lots_post |
| GET | `/api/inventory/stock-posting/status` | Status | status_api_inventory_stock_posting_status_get |
| GET | `/api/inventory/stock-posting/operations/{operation_id}` | Operation | operation_api_inventory_stock_posting_operations__operation_id__get |
| GET | `/api/warehouse-tasks/{task_id}/scan-context` | Get Scan Context | get_scan_context_api_warehouse_tasks__task_id__scan_context_get |
| GET | `/api/warehouse-tasks/{task_id}/scan-draft` | Get Scan Draft | get_scan_draft_api_warehouse_tasks__task_id__scan_draft_get |
| POST | `/api/warehouse-tasks/{task_id}/scan-draft` | Save Scan Draft | save_scan_draft_api_warehouse_tasks__task_id__scan_draft_post |
| GET | `/api/inventory/replenishment-progress` | Replenishment Progress | replenishment_progress_api_inventory_replenishment_progress_get |
| GET | `/api/inventory/tasks` | List Inventory Tasks | list_inventory_tasks_api_inventory_tasks_get |
| POST | `/api/inventory/tasks/{task_id}/claim` | Claim Inventory Task | claim_inventory_task_api_inventory_tasks__task_id__claim_post |
| GET | `/api/inventory/recovery-shorts` | List Recovery Shorts | list_recovery_shorts_api_inventory_recovery_shorts_get |
| GET | `/api/inventory/stock-posting/source-availability` | Source Availability | source_availability_api_inventory_stock_posting_source_availability_get |
| GET | `/health` | Health | health_health_get |
| GET | `/db/ping` | Db Ping | db_ping_db_ping_get |
| POST | `/api/production-batches` | Create Production Batch | create_production_batch_api_production_batches_post |
| GET | `/api/production-batches/{prod_batch_id}/status` | Get Production Batch Status | get_production_batch_status_api_production_batches__prod_batch_id__status_get |
| POST | `/api/production-batches/{prod_batch_id}/pallets` | Attach Pallet | attach_pallet_api_production_batches__prod_batch_id__pallets_post |
| POST | `/api/raw-batches` | Create Raw Batch | create_raw_batch_api_raw_batches_post |
| GET | `/api/raw-batches/{raw_batch_id}` | Get Raw Batch | get_raw_batch_api_raw_batches__raw_batch_id__get |
| POST | `/api/production-batches/{prod_batch_id}/raw-usage` | Add Raw Usage | add_raw_usage_api_production_batches__prod_batch_id__raw_usage_post |
| POST | `/api/production-batches/{prod_batch_id}/crpt-codes` | Add Crpt Code | add_crpt_code_api_production_batches__prod_batch_id__crpt_codes_post |
| POST | `/api/production-batches/{prod_batch_id}/aggregations` | Create Aggregation | create_aggregation_api_production_batches__prod_batch_id__aggregations_post |
| POST | `/api/aggregations/{aggregation_id}/items` | Add Aggregation Item | add_aggregation_item_api_aggregations__aggregation_id__items_post |
| POST | `/api/production-batches/{prod_batch_id}/mercury` | Set Mercury Batch | set_mercury_batch_api_production_batches__prod_batch_id__mercury_post |
| GET | `/api/production-batches/{prod_batch_id}/regulatory-status` | Get Regulatory Status | get_regulatory_status_api_production_batches__prod_batch_id__regulatory_status_get |
| POST | `/api/regulatory/mercury-sites` | Upsert Mercury Site | upsert_mercury_site_api_regulatory_mercury_sites_post |
| GET | `/api/regulatory/mercury-sites` | List Mercury Sites | list_mercury_sites_api_regulatory_mercury_sites_get |
| POST | `/api/production-batches/{prod_batch_id}/mercury-operations` | Create Batch Mercury Operation | create_batch_mercury_operation_api_production_batches__prod_batch_id__mercury_operations_post |
| POST | `/api/mercury-operations` | Create Mercury Operation | create_mercury_operation_api_mercury_operations_post |
| PATCH | `/api/mercury-operations/{operation_row_id}` | Update Mercury Operation | update_mercury_operation_api_mercury_operations__operation_row_id__patch |
| POST | `/api/crpt-codes/status` | Set Crpt Code Status | set_crpt_code_status_api_crpt_codes_status_post |
| GET | `/api/regulatory/journal` | List Regulatory Journal | list_regulatory_journal_api_regulatory_journal_get |
| GET | `/api/regulatory/outbox` | List Regulatory Outbox | list_regulatory_outbox_api_regulatory_outbox_get |
| POST | `/api/legacy/tserver/execute` | Execute Legacy Tserver | execute_legacy_tserver_api_legacy_tserver_execute_post |
| GET | `/api/terminal/users/{user_id}` | Get Terminal User | get_terminal_user_api_terminal_users__user_id__get |
| GET | `/api/products/by-barcode/{barcode}` | Get Product By Barcode | get_product_by_barcode_api_products_by_barcode__barcode__get |
| GET | `/api/lots/{usscc}/items` | Get Lot Items | get_lot_items_api_lots__usscc__items_get |
| GET | `/api/places/{place_id}/items` | Get Place Items | get_place_items_api_places__place_id__items_get |
| POST | `/api/terminal/lots/{usscc}/check` | Confirm Lot Check | confirm_lot_check_api_terminal_lots__usscc__check_post |
| POST | `/api/terminal/place-checks` | Confirm Place Check | confirm_place_check_api_terminal_place_checks_post |
| POST | `/api/terminal/order-checks` | Confirm Order Check | confirm_order_check_api_terminal_order_checks_post |
| POST | `/api/terminal/call-spf` | Call Spf | call_spf_api_terminal_call_spf_post |
| GET | `/api/terminal/auth/me` | Terminal Identity | terminal_identity_api_terminal_auth_me_get |
| GET | `/api/admin/auth/login` | Login | login_api_admin_auth_login_get |
| GET | `/api/admin/auth/me` | Me | me_api_admin_auth_me_get |
| GET | `/api/admin/rights/users` | List Users | list_users_api_admin_rights_users_get |
| GET | `/api/admin/rights/groups` | List Groups | list_groups_api_admin_rights_groups_get |
| POST | `/api/admin/rights/groups` | Upsert Group | upsert_group_api_admin_rights_groups_post |
| GET | `/api/admin/rights/groups/{group_id}/rights` | List Group Rights | list_group_rights_api_admin_rights_groups__group_id__rights_get |
| POST | `/api/admin/rights/groups/{group_id}/rights` | Grant Group Right | grant_group_right_api_admin_rights_groups__group_id__rights_post |
| DELETE | `/api/admin/rights/groups/{group_id}/rights/{right_name}` | Revoke Group Right | revoke_group_right_api_admin_rights_groups__group_id__rights__right_name__delete |
| PUT | `/api/admin/rights/users/{user_id}/group` | Update User Group | update_user_group_api_admin_rights_users__user_id__group_put |
| GET | `/api/admin/api-calls` | List Api Calls | list_api_calls_api_admin_api_calls_get |
| GET | `/api/admin/api-calls/{api_call_id}` | Get Api Call | get_api_call_api_admin_api_calls__api_call_id__get |
| POST | `/api/admin/api-calls/replay` | Replay Api Calls | replay_api_calls_api_admin_api_calls_replay_post |
| GET | `/api/admin/slow-sql` | List Slow Sql | list_slow_sql_api_admin_slow_sql_get |
| GET | `/api/admin/slow-sql/top` | Top Slow Sql | top_slow_sql_api_admin_slow_sql_top_get |
| GET | `/api/admin/slow-sql/oracle-top` | Oracle Top Sql | oracle_top_sql_api_admin_slow_sql_oracle_top_get |
| GET | `/api/admin/slow-sql/{log_id}` | Get Slow Sql | get_slow_sql_api_admin_slow_sql__log_id__get |
| GET | `/api/trace/entities/{entity_type}/{entity_id}/forward` | Trace Forward | trace_forward_api_trace_entities__entity_type___entity_id__forward_get |
| GET | `/api/trace/entities/{entity_type}/{entity_id}/backward` | Trace Backward | trace_backward_api_trace_entities__entity_type___entity_id__backward_get |
| GET | `/api/admin/event-outbox` | List Event Outbox | list_event_outbox_api_admin_event_outbox_get |
| GET | `/api/admin/event-outbox/{event_outbox_id}` | Get Event Outbox | get_event_outbox_api_admin_event_outbox__event_outbox_id__get |
| POST | `/api/admin/event-outbox/{event_outbox_id}/retry` | Retry Event Outbox | retry_event_outbox_api_admin_event_outbox__event_outbox_id__retry_post |
| GET | `/api/admin/adapter-requests` | List Adapter Requests | list_adapter_requests_api_admin_adapter_requests_get |
| GET | `/api/admin/adapter-requests/{adapter_request_id}` | Get Adapter Request | get_adapter_request_api_admin_adapter_requests__adapter_request_id__get |
| GET | `/api/bom` | List Boms | list_boms_api_bom_get |
| POST | `/api/bom` | Create Bom | create_bom_api_bom_post |
| GET | `/api/bom/default` | Find Default Bom | find_default_bom_api_bom_default_get |
| GET | `/api/bom/{bom_id}` | Get Bom | get_bom_api_bom__bom_id__get |
| PATCH | `/api/bom/{bom_id}` | Update Bom | update_bom_api_bom__bom_id__patch |
| POST | `/api/bom/{bom_id}/lines` | Add Bom Line | add_bom_line_api_bom__bom_id__lines_post |
| PATCH | `/api/bom/{bom_id}/lines/{line_id}` | Update Bom Line | update_bom_line_api_bom__bom_id__lines__line_id__patch |
| DELETE | `/api/bom/{bom_id}/lines/{line_id}` | Delete Bom Line | delete_bom_line_api_bom__bom_id__lines__line_id__delete |
| POST | `/api/bom/{bom_id}/approve` | Approve Bom | approve_bom_api_bom__bom_id__approve_post |
| POST | `/api/bom/{bom_id}/block` | Block Bom | block_bom_api_bom__bom_id__block_post |
| POST | `/api/bom/{bom_id}/archive` | Archive Bom | archive_bom_api_bom__bom_id__archive_post |
| POST | `/api/bom/{bom_id}/make-primary` | Make Primary | make_primary_api_bom__bom_id__make_primary_post |
| POST | `/api/bom/{bom_id}/clone` | Clone Bom | clone_bom_api_bom__bom_id__clone_post |
| POST | `/api/bom/{bom_id}/calculate` | Calculate Bom | calculate_bom_api_bom__bom_id__calculate_post |
| GET | `/api/mes/production-orders` | List Production Orders | list_production_orders_api_mes_production_orders_get |
| POST | `/api/mes/production-orders` | Create Production Order | create_production_order_api_mes_production_orders_post |
| GET | `/api/mes/production-orders/{production_order_id}` | Get Production Order | get_production_order_api_mes_production_orders__production_order_id__get |
| POST | `/api/mes/production-orders/{production_order_id}/issue-raw` | Issue Raw | issue_raw_api_mes_production_orders__production_order_id__issue_raw_post |
| POST | `/api/mes/production-orders/{production_order_id}/complete` | Complete Order | complete_order_api_mes_production_orders__production_order_id__complete_post |
| POST | `/api/mes/production-orders/{production_order_id}/apply-wms` | Apply Wms | apply_wms_api_mes_production_orders__production_order_id__apply_wms_post |
| GET | `/api/mes/production-orders/{production_order_id}/genealogy` | Get Genealogy | get_genealogy_api_mes_production_orders__production_order_id__genealogy_get |
| POST | `/api/mes/production-orders/{production_order_id}/raw-supply/calculate` | Calculate Raw Supply | calculate_raw_supply_api_mes_production_orders__production_order_id__raw_supply_calculate_post |
| GET | `/api/mes/production-orders/{production_order_id}/raw-supply` | Get Raw Supply | get_raw_supply_api_mes_production_orders__production_order_id__raw_supply_get |
| POST | `/api/mes/production-orders/{production_order_id}/release-to-production` | Release To Production | release_to_production_api_mes_production_orders__production_order_id__release_to_production_post |
| GET | `/api/mes/raw-transfer-tasks` | List Raw Transfer Tasks | list_raw_transfer_tasks_api_mes_raw_transfer_tasks_get |
| GET | `/api/mes/raw-transfer-tasks/{task_id}` | Get Raw Transfer Task | get_raw_transfer_task_api_mes_raw_transfer_tasks__task_id__get |
| GET | `/api/mes/raw-shortages` | List Raw Shortages | list_raw_shortages_api_mes_raw_shortages_get |
| POST | `/api/mes/raw-transfer-tasks/{task_id}/confirm` | Confirm Raw Transfer Task | confirm_raw_transfer_task_api_mes_raw_transfer_tasks__task_id__confirm_post |
| POST | `/api/mes/raw-transfer-tasks/{task_id}/cancel` | Cancel Raw Transfer Task | cancel_raw_transfer_task_api_mes_raw_transfer_tasks__task_id__cancel_post |
| GET | `/api/mes/movements` | List Movements | list_movements_api_mes_movements_get |
| POST | `/api/mes/movements/{movement_id}/retry` | Retry Movement | retry_movement_api_mes_movements__movement_id__retry_post |
| GET | `/api/admin/warehouses` | List Warehouses | list_warehouses_api_admin_warehouses_get |
| PATCH | `/api/admin/warehouses/{ware_id}` | Update Warehouse | update_warehouse_api_admin_warehouses__ware_id__patch |
| GET | `/api/admin/product-shipment-settings` | List Product Shipment Settings | list_product_shipment_settings_api_admin_product_shipment_settings_get |
| PATCH | `/api/admin/product-shipment-settings/{articul}` | Update Product Shipment Settings | update_product_shipment_settings_api_admin_product_shipment_settings__articul__patch |
| GET | `/api/raw-material/skus` | List Raw Material Skus | list_raw_material_skus_api_raw_material_skus_get |
| PATCH | `/api/raw-material/skus/{articul}` | Update Raw Material Sku | update_raw_material_sku_api_raw_material_skus__articul__patch |
| GET | `/api/raw-material/warehouses` | List Raw Material Warehouses | list_raw_material_warehouses_api_raw_material_warehouses_get |
| GET | `/api/raw-material/remains` | List Raw Material Remains | list_raw_material_remains_api_raw_material_remains_get |
| GET | `/api/finished-goods/skus` | List Finished Goods Skus | list_finished_goods_skus_api_finished_goods_skus_get |
| PATCH | `/api/finished-goods/skus/{articul}` | Update Finished Goods Sku | update_finished_goods_sku_api_finished_goods_skus__articul__patch |
| GET | `/api/finished-goods/warehouses` | List Finished Goods Warehouses | list_finished_goods_warehouses_api_finished_goods_warehouses_get |
| GET | `/api/finished-goods/batches` | List Finished Goods Batches | list_finished_goods_batches_api_finished_goods_batches_get |
| GET | `/api/finished-goods/remains` | List Finished Goods Remains | list_finished_goods_remains_api_finished_goods_remains_get |
| GET | `/api/customers` | List Customers | list_customers_api_customers_get |
| POST | `/api/customers` | Create Customer | create_customer_api_customers_post |
| GET | `/api/customers/{customer_id}` | Get Customer | get_customer_api_customers__customer_id__get |
| PATCH | `/api/customers/{customer_id}` | Update Customer | update_customer_api_customers__customer_id__patch |
| POST | `/api/customers/{customer_id}/addresses` | Create Customer Address | create_customer_address_api_customers__customer_id__addresses_post |
| GET | `/api/customer-orders` | List Customer Orders | list_customer_orders_api_customer_orders_get |
| GET | `/api/customer-orders/{customer_order_id}` | Get Customer Order | get_customer_order_api_customer_orders__customer_order_id__get |
| POST | `/api/customer-orders/import-legacy/{legacy_order_id}` | Import Legacy Order | import_legacy_order_api_customer_orders_import_legacy__legacy_order_id__post |
| GET | `/api/customer-orders/{customer_order_id}/fulfillment` | Get Customer Order Fulfillment | get_customer_order_fulfillment_api_customer_orders__customer_order_id__fulfillment_get |
| GET | `/api/customers/{customer_id}/product-rules` | List Product Rules | list_product_rules_api_customers__customer_id__product_rules_get |
| POST | `/api/customers/{customer_id}/product-rules` | Create Product Rule | create_product_rule_api_customers__customer_id__product_rules_post |
| GET | `/api/customers/{customer_id}/shelf-life-rules` | List Shelf Life Rules | list_shelf_life_rules_api_customers__customer_id__shelf_life_rules_get |
| POST | `/api/customers/{customer_id}/shelf-life-rules` | Create Shelf Life Rule | create_shelf_life_rule_api_customers__customer_id__shelf_life_rules_post |
| GET | `/api/customers/{customer_id}/stack-rules` | List Stack Rules | list_stack_rules_api_customers__customer_id__stack_rules_get |
| POST | `/api/customers/{customer_id}/stack-rules` | Create Stack Rule | create_stack_rule_api_customers__customer_id__stack_rules_post |
| GET | `/api/customers/{customer_id}/vehicle-rules` | List Vehicle Rules | list_vehicle_rules_api_customers__customer_id__vehicle_rules_get |
| POST | `/api/customers/{customer_id}/vehicle-rules` | Create Vehicle Rule | create_vehicle_rule_api_customers__customer_id__vehicle_rules_post |
| GET | `/api/vehicle-types` | List Vehicle Types | list_vehicle_types_api_vehicle_types_get |
| POST | `/api/vehicle-types` | Create Vehicle Type | create_vehicle_type_api_vehicle_types_post |
| POST | `/api/picking/plans` | Create Picking Plan | create_picking_plan_api_picking_plans_post |
| GET | `/api/picking/plans` | List Picking Plans | list_picking_plans_api_picking_plans_get |
| GET | `/api/picking/plans/{pick_plan_id}` | Get Picking Plan | get_picking_plan_api_picking_plans__pick_plan_id__get |
| POST | `/api/picking/plans/{pick_plan_id}/cancel` | Cancel Picking Plan | cancel_picking_plan_api_picking_plans__pick_plan_id__cancel_post |
| GET | `/api/picking/reservations` | List Picking Reservations | list_picking_reservations_api_picking_reservations_get |
| GET | `/api/picking/shortages` | List Picking Shortages | list_picking_shortages_api_picking_shortages_get |
| GET | `/api/picking/plans/{pick_plan_id}/shortages` | List Picking Plan Shortages | list_picking_plan_shortages_api_picking_plans__pick_plan_id__shortages_get |
| GET | `/api/picking/waves` | List Pick Waves | list_pick_waves_api_picking_waves_get |
| POST | `/api/picking/waves` | Create Pick Wave | create_pick_wave_api_picking_waves_post |
| GET | `/api/picking/waves/candidates` | List Pick Wave Candidates | list_pick_wave_candidates_api_picking_waves_candidates_get |
| GET | `/api/picking/waves/{pick_wave_id}/header` | Get Pick Wave Header | get_pick_wave_header_api_picking_waves__pick_wave_id__header_get |
| GET | `/api/picking/waves/{pick_wave_id}` | Get Pick Wave | get_pick_wave_api_picking_waves__pick_wave_id__get |
| GET | `/api/picking/waves/{pick_wave_id}/readiness` | Get Pick Wave Readiness | get_pick_wave_readiness_api_picking_waves__pick_wave_id__readiness_get |
| POST | `/api/picking/waves/{pick_wave_id}/plans` | Add Pick Wave Plan | add_pick_wave_plan_api_picking_waves__pick_wave_id__plans_post |
| POST | `/api/picking/waves/{pick_wave_id}/calculate` | Calculate Pick Wave | calculate_pick_wave_api_picking_waves__pick_wave_id__calculate_post |
| POST | `/api/picking/waves/{pick_wave_id}/launch` | Launch Pick Wave | launch_pick_wave_api_picking_waves__pick_wave_id__launch_post |
| POST | `/api/picking/waves/{pick_wave_id}/cancel` | Cancel Pick Wave | cancel_pick_wave_api_picking_waves__pick_wave_id__cancel_post |
| POST | `/api/picking/waves/{pick_wave_id}/release-reservations` | Release Pick Wave Reservations | release_pick_wave_reservations_api_picking_waves__pick_wave_id__release_reservations_post |
| POST | `/api/picking/waves/{pick_wave_id}/replenishment/minimax-check` | Release Pick Wave Minimax Replenishment | release_pick_wave_minimax_replenishment_api_picking_waves__pick_wave_id__replenishment_minimax_check_post |
| POST | `/api/picking/waves/{pick_wave_id}/staging/release` | Release Pick Wave Staging | release_pick_wave_staging_api_picking_waves__pick_wave_id__staging_release_post |
| GET | `/api/picking/waves/{pick_wave_id}/reservations` | List Pick Wave Reservations | list_pick_wave_reservations_api_picking_waves__pick_wave_id__reservations_get |
| GET | `/api/picking/waves/{pick_wave_id}/replenishment-tasks` | List Pick Wave Replenishment Tasks | list_pick_wave_replenishment_tasks_api_picking_waves__pick_wave_id__replenishment_tasks_get |
| GET | `/api/picking/waves/{pick_wave_id}/tasks` | List Pick Wave Tasks | list_pick_wave_tasks_api_picking_waves__pick_wave_id__tasks_get |
| POST | `/api/picking/waves/{pick_wave_id}/tasks/{pick_task_id}/complete` | Complete Pick Wave Task | complete_pick_wave_task_api_picking_waves__pick_wave_id__tasks__pick_task_id__complete_post |
| GET | `/api/picking/waves/{pick_wave_id}/audit` | List Pick Wave Audit | list_pick_wave_audit_api_picking_waves__pick_wave_id__audit_get |
| GET | `/api/picking/routes` | List Pick Routes | list_pick_routes_api_picking_routes_get |
| POST | `/api/picking/routes` | Upsert Pick Route | upsert_pick_route_api_picking_routes_post |
| GET | `/api/picking/route-cells` | List Pick Route Cells | list_pick_route_cells_api_picking_route_cells_get |
| POST | `/api/picking/route-cells` | Upsert Pick Route Cell | upsert_pick_route_cell_api_picking_route_cells_post |
| GET | `/api/picking/pick-faces` | List Pick Faces | list_pick_faces_api_picking_pick_faces_get |
| POST | `/api/picking/pick-faces` | Upsert Pick Face | upsert_pick_face_api_picking_pick_faces_post |
| GET | `/api/picking/pick-faces/{pick_face_id}/articuls` | List Pick Face Articuls | list_pick_face_articuls_api_picking_pick_faces__pick_face_id__articuls_get |
| POST | `/api/picking/pick-faces/{pick_face_id}/articuls` | Assign Pick Face Articul | assign_pick_face_articul_api_picking_pick_faces__pick_face_id__articuls_post |
| GET | `/api/picking/articul-replenishment-rules` | List Articul Replenishment Rules | list_articul_replenishment_rules_api_picking_articul_replenishment_rules_get |
| POST | `/api/picking/articul-replenishment-rules` | Upsert Articul Replenishment Rule | upsert_articul_replenishment_rule_api_picking_articul_replenishment_rules_post |
| POST | `/api/case-pick/waves/{pick_wave_id}/ensure` | Ensure Wave Case Pick Tasks | ensure_wave_case_pick_tasks_api_case_pick_waves__pick_wave_id__ensure_post |
| GET | `/api/case-pick/tasks` | List Case Pick Tasks | list_case_pick_tasks_api_case_pick_tasks_get |
| GET | `/api/case-pick/tasks/{case_pick_task_id}` | Get Case Pick Task | get_case_pick_task_api_case_pick_tasks__case_pick_task_id__get |
| POST | `/api/case-pick/tasks/{case_pick_task_id}/claim` | Claim Case Pick Task | claim_case_pick_task_api_case_pick_tasks__case_pick_task_id__claim_post |
| POST | `/api/case-pick/tasks/{case_pick_task_id}/start` | Start Case Pick Task | start_case_pick_task_api_case_pick_tasks__case_pick_task_id__start_post |
| POST | `/api/case-pick/tasks/{case_pick_task_id}/transfer` | Transfer Case Pick Task | transfer_case_pick_task_api_case_pick_tasks__case_pick_task_id__transfer_post |
| POST | `/api/case-pick/tasks/{case_pick_task_id}/move-carrier` | Move Case Carrier | move_case_carrier_api_case_pick_tasks__case_pick_task_id__move_carrier_post |
| GET | `/api/case-pick/tasks/{case_pick_task_id}/lines/{line_id}/marking-policy` | Case Line Marking Policy | case_line_marking_policy_api_case_pick_tasks__case_pick_task_id__lines__line_id__marking_policy_get |
| POST | `/api/case-pick/tasks/{case_pick_task_id}/lines/{line_id}/confirm` | Confirm Case Pick Line | confirm_case_pick_line_api_case_pick_tasks__case_pick_task_id__lines__line_id__confirm_post |
| POST | `/api/case-pick/tasks/{case_pick_task_id}/lines/{line_id}/short` | Create Case Pick Short | create_case_pick_short_api_case_pick_tasks__case_pick_task_id__lines__line_id__short_post |
| POST | `/api/case-pick/tasks/{case_pick_task_id}/close-pallet` | Close Case Pick Task | close_case_pick_task_api_case_pick_tasks__case_pick_task_id__close_pallet_post |
| GET | `/api/case-pick/shorts` | List Case Pick Shorts | list_case_pick_shorts_api_case_pick_shorts_get |
| POST | `/api/case-pick/shorts/{short_id}/approve` | Approve Case Pick Short | approve_case_pick_short_api_case_pick_shorts__short_id__approve_post |
| POST | `/api/case-pick/shorts/{short_id}/reject` | Reject Case Pick Short | reject_case_pick_short_api_case_pick_shorts__short_id__reject_post |
| GET | `/api/case-pick/pallet-types` | List Pallet Types | list_pallet_types_api_case_pick_pallet_types_get |
| POST | `/api/case-pick/pallet-types` | Upsert Pallet Type | upsert_pallet_type_api_case_pick_pallet_types_post |
| POST | `/api/case-pick/tasks/{case_pick_task_id}/bind-shipment` | Bind Case Shipment | bind_case_shipment_api_case_pick_tasks__case_pick_task_id__bind_shipment_post |
| POST | `/api/case-pick/tasks/{case_pick_task_id}/return-carrier` | Return Case Carrier | return_case_carrier_api_case_pick_tasks__case_pick_task_id__return_carrier_post |
| POST | `/api/case-pick/tasks/{task}/lines/{line}/weighted-box` | Confirm Weighted Box | confirm_weighted_box_api_case_pick_tasks__task__lines__line__weighted_box_post |
| POST | `/api/case-pick/tasks/{task}/lines/{line}/weigh-line` | Confirm Weighed Line | confirm_weighed_line_api_case_pick_tasks__task__lines__line__weigh_line_post |
| GET | `/api/case-pick/tasks/{task}/lines/{line}/order-weight-preview` | Order Weight Preview | order_weight_preview_api_case_pick_tasks__task__lines__line__order_weight_preview_get |
| GET | `/api/case-pick/shorts/{short}/weight-preview` | Short Weight Preview | short_weight_preview_api_case_pick_shorts__short__weight_preview_get |
| GET | `/api/picking/order-rows/{row}/weighted-box-options` | Weighted Box Options | weighted_box_options_api_picking_order_rows__row__weighted_box_options_get |
| GET | `/api/picking/order-rows/{row}/weighted-box-approval-preview` | Weighted Box Approval Preview | weighted_box_approval_preview_api_picking_order_rows__row__weighted_box_approval_preview_get |
| POST | `/api/picking/weighted-box-choices` | Approve Weighted Box | approve_weighted_box_api_picking_weighted_box_choices_post |
| POST | `/api/picking/weighted-box-choices/{choice}/cancel` | Cancel Weighted Box | cancel_weighted_box_api_picking_weighted_box_choices__choice__cancel_post |
| PUT | `/api/inventory/warehouse-scales/devices/{device}` | Configure | configure_api_inventory_warehouse_scales_devices__device__put |
| POST | `/api/inventory/warehouse-scales/captures` | Capture | capture_api_inventory_warehouse_scales_captures_post |
| GET | `/api/inventory/warehouse-scales/captures` | Readings | readings_api_inventory_warehouse_scales_captures_get |
| GET | `/api/inventory/warehouse-scales/captures/{key}` | Reading | reading_api_inventory_warehouse_scales_captures__key__get |
| POST | `/api/inventory/warehouse-scales/final-captures` | Final Capture | final_capture_api_inventory_warehouse_scales_final_captures_post |
| GET | `/api/inventory/warehouse-scales/final-captures` | Final Readings | final_readings_api_inventory_warehouse_scales_final_captures_get |
| GET | `/api/stock-reservations` | List Stock Reservations | list_stock_reservations_api_stock_reservations_get |
| POST | `/api/stock-reservations` | Create Stock Reservation | create_stock_reservation_api_stock_reservations_post |
| GET | `/api/stock-reservations/{reservation_id}` | Get Stock Reservation | get_stock_reservation_api_stock_reservations__reservation_id__get |
| POST | `/api/stock-reservations/{reservation_id}/promote-to-hard` | Promote Stock Reservation To Hard | promote_stock_reservation_to_hard_api_stock_reservations__reservation_id__promote_to_hard_post |
| POST | `/api/stock-reservations/{reservation_id}/release` | Release Stock Reservation | release_stock_reservation_api_stock_reservations__reservation_id__release_post |
| POST | `/api/stock-reservations/{reservation_id}/consume` | Consume Stock Reservation | consume_stock_reservation_api_stock_reservations__reservation_id__consume_post |
| POST | `/api/stock-reservations/{reservation_id}/cancel` | Cancel Stock Reservation | cancel_stock_reservation_api_stock_reservations__reservation_id__cancel_post |
| GET | `/api/warehouse-tasks` | List Warehouse Tasks | list_warehouse_tasks_api_warehouse_tasks_get |
| GET | `/api/warehouse-tasks/domain-sync` | List Warehouse Task Sync | list_warehouse_task_sync_api_warehouse_tasks_domain_sync_get |
| GET | `/api/warehouse-tasks/{task_id}` | Get Warehouse Task | get_warehouse_task_api_warehouse_tasks__task_id__get |
| GET | `/api/warehouse-tasks/{task_id}/progress` | Get Warehouse Task Progress | get_warehouse_task_progress_api_warehouse_tasks__task_id__progress_get |
| GET | `/api/warehouse-tasks/{task_id}/sync` | Get Warehouse Task Sync | get_warehouse_task_sync_api_warehouse_tasks__task_id__sync_get |
| POST | `/api/warehouse-tasks/{task_id}/assign` | Assign Warehouse Task | assign_warehouse_task_api_warehouse_tasks__task_id__assign_post |
| POST | `/api/warehouse-tasks/{task_id}/start` | Start Warehouse Task | start_warehouse_task_api_warehouse_tasks__task_id__start_post |
| POST | `/api/warehouse-tasks/{task_id}/complete` | Complete Warehouse Task | complete_warehouse_task_api_warehouse_tasks__task_id__complete_post |
| POST | `/api/warehouse-tasks/{task_id}/sync/retry` | Retry Warehouse Task Sync | retry_warehouse_task_sync_api_warehouse_tasks__task_id__sync_retry_post |
| POST | `/api/warehouse-tasks/{task_id}/cancel` | Cancel Warehouse Task | cancel_warehouse_task_api_warehouse_tasks__task_id__cancel_post |
| GET | `/api/resources/types` | List Resource Types | list_resource_types_api_resources_types_get |
| GET | `/api/resources/equipment` | List Equipment | list_equipment_api_resources_equipment_get |
| POST | `/api/resources/equipment` | Create Equipment | create_equipment_api_resources_equipment_post |
| GET | `/api/resources` | List Resources | list_resources_api_resources_get |
| POST | `/api/resources` | Create Resource | create_resource_api_resources_post |
| GET | `/api/resources/shifts` | List Shifts | list_shifts_api_resources_shifts_get |
| POST | `/api/resources/shifts` | Create Shift | create_shift_api_resources_shifts_post |
| GET | `/api/resources/sessions` | List Sessions | list_sessions_api_resources_sessions_get |
| POST | `/api/resources/sessions/login` | Login Session | login_session_api_resources_sessions_login_post |
| POST | `/api/resources/sessions/tsd-login` | Login Tsd Session | login_tsd_session_api_resources_sessions_tsd_login_post |
| POST | `/api/resources/sessions/{session_id}/heartbeat` | Heartbeat Session | heartbeat_session_api_resources_sessions__session_id__heartbeat_post |
| POST | `/api/resources/sessions/{session_id}/pause` | Pause Session | pause_session_api_resources_sessions__session_id__pause_post |
| POST | `/api/resources/sessions/{session_id}/resume` | Resume Session | resume_session_api_resources_sessions__session_id__resume_post |
| POST | `/api/resources/sessions/{session_id}/logout` | Logout Session | logout_session_api_resources_sessions__session_id__logout_post |
| GET | `/api/admin/warehouse-map-drafts` | List Warehouse Map Drafts | list_warehouse_map_drafts_api_admin_warehouse_map_drafts_get |
| POST | `/api/admin/warehouse-map-drafts` | Create Warehouse Map Draft | create_warehouse_map_draft_api_admin_warehouse_map_drafts_post |
| POST | `/api/admin/warehouse-map-drafts/load-from-db` | Load Warehouse Map Draft From Db | load_warehouse_map_draft_from_db_api_admin_warehouse_map_drafts_load_from_db_post |
| GET | `/api/admin/warehouse-map-drafts/{draft_id}` | Get Warehouse Map Draft | get_warehouse_map_draft_api_admin_warehouse_map_drafts__draft_id__get |
| PATCH | `/api/admin/warehouse-map-drafts/{draft_id}/cells` | Patch Warehouse Map Draft Cells | patch_warehouse_map_draft_cells_api_admin_warehouse_map_drafts__draft_id__cells_patch |
| GET | `/api/admin/warehouse-map-drafts/{draft_id}/diff` | Get Warehouse Map Draft Diff | get_warehouse_map_draft_diff_api_admin_warehouse_map_drafts__draft_id__diff_get |
| POST | `/api/admin/warehouse-map-drafts/{draft_id}/save-to-db` | Save Warehouse Map Draft To Db | save_warehouse_map_draft_to_db_api_admin_warehouse_map_drafts__draft_id__save_to_db_post |
| PATCH | `/api/admin/warehouse-map-drafts/{draft_id}/metadata` | Patch Warehouse Map Draft Metadata | patch_warehouse_map_draft_metadata_api_admin_warehouse_map_drafts__draft_id__metadata_patch |
| POST | `/api/admin/warehouse-map-drafts/{draft_id}/route/build` | Build Warehouse Map Draft Route | build_warehouse_map_draft_route_api_admin_warehouse_map_drafts__draft_id__route_build_post |
| PATCH | `/api/admin/warehouse-map-drafts/{draft_id}/route` | Patch Warehouse Map Draft Route | patch_warehouse_map_draft_route_api_admin_warehouse_map_drafts__draft_id__route_patch |
| POST | `/api/admin/warehouse-map-drafts/{draft_id}/route/save-to-db` | Save Warehouse Map Draft Route To Db | save_warehouse_map_draft_route_to_db_api_admin_warehouse_map_drafts__draft_id__route_save_to_db_post |
| POST | `/api/admin/warehouse-map-drafts/{draft_id}/publish-oracle` | Publish Warehouse Map Draft To Oracle | publish_warehouse_map_draft_to_oracle_api_admin_warehouse_map_drafts__draft_id__publish_oracle_post |
| POST | `/api/admin/warehouse-map-drafts/{draft_id}/bulk-role` | Apply Warehouse Map Bulk Role | apply_warehouse_map_bulk_role_api_admin_warehouse_map_drafts__draft_id__bulk_role_post |
| POST | `/api/admin/warehouse-map-drafts/{draft_id}/pick-face-addresses/generate` | Generate Warehouse Map Pick Face Addresses | generate_warehouse_map_pick_face_addresses_api_admin_warehouse_map_drafts__draft_id__pick_face_addresses_generate_post |
| POST | `/api/admin/warehouse-map-drafts/{draft_id}/small-pick-faces/generate` | Generate Warehouse Map Small Pick Faces | generate_warehouse_map_small_pick_faces_api_admin_warehouse_map_drafts__draft_id__small_pick_faces_generate_post |
| PATCH | `/api/admin/warehouse-map-drafts/{draft_id}/small-pick-faces/{small_pick_face_id}` | Patch Warehouse Map Small Pick Face | patch_warehouse_map_small_pick_face_api_admin_warehouse_map_drafts__draft_id__small_pick_faces__small_pick_face_id__patch |
| POST | `/api/admin/warehouse-map-drafts/{draft_id}/small-pick-faces/renumber` | Renumber Warehouse Map Small Pick Faces | renumber_warehouse_map_small_pick_faces_api_admin_warehouse_map_drafts__draft_id__small_pick_faces_renumber_post |
| POST | `/api/admin/warehouse-map-drafts/{draft_id}/storage-slots/generate` | Generate Warehouse Map Storage Slots | generate_warehouse_map_storage_slots_api_admin_warehouse_map_drafts__draft_id__storage_slots_generate_post |
| PATCH | `/api/admin/warehouse-map-drafts/{draft_id}/storage-slots/{storage_slot_id}` | Patch Warehouse Map Storage Slot | patch_warehouse_map_storage_slot_api_admin_warehouse_map_drafts__draft_id__storage_slots__storage_slot_id__patch |
| POST | `/api/admin/warehouse-map-drafts/{draft_id}/validate` | Validate Warehouse Map Draft | validate_warehouse_map_draft_api_admin_warehouse_map_drafts__draft_id__validate_post |
| POST | `/api/admin/warehouse-map-drafts/{draft_id}/projection/preview` | Preview Warehouse Map Draft Projection | preview_warehouse_map_draft_projection_api_admin_warehouse_map_drafts__draft_id__projection_preview_post |
| POST | `/api/admin/warehouse-map-drafts/{draft_id}/projection/save-to-topology` | Save Warehouse Map Draft Projection To Topology | save_warehouse_map_draft_projection_to_topology_api_admin_warehouse_map_drafts__draft_id__projection_save_to_topology_post |
| POST | `/api/admin/warehouse-map-drafts/{draft_id}/publish` | Publish Warehouse Map Draft | publish_warehouse_map_draft_api_admin_warehouse_map_drafts__draft_id__publish_post |
| GET | `/api/admin/warehouse-map/warehouses/{ware_id}/canvases` | List Warehouse Map Canvases | list_warehouse_map_canvases_api_admin_warehouse_map_warehouses__ware_id__canvases_get |
| POST | `/api/admin/warehouse-map/warehouses/{ware_id}/canvases` | Create Warehouse Map Canvas | create_warehouse_map_canvas_api_admin_warehouse_map_warehouses__ware_id__canvases_post |
| GET | `/api/admin/warehouse-map/warehouses/{ware_id}/state` | Get Warehouse Map State | get_warehouse_map_state_api_admin_warehouse_map_warehouses__ware_id__state_get |
| GET | `/api/admin/warehouse-map/canvases/{canvas_id}` | Get Warehouse Map Canvas State | get_warehouse_map_canvas_state_api_admin_warehouse_map_canvases__canvas_id__get |
| POST | `/api/admin/warehouse-map/canvases/{canvas_id}/archive` | Archive Warehouse Map Canvas | archive_warehouse_map_canvas_api_admin_warehouse_map_canvases__canvas_id__archive_post |
| POST | `/api/admin/warehouse-map/canvases/{canvas_id}/cameras` | Create Warehouse Map Camera | create_warehouse_map_camera_api_admin_warehouse_map_canvases__canvas_id__cameras_post |
| POST | `/api/admin/warehouse-map/cameras/{camera_id}/clone` | Clone Warehouse Map Camera | clone_warehouse_map_camera_api_admin_warehouse_map_cameras__camera_id__clone_post |
| POST | `/api/admin/warehouse-map/cameras/{camera_id}/archive` | Archive Warehouse Map Camera | archive_warehouse_map_camera_api_admin_warehouse_map_cameras__camera_id__archive_post |
| PATCH | `/api/admin/warehouse-map/cameras/{camera_id}/objects` | Patch Warehouse Map Camera Objects | patch_warehouse_map_camera_objects_api_admin_warehouse_map_cameras__camera_id__objects_patch |
| PATCH | `/api/admin/warehouse-map/cameras/{camera_id}/passages` | Patch Warehouse Map Camera Passages | patch_warehouse_map_camera_passages_api_admin_warehouse_map_cameras__camera_id__passages_patch |
| PATCH | `/api/admin/warehouse-map/canvases/{canvas_id}/camera-links` | Patch Warehouse Map Camera Links | patch_warehouse_map_camera_links_api_admin_warehouse_map_canvases__canvas_id__camera_links_patch |
| GET | `/api/admin/warehouse-topologies` | List Topologies | list_topologies_api_admin_warehouse_topologies_get |
| POST | `/api/admin/warehouse-topologies` | Create Topology | create_topology_api_admin_warehouse_topologies_post |
| GET | `/api/admin/warehouse-topologies/{topology_id}/map` | Get Topology Map | get_topology_map_api_admin_warehouse_topologies__topology_id__map_get |
| POST | `/api/admin/warehouse-topologies/{topology_id}/generate-cells` | Generate Cells | generate_cells_api_admin_warehouse_topologies__topology_id__generate_cells_post |
| POST | `/api/admin/warehouse-topologies/{topology_id}/generate-gates` | Generate Gates | generate_gates_api_admin_warehouse_topologies__topology_id__generate_gates_post |
| POST | `/api/admin/warehouse-topologies/{topology_id}/distances/recalculate` | Recalculate Gate Distances | recalculate_gate_distances_api_admin_warehouse_topologies__topology_id__distances_recalculate_post |
| POST | `/api/admin/warehouse-topologies/{topology_id}/validate` | Validate Topology | validate_topology_api_admin_warehouse_topologies__topology_id__validate_post |
| POST | `/api/admin/warehouse-topologies/{topology_id}/normalize-cell-codes` | Normalize Topology Cell Codes | normalize_topology_cell_codes_api_admin_warehouse_topologies__topology_id__normalize_cell_codes_post |
| POST | `/api/admin/warehouse-topologies/{topology_id}/publish` | Publish Topology | publish_topology_api_admin_warehouse_topologies__topology_id__publish_post |
| PATCH | `/api/admin/topology-cells/{topology_cell_id}` | Patch Topology Cell | patch_topology_cell_api_admin_topology_cells__topology_cell_id__patch |
| GET | `/api/admin/pick-routes` | List Admin Pick Routes | list_admin_pick_routes_api_admin_pick_routes_get |
| POST | `/api/admin/pick-routes/build` | Build Pick Route | build_pick_route_api_admin_pick_routes_build_post |
| POST | `/api/admin/pick-routes/{pick_route_id}/publish` | Publish Pick Route | publish_pick_route_api_admin_pick_routes__pick_route_id__publish_post |
| GET | `/api/admin/transport/vehicles` | List Vehicles | list_vehicles_api_admin_transport_vehicles_get |
| POST | `/api/admin/transport/vehicles` | Create Vehicle | create_vehicle_api_admin_transport_vehicles_post |
| GET | `/api/admin/transport/vehicles/full` | List Vehicles Full | list_vehicles_full_api_admin_transport_vehicles_full_get |
| PATCH | `/api/admin/transport/vehicles/{vehicle_id}` | Update Vehicle | update_vehicle_api_admin_transport_vehicles__vehicle_id__patch |
| DELETE | `/api/admin/transport/vehicles/{vehicle_id}` | Delete Vehicle | delete_vehicle_api_admin_transport_vehicles__vehicle_id__delete |
| GET | `/api/admin/transport/drivers` | List Drivers | list_drivers_api_admin_transport_drivers_get |
| POST | `/api/admin/transport/drivers` | Create Driver | create_driver_api_admin_transport_drivers_post |
| GET | `/api/admin/transport/drivers/full` | List Drivers Full | list_drivers_full_api_admin_transport_drivers_full_get |
| PATCH | `/api/admin/transport/drivers/{driver_id}` | Update Driver | update_driver_api_admin_transport_drivers__driver_id__patch |
| DELETE | `/api/admin/transport/drivers/{driver_id}` | Delete Driver | delete_driver_api_admin_transport_drivers__driver_id__delete |
| GET | `/api/admin/transport/types` | List Transport Types | list_transport_types_api_admin_transport_types_get |
| GET | `/api/admin/transport/available-sts` | List Available Sts | list_available_sts_api_admin_transport_available_sts_get |
| GET | `/api/admin/transport/clusters` | List Clusters | list_clusters_api_admin_transport_clusters_get |
| POST | `/api/admin/transport/clusters/{raion}/create-task` | Create Task From Cluster | create_task_from_cluster_api_admin_transport_clusters__raion__create_task_post |
| GET | `/api/admin/transport/tasks/export.xlsx` | Export Tasks Xlsx | export_tasks_xlsx_api_admin_transport_tasks_export_xlsx_get |
| GET | `/api/admin/transport/tasks` | List Tasks | list_tasks_api_admin_transport_tasks_get |
| POST | `/api/admin/transport/tasks` | Create Task | create_task_api_admin_transport_tasks_post |
| GET | `/api/admin/transport/tasks/{task_id}` | Get Task | get_task_api_admin_transport_tasks__task_id__get |
| PATCH | `/api/admin/transport/tasks/{task_id}` | Update Task | update_task_api_admin_transport_tasks__task_id__patch |
| POST | `/api/admin/transport/tasks/{task_id}/close` | Close Task | close_task_api_admin_transport_tasks__task_id__close_post |
| POST | `/api/admin/transport/tasks/{task_id}/cancel` | Cancel Task | cancel_task_api_admin_transport_tasks__task_id__cancel_post |
| GET | `/api/admin/transport/tasks/{task_id}/sts` | Get Task Sts | get_task_sts_api_admin_transport_tasks__task_id__sts_get |
| POST | `/api/admin/transport/tasks/{task_id}/sts` | Assign Sts | assign_sts_api_admin_transport_tasks__task_id__sts_post |
| DELETE | `/api/admin/transport/tasks/{task_id}/sts/{st_number}` | Unassign St | unassign_st_api_admin_transport_tasks__task_id__sts__st_number__delete |
| PATCH | `/api/admin/transport/tasks/{task_id}/sts/{st_number}/load-type` | Set St Load Type | set_st_load_type_api_admin_transport_tasks__task_id__sts__st_number__load_type_patch |
| PATCH | `/api/admin/transport/tasks/{task_id}/sts/{st_number}/order` | Set St Order | set_st_order_api_admin_transport_tasks__task_id__sts__st_number__order_patch |
| GET | `/api/admin/transport/sts/{st_number}/pallets` | List St Pallets | list_st_pallets_api_admin_transport_sts__st_number__pallets_get |
| GET | `/api/admin/transport/planner/orders` | Get Planner Orders | get_planner_orders_api_admin_transport_planner_orders_get |
| GET | `/api/admin/transport/routing/status` | Get Routing Status | get_routing_status_api_admin_transport_routing_status_get |
| POST | `/api/admin/transport/distance-matrix/rebuild` | Rebuild Distance Matrix | rebuild_distance_matrix_api_admin_transport_distance_matrix_rebuild_post |
| POST | `/api/admin/transport/planner/solve` | Solve Vrp | solve_vrp_api_admin_transport_planner_solve_post |
| GET | `/api/admin/transport/planner/solve/{job_id}/stream` | Stream Vrp Job | stream_vrp_job_api_admin_transport_planner_solve__job_id__stream_get |
| DELETE | `/api/admin/transport/planner/solve/{job_id}` | Cancel Vrp Job | cancel_vrp_job_api_admin_transport_planner_solve__job_id__delete |
| POST | `/api/admin/transport/planner/apply` | Apply Vrp Plan | apply_vrp_plan_api_admin_transport_planner_apply_post |
| GET | `/api/admin/transport/planner/metrics` | Get Planner Metrics | get_planner_metrics_api_admin_transport_planner_metrics_get |
| GET | `/api/admin/transport/planner/templates` | Get Planner Templates | get_planner_templates_api_admin_transport_planner_templates_get |
| GET | `/api/admin/transport/planner/history` | Get Planner History | get_planner_history_api_admin_transport_planner_history_get |
| GET | `/api/admin/transport/planner/demand-forecast` | Get Demand Forecast | get_demand_forecast_api_admin_transport_planner_demand_forecast_get |
| POST | `/api/admin/transport/tasks/{task_id}/plan-operations` | Plan Operations | plan_operations_api_admin_transport_tasks__task_id__plan_operations_post |
| GET | `/api/admin/transport/tasks/{task_id}/operations` | Get Operations | get_operations_api_admin_transport_tasks__task_id__operations_get |
| GET | `/api/admin/transport/vehicles/gantt` | Get Vehicles Gantt | get_vehicles_gantt_api_admin_transport_vehicles_gantt_get |
| GET | `/api/admin/transport/vehicles/available` | Get Vehicles Available | get_vehicles_available_api_admin_transport_vehicles_available_get |
| GET | `/api/admin/transport/plan-fact` | Get Plan Fact | get_plan_fact_api_admin_transport_plan_fact_get |
| GET | `/api/admin/transport/billing/orders` | List Billing Orders | list_billing_orders_api_admin_transport_billing_orders_get |
| POST | `/api/admin/transport/billing/orders` | Create Billing Order | create_billing_order_api_admin_transport_billing_orders_post |
| GET | `/api/admin/transport/billing/orders/export.xlsx` | Export Billing Registry Xlsx | export_billing_registry_xlsx_api_admin_transport_billing_orders_export_xlsx_get |
| GET | `/api/admin/transport/billing/orders/{order_id}` | Get Billing Order | get_billing_order_api_admin_transport_billing_orders__order_id__get |
| PATCH | `/api/admin/transport/billing/orders/{order_id}/close` | Close Billing Order | close_billing_order_api_admin_transport_billing_orders__order_id__close_patch |
| PATCH | `/api/admin/transport/billing/orders/{order_id}/pay` | Pay Billing Order | pay_billing_order_api_admin_transport_billing_orders__order_id__pay_patch |
| GET | `/api/admin/transport/billing/orders/{order_id}/tasks` | Get Billing Order Tasks | get_billing_order_tasks_api_admin_transport_billing_orders__order_id__tasks_get |
| POST | `/api/admin/transport/billing/orders/{order_id}/tasks` | Add Tasks To Billing Order | add_tasks_to_billing_order_api_admin_transport_billing_orders__order_id__tasks_post |
| GET | `/api/admin/transport/billing/orders/{order_id}/export.xlsx` | Export Billing Order Xlsx | export_billing_order_xlsx_api_admin_transport_billing_orders__order_id__export_xlsx_get |
| GET | `/api/admin/transport/tasks/{task_id}/billing` | Get Task Billing | get_task_billing_api_admin_transport_tasks__task_id__billing_get |
| POST | `/api/admin/transport/tasks/{task_id}/billing/open` | Open Billing For Task | open_billing_for_task_api_admin_transport_tasks__task_id__billing_open_post |
| DELETE | `/api/admin/transport/billing/orders/{order_id}/tasks/{tt_id}` | Remove Task From Billing Order | remove_task_from_billing_order_api_admin_transport_billing_orders__order_id__tasks__tt_id__delete |
| POST | `/api/admin/transport/tasks/{task_id}/recalculate-price` | Recalculate Task Price | recalculate_task_price_api_admin_transport_tasks__task_id__recalculate_price_post |
| PATCH | `/api/admin/transport/tasks/{task_id}/price` | Set Task Price | set_task_price_api_admin_transport_tasks__task_id__price_patch |
| GET | `/api/admin/transport/billing/companies` | List Billing Companies | list_billing_companies_api_admin_transport_billing_companies_get |
| GET | `/api/admin/transport/ws/status` | Ws Status | ws_status_api_admin_transport_ws_status_get |
| GET | `/api/admin/users` | List Users | list_users_api_admin_users_get |
| POST | `/api/admin/users` | Create User | create_user_api_admin_users_post |
| GET | `/api/admin/users/groups` | List Groups | list_groups_api_admin_users_groups_get |
| POST | `/api/admin/users/groups` | Create Group | create_group_api_admin_users_groups_post |
| GET | `/api/admin/users/rights` | List All Rights | list_all_rights_api_admin_users_rights_get |
| PATCH | `/api/admin/users/{login}` | Update User | update_user_api_admin_users__login__patch |
| DELETE | `/api/admin/users/{login}` | Delete User | delete_user_api_admin_users__login__delete |
| PATCH | `/api/admin/users/{login}/password` | Set Password | set_password_api_admin_users__login__password_patch |
| POST | `/api/admin/users/groups/{group}/rights` | Add Group Right | add_group_right_api_admin_users_groups__group__rights_post |
| DELETE | `/api/admin/users/groups/{group}/rights/{right}` | Remove Group Right | remove_group_right_api_admin_users_groups__group__rights__right__delete |
| GET | `/api/driver/trips` | Trips | trips_api_driver_trips_get |
| GET | `/api/driver/trips/{task_id}/sts` | Stops | stops_api_driver_trips__task_id__sts_get |
| GET | `/api/driver/trips/{task_id}/ops` | Operations | operations_api_driver_trips__task_id__ops_get |
| POST | `/api/driver/ops/{op_id}/start` | Start | start_api_driver_ops__op_id__start_post |
| POST | `/api/driver/ops/{op_id}/done` | Done | done_api_driver_ops__op_id__done_post |
| POST | `/api/admin/notifications/subscribe` | Subscribe Push | subscribe_push_api_admin_notifications_subscribe_post |
| DELETE | `/api/admin/notifications/subscribe` | Unsubscribe Push | unsubscribe_push_api_admin_notifications_subscribe_delete |
| POST | `/api/admin/notifications/broadcast` | Broadcast Push | broadcast_push_api_admin_notifications_broadcast_post |
| GET | `/api/admin/notifications/settings` | Get Notification Settings | get_notification_settings_api_admin_notifications_settings_get |
| POST | `/api/admin/notifications/settings` | Save Notification Settings | save_notification_settings_api_admin_notifications_settings_post |
| POST | `/api/admin/notifications/test-email` | Send Test Email | send_test_email_api_admin_notifications_test_email_post |
| GET | `/api/admin/transport/kpi/fleet` | Get Fleet Kpi | get_fleet_kpi_api_admin_transport_kpi_fleet_get |
| GET | `/api/admin/transport/kpi/summary` | Get Summary Kpi | get_summary_kpi_api_admin_transport_kpi_summary_get |
| GET | `/api/admin/transport/kpi/regions` | Get Regions Kpi | get_regions_kpi_api_admin_transport_kpi_regions_get |
| GET | `/api/admin/transport/kpi/billing` | Get Billing Kpi | get_billing_kpi_api_admin_transport_kpi_billing_get |
| GET | `/api/admin/transport/kpi/billing/by-company` | Get Billing By Company | get_billing_by_company_api_admin_transport_kpi_billing_by_company_get |
| POST | `/api/gps/track` | Receive Gps Track | receive_gps_track_api_gps_track_post |
| GET | `/api/admin/transport/geofences` | List Geofences | list_geofences_api_admin_transport_geofences_get |
| PATCH | `/api/admin/transport/geofences/{addr_id}` | Update Geofence Radius | update_geofence_radius_api_admin_transport_geofences__addr_id__patch |
| GET | `/api/admin/transport/vehicles/positions` | Get Vehicle Positions | get_vehicle_positions_api_admin_transport_vehicles_positions_get |
| GET | `/api/admin/transport/vehicles/{vehicle_id}/track` | Get Vehicle Track | get_vehicle_track_api_admin_transport_vehicles__vehicle_id__track_get |
| GET | `/api/admin/transport/tariffs` | List Tariffs | list_tariffs_api_admin_transport_tariffs_get |
| GET | `/api/admin/transport/tariffs/table-info` | Get Tariff Table Info | get_tariff_table_info_api_admin_transport_tariffs_table_info_get |
| GET | `/api/admin/transport/billing/orders/{order_id}/export/1c` | Export Order 1C | export_order_1c_api_admin_transport_billing_orders__order_id__export_1c_get |
| GET | `/api/admin/transport/billing/orders/export/1c` | Export Orders 1C | export_orders_1c_api_admin_transport_billing_orders_export_1c_get |
| GET | `/api/admin/transport/maintenance/stats` | Get Table Stats | get_table_stats_api_admin_transport_maintenance_stats_get |
| POST | `/api/admin/transport/maintenance/archive` | Archive Old Tasks | archive_old_tasks_api_admin_transport_maintenance_archive_post |
| GET | `/api/case-pick/tasks/{task_id}/partial-shipment-layout` | Preview | preview_api_case_pick_tasks__task_id__partial_shipment_layout_get |
| POST | `/api/case-pick/tasks/{task_id}/partial-shipment-layout` | Prepare | prepare_api_case_pick_tasks__task_id__partial_shipment_layout_post |
| GET | `/api/picking/waves/{wave_id}/pick-readiness` | Preview | preview_api_picking_waves__wave_id__pick_readiness_get |
| POST | `/api/picking/waves/{wave_id}/release-picking` | Release | release_api_picking_waves__wave_id__release_picking_post |
| GET | `/api/warehouse-tasks/{task_id}/full-pallet-shipment` | Preview | preview_api_warehouse_tasks__task_id__full_pallet_shipment_get |
| POST | `/api/warehouse-tasks/{task_id}/full-pallet-shipment` | Bind | bind_api_warehouse_tasks__task_id__full_pallet_shipment_post |
| GET | `/api/picking/waves/{wave_id}/execution` | Preview | preview_api_picking_waves__wave_id__execution_get |
| POST | `/api/picking/waves/{wave_id}/finish-execution` | Finish | finish_api_picking_waves__wave_id__finish_execution_post |
| GET | `/api/warehouse-hus/composition` | Preview | preview_api_warehouse_hus_composition_get |
| GET | `/api/warehouse-hus/target-slots` | Target Slots | target_slots_api_warehouse_hus_target_slots_get |
| POST | `/api/warehouse-hus/create` | Create | create_api_warehouse_hus_create_post |
| POST | `/api/warehouse-hus/attach` | Attach | attach_api_warehouse_hus_attach_post |
| POST | `/api/warehouse-hus/detach` | Detach | detach_api_warehouse_hus_detach_post |
| POST | `/api/warehouse-hus/move` | Move | move_api_warehouse_hus_move_post |
| POST | `/api/warehouse-hus/plan-move` | Plan Move | plan_move_api_warehouse_hus_plan_move_post |
| POST | `/api/warehouse-hus/attach-case` | Attach Case | attach_case_api_warehouse_hus_attach_case_post |
| POST | `/api/warehouse-hus/detach-case` | Detach Case | detach_case_api_warehouse_hus_detach_case_post |
| POST | `/api/warehouse-hus/ship` | Ship | ship_api_warehouse_hus_ship_post |
| POST | `/api/warehouse-hus/unpack` | Unpack | unpack_api_warehouse_hus_unpack_post |
| POST | `/api/warehouse-hus/relocate-slot` | Relocate Slot | relocate_slot_api_warehouse_hus_relocate_slot_post |
| POST | `/api/warehouse-hus/unpack-case` | Unpack Case | unpack_case_api_warehouse_hus_unpack_case_post |
| POST | `/api/warehouse-hus/repack-slot` | Repack | repack_api_warehouse_hus_repack_slot_post |
| POST | `/api/warehouse-hus/repack-case-slot` | Repack Case | repack_case_api_warehouse_hus_repack_case_slot_post |
| GET | `/api/outgoing-quality/{identifier}` | Status | status_api_outgoing_quality__identifier__get |
| GET | `/api/outgoing-quality/{identifier}/control-label` | Control Label | control_label_api_outgoing_quality__identifier__control_label_get |
| POST | `/api/outgoing-quality/{identifier}/scan` | Scan | scan_api_outgoing_quality__identifier__scan_post |
| POST | `/api/outgoing-quality/{identifier}/weight` | Weight | weight_api_outgoing_quality__identifier__weight_post |
| POST | `/api/outgoing-quality/{identifier}/plan` | Assign Plan | assign_plan_api_outgoing_quality__identifier__plan_post |
| POST | `/api/outgoing-quality/{identifier}/final-weight` | Final Weight | final_weight_api_outgoing_quality__identifier__final_weight_post |
| GET | `/api/outgoing-quality/{identifier}/final-captures` | Final Readings | final_readings_api_outgoing_quality__identifier__final_captures_get |
| GET | `/api/sku-quality-weight/{warehouse}/{article}` | Get Policy | get_policy_api_sku_quality_weight__warehouse___article__get |
| PUT | `/api/sku-quality-weight/{warehouse}/{article}` | Set Policy | set_policy_api_sku_quality_weight__warehouse___article__put |
| GET | `/api/master-data/stores` | Search Stores | search_stores_api_master_data_stores_get |
| GET | `/api/master-data/stores/card` | Store Card | store_card_api_master_data_stores_card_get |
| GET | `/api/master-data/warehouses/options` | Warehouse Options | warehouse_options_api_master_data_warehouses_options_get |
| GET | `/api/master-data/stores/profile` | Read Profile | read_profile_api_master_data_stores_profile_get |
| PUT | `/api/master-data/stores/profile` | Save Profile | save_profile_api_master_data_stores_profile_put |
| GET | `/api/transport/loading/{task_id}/status` | Status | status_api_transport_loading__task_id__status_get |
| POST | `/api/transport/loading/confirm` | Confirm | confirm_api_transport_loading_confirm_post |
| POST | `/api/transport/loading/{task_id}/depart` | Depart | depart_api_transport_loading__task_id__depart_post |
| GET | `/api/transport/loading/single-preview` | Single Preview | single_preview_api_transport_loading_single_preview_get |
| POST | `/api/transport/loading/confirm-single` | Confirm Single | confirm_single_api_transport_loading_confirm_single_post |
| GET | `/api/transport/loading/reconciliation-preview` | Reconciliation Preview | reconciliation_preview_api_transport_loading_reconciliation_preview_get |
| POST | `/api/transport/loading/confirm-reconciliation` | Confirm Reconciliation | confirm_reconciliation_api_transport_loading_confirm_reconciliation_post |
| POST | `/api/transport/loading/unload` | Unload | unload_api_transport_loading_unload_post |
| GET | `/api/delivery/store-receipts/preview` | Preview | preview_api_delivery_store_receipts_preview_get |
| GET | `/api/delivery/store-receipts/trips/{trip_id}/places` | Places | places_api_delivery_store_receipts_trips__trip_id__places_get |
| POST | `/api/delivery/store-receipts/confirm` | Confirm | confirm_api_delivery_store_receipts_confirm_post |
| PUT | `/api/delivery/store-receipts/policy` | Configure | configure_api_delivery_store_receipts_policy_put |
| POST | `/api/delivery/store-receipts/receivers` | Assign Receiver | assign_receiver_api_delivery_store_receipts_receivers_post |
| GET | `/api/delivery/store-receipts/cases` | Cases | cases_api_delivery_store_receipts_cases_get |
| GET | `/api/delivery/store-receipts/cases/{case_id}` | Case Detail | case_detail_api_delivery_store_receipts_cases__case_id__get |
| POST | `/api/delivery/store-receipts/load-custody/release` | Release Custody | release_custody_api_delivery_store_receipts_load_custody_release_post |
| POST | `/api/delivery/store-receipts/unloading/start` | Start Unloading | start_unloading_api_delivery_store_receipts_unloading_start_post |
| GET | `/api/delivery/store-receipts/unloading` | Unloading | unloading_api_delivery_store_receipts_unloading_get |
| POST | `/api/delivery/store-photos/upload` | Upload | upload_api_delivery_store_photos_upload_post |
| GET | `/api/delivery/store-photos/list` | Photos | photos_api_delivery_store_photos_list_get |
| GET | `/api/delivery/store-photos/{photo_id}/content` | Content | content_api_delivery_store_photos__photo_id__content_get |
| PUT | `/api/delivery/store-scales/devices/{device_id}` | Configure | configure_api_delivery_store_scales_devices__device_id__put |
| POST | `/api/delivery/store-scales/captures` | Capture | capture_api_delivery_store_scales_captures_post |
| GET | `/api/delivery/store-scales/captures` | Readings | readings_api_delivery_store_scales_captures_get |
| GET | `/api/delivery/store-scales/captures/{capture_key}` | Reading | reading_api_delivery_store_scales_captures__capture_key__get |
| GET | `/api/customer-orders/{order_id}/delivery` | Delivery | delivery_api_customer_orders__order_id__delivery_get |
| POST | `/api/delivery/case-work/{case_id}/assign` | Assign | assign_api_delivery_case_work__case_id__assign_post |
| POST | `/api/delivery/case-work/{case_id}/finding` | Finding | finding_api_delivery_case_work__case_id__finding_post |
| POST | `/api/delivery/case-work/{case_id}/loss` | Loss | loss_api_delivery_case_work__case_id__loss_post |
| GET | `/api/delivery/case-work/mine` | Mine | mine_api_delivery_case_work_mine_get |
| GET | `/api/delivery/case-work/{case_id}/investigation` | Investigation | investigation_api_delivery_case_work__case_id__investigation_get |
| GET | `/api/delivery/case-work/{case_id}/loss-review` | Review | review_api_delivery_case_work__case_id__loss_review_get |
| GET | `/api/delivery/case-work/{case_id}/management` | Management | management_api_delivery_case_work__case_id__management_get |
| POST | `/api/delivery/case-work/{case_id}/close` | Close | close_api_delivery_case_work__case_id__close_post |
| POST | `/api/delivery/store-returns/{receipt_id}/approve` | Approve | approve_api_delivery_store_returns__receipt_id__approve_post |
| GET | `/api/delivery/store-returns/{receipt_id}` | Original | original_api_delivery_store_returns__receipt_id__get |
| GET | `/api/delivery/store-returns/{receipt_id}/reuse-preview` | Reuse Preview | reuse_preview_api_delivery_store_returns__receipt_id__reuse_preview_get |
| POST | `/api/integrations/sap/store-returns` | Receive | receive_api_integrations_sap_store_returns_post |
| POST | `/api/delivery/store-return-transport/plan` | Plan | plan_api_delivery_store_return_transport_plan_post |
| GET | `/api/delivery/store-return-transport/eligible` | Eligible | eligible_api_delivery_store_return_transport_eligible_get |
| GET | `/api/delivery/store-return-transport/trips/{task_id}` | Trip | trip_api_delivery_store_return_transport_trips__task_id__get |
| PUT | `/api/transport/driver-bindings/{driver_id}` | Configure | configure_api_transport_driver_bindings__driver_id__put |
| GET | `/api/transport/driver-bindings/{driver_id}` | Get | get_api_transport_driver_bindings__driver_id__get |
| POST | `/api/delivery/store-return-custody/handover` | Handover | handover_api_delivery_store_return_custody_handover_post |
| POST | `/api/delivery/store-return-custody/pickup` | Pickup | pickup_api_delivery_store_return_custody_pickup_post |
| GET | `/api/delivery/store-return-custody/store` | Store | store_api_delivery_store_return_custody_store_get |
| GET | `/api/delivery/store-return-custody/driver` | Driver | driver_api_delivery_store_return_custody_driver_get |
| PUT | `/api/inventory/store-returns/warehouses/{ware_id}/policy` | Configure | configure_api_inventory_store_returns_warehouses__ware_id__policy_put |
| GET | `/api/inventory/store-returns/warehouses/{ware_id}/policy` | Policy | policy_api_inventory_store_returns_warehouses__ware_id__policy_get |
| GET | `/api/inventory/store-returns/warehouses/{ware_id}/pending` | Pending | pending_api_inventory_store_returns_warehouses__ware_id__pending_get |
| POST | `/api/inventory/store-returns/receive` | Receive | receive_api_inventory_store_returns_receive_post |
| PUT | `/api/inventory/store-returns/warehouses/{ware_id}/reuse-receiving` | Reuse Zone | reuse_zone_api_inventory_store_returns_warehouses__ware_id__reuse_receiving_put |
| GET | `/api/inventory/store-returns/warehouses/{ware_id}/pending-page` | Pending Page | pending_page_api_inventory_store_returns_warehouses__ware_id__pending_page_get |
| GET | `/api/inventory/store-returns/warehouses/{ware_id}/pickups/{pickup_id}/source` | Selected Source | selected_source_api_inventory_store_returns_warehouses__ware_id__pickups__pickup_id__source_get |
| PUT | `/api/inventory/store-return-putaway/warehouses/{ware_id}/targets` | Targets | targets_api_inventory_store_return_putaway_warehouses__ware_id__targets_put |
| GET | `/api/inventory/store-return-putaway/warehouses/{ware_id}/pending` | Pending | pending_api_inventory_store_return_putaway_warehouses__ware_id__pending_get |
| POST | `/api/inventory/store-return-putaway/plan` | Plan | plan_api_inventory_store_return_putaway_plan_post |
| POST | `/api/inventory/tare/count` | Count | count_api_inventory_tare_count_post |
| POST | `/api/inventory/tare/offer` | Offer | offer_api_inventory_tare_offer_post |
| POST | `/api/inventory/tare/accept` | Accept | accept_api_inventory_tare_accept_post |
| POST | `/api/inventory/tare/offer-cancel` | Offer Cancel | offer_cancel_api_inventory_tare_offer_cancel_post |
| GET | `/api/inventory/tare/warehouses/{ware_id}/balances` | Balances | balances_api_inventory_tare_warehouses__ware_id__balances_get |
| GET | `/api/inventory/tare/trips/{task_id}/offers` | Offers | offers_api_inventory_tare_trips__task_id__offers_get |
| GET | `/api/inventory/tare/trips/{task_id}/context` | Context | context_api_inventory_tare_trips__task_id__context_get |
| GET | `/api/inventory/tare/warehouses/{ware_id}/damage-custody` | Damage Custody | damage_custody_api_inventory_tare_warehouses__ware_id__damage_custody_get |
| GET | `/api/inventory/tare/return-policy` | Read | read_api_inventory_tare_return_policy_get |
| PUT | `/api/inventory/tare/return-policy` | Configure | configure_api_inventory_tare_return_policy_put |
| GET | `/api/inventory/tare/warehouses/{ware_id}/store-debt` | Debt | debt_api_inventory_tare_warehouses__ware_id__store_debt_get |
| POST | `/api/inventory/tare/damage` | Damage | damage_api_inventory_tare_damage_post |
| POST | `/api/inventory/tare/writeoff` | Writeoff | writeoff_api_inventory_tare_writeoff_post |
| GET | `/api/inventory/tare/warehouses/{ware_id}/damage-cases` | Cases | cases_api_inventory_tare_warehouses__ware_id__damage_cases_get |
| POST | `/api/inventory/tare/book` | Book | book_api_inventory_tare_book_post |
| POST | `/api/inventory/tare/book-cancel` | Cancel | cancel_api_inventory_tare_book_cancel_post |
| GET | `/api/inventory/tare/warehouses/{ware_id}/availability` | Availability | availability_api_inventory_tare_warehouses__ware_id__availability_get |
| GET | `/api/inventory/tare/warehouses/{ware_id}/bookings` | Bookings | bookings_api_inventory_tare_warehouses__ware_id__bookings_get |
| GET | `/api/inventory/tare/assembly/catalog` | Catalog | catalog_api_inventory_tare_assembly_catalog_get |
| GET | `/api/inventory/tare/warehouses/{ware_id}/trips/{task_id}/loaded-bookings` | Loaded Bookings | loaded_bookings_api_inventory_tare_warehouses__ware_id__trips__task_id__loaded_bookings_get |
| GET | `/api/inventory/tare/warehouses/{ware_id}/waves/{wave_id}/forecast` | Forecast | forecast_api_inventory_tare_warehouses__ware_id__waves__wave_id__forecast_get |
| GET | `/api/inventory/tare/load-recovery-candidates` | Load Recovery Candidates | load_recovery_candidates_api_inventory_tare_load_recovery_candidates_get |
| POST | `/api/inventory/tare/loss-report` | Report | report_api_inventory_tare_loss_report_post |
| POST | `/api/inventory/tare/loss-decide` | Decide | decide_api_inventory_tare_loss_decide_post |
| GET | `/api/inventory/tare/warehouses/{ware_id}/loss-cases` | Cases | cases_api_inventory_tare_warehouses__ware_id__loss_cases_get |
| POST | `/api/inventory/supplier-returns/prepare` | Prepare | prepare_api_inventory_supplier_returns_prepare_post |
| GET | `/api/inventory/supplier-returns/warehouses/{ware_id}` | Pending | pending_api_inventory_supplier_returns_warehouses__ware_id__get |
| GET | `/api/inventory/supplier-returns/suppliers` | Suppliers | suppliers_api_inventory_supplier_returns_suppliers_get |
| POST | `/api/inventory/supplier-handover/record` | Record | record_api_inventory_supplier_handover_record_post |
| POST | `/api/inventory/supplier-handover/confirm` | Confirm | confirm_api_inventory_supplier_handover_confirm_post |
| GET | `/api/inventory/supplier-handover/warehouses/{ware_id}` | Pending | pending_api_inventory_supplier_handover_warehouses__ware_id__get |
| POST | `/api/inventory/return-disposal/report` | Report | report_api_inventory_return_disposal_report_post |
| POST | `/api/inventory/return-disposal/dispose` | Dispose | dispose_api_inventory_return_disposal_dispose_post |
| GET | `/api/inventory/return-disposal/warehouses/{ware_id}` | Pending | pending_api_inventory_return_disposal_warehouses__ware_id__get |
| POST | `/api/finance/logistics-costs/rates` | Rate | rate_api_finance_logistics_costs_rates_post |
| POST | `/api/finance/logistics-costs/rates/monthly` | Monthly Rate | monthly_rate_api_finance_logistics_costs_rates_monthly_post |
| GET | `/api/finance/logistics-costs/warehouses/{ware_id}/rates` | Rates | rates_api_finance_logistics_costs_warehouses__ware_id__rates_get |
| GET | `/api/finance/logistics-costs/warehouses/{ware_id}/rates/history` | Rate History | rate_history_api_finance_logistics_costs_warehouses__ware_id__rates_history_get |
| POST | `/api/finance/logistics-costs/calculate` | Calculate | calculate_api_finance_logistics_costs_calculate_post |
| GET | `/api/finance/logistics-costs/trips/{trip_id}` | Trip | trip_api_finance_logistics_costs_trips__trip_id__get |
| GET | `/api/finance/logistics-costs/billing-orders/{invoice_id}` | Invoice | invoice_api_finance_logistics_costs_billing_orders__invoice_id__get |
| GET | `/api/finance/logistics-costs/trips/{trip_id}/assembly-period` | Assembly Period | assembly_period_api_finance_logistics_costs_trips__trip_id__assembly_period_get |
| GET | `/api/finance/logistics-costs/warehouses/{ware_id}/period-policy` | Period Policy | period_policy_api_finance_logistics_costs_warehouses__ware_id__period_policy_get |
| POST | `/api/finance/logistics-costs/warehouses/{ware_id}/period-policy` | Configure Period | configure_period_api_finance_logistics_costs_warehouses__ware_id__period_policy_post |
| GET | `/api/finance/logistics-costs/billing-orders/{invoice_id}/summary` | Invoice Summary | invoice_summary_api_finance_logistics_costs_billing_orders__invoice_id__summary_get |
| GET | `/api/finance/logistics-costs/trips/{trip_id}/transport-tariff-sources` | Transport Tariff Sources | transport_tariff_sources_api_finance_logistics_costs_trips__trip_id__transport_tariff_sources_get |
| POST | `/api/finance/logistics-costs/transport-norms` | Publish Transport Norm | publish_transport_norm_api_finance_logistics_costs_transport_norms_post |
| GET | `/api/finance/logistics-costs/warehouses/{ware_id}/transport-norms/{source_price_id}/history` | Transport Norm History | transport_norm_history_api_finance_logistics_costs_warehouses__ware_id__transport_norms__source_price_id__history_get |
| GET | `/api/finance/logistics-costs/trips/{trip_id}/transport-cost-facts` | Transport Cost Facts | transport_cost_facts_api_finance_logistics_costs_trips__trip_id__transport_cost_facts_get |
| GET | `/api/finance/logistics-costs/trips/{trip_id}/transport-cost-preview` | Transport Cost Preview | transport_cost_preview_api_finance_logistics_costs_trips__trip_id__transport_cost_preview_get |
| POST | `/api/finance/logistics-costs/transport-costs/conduct` | Conduct Transport Cost | conduct_transport_cost_api_finance_logistics_costs_transport_costs_conduct_post |
| GET | `/api/finance/logistics-costs/trips/{trip_id}/transport-costs` | Transport Costs | transport_costs_api_finance_logistics_costs_trips__trip_id__transport_costs_get |
| GET | `/api/finance/logistics-costs/billing-orders/{invoice_id}/transport-costs` | Invoice Transport Costs | invoice_transport_costs_api_finance_logistics_costs_billing_orders__invoice_id__transport_costs_get |
| GET | `/api/finance/logistics-expenses/articles` | Articles | articles_api_finance_logistics_expenses_articles_get |
| POST | `/api/finance/logistics-expenses/articles` | Article | article_api_finance_logistics_expenses_articles_post |
| POST | `/api/finance/logistics-expenses/report` | Report | report_api_finance_logistics_expenses_report_post |
| POST | `/api/finance/logistics-expenses/decide` | Decide | decide_api_finance_logistics_expenses_decide_post |
| GET | `/api/finance/logistics-expenses/warehouses/{ware_id}` | Pending | pending_api_finance_logistics_expenses_warehouses__ware_id__get |
| GET | `/api/finance/logistics-expenses/warehouses/{ware_id}/normative-costs` | Normative Cost Sources | normative_cost_sources_api_finance_logistics_expenses_warehouses__ware_id__normative_costs_get |
| POST | `/api/finance/expense-allocation` | Allocate | allocate_api_finance_expense_allocation_post |
| GET | `/api/finance/expense-allocation/billing-orders/{invoice_id}` | Invoice | invoice_api_finance_expense_allocation_billing_orders__invoice_id__get |
| GET | `/api/finance/day-reconciliation/warehouses/{ware_id}` | Report | report_api_finance_day_reconciliation_warehouses__ware_id__get |
| GET | `/api/finance/day-reconciliation/warehouses/{ware_id}/stock-conflicts` | Stock Conflicts | stock_conflicts_api_finance_day_reconciliation_warehouses__ware_id__stock_conflicts_get |
| GET | `/api/inventory/interwarehouse/source-loads/{load_id}/group-composition` | Group Source | group_source_api_inventory_interwarehouse_source_loads__load_id__group_composition_get |
| GET | `/api/inventory/interwarehouse/group-warehouses/{ware_id}` | Group Queue | group_queue_api_inventory_interwarehouse_group_warehouses__ware_id__get |
| GET | `/api/inventory/interwarehouse/group-plans/{plan_id}` | Group Detail | group_detail_api_inventory_interwarehouse_group_plans__plan_id__get |
| GET | `/api/inventory/interwarehouse/source-loads/{load_id}/group-proof` | Group Proof | group_proof_api_inventory_interwarehouse_source_loads__load_id__group_proof_get |
| POST | `/api/inventory/interwarehouse/group-plan` | Group Plan | group_plan_api_inventory_interwarehouse_group_plan_post |
| POST | `/api/inventory/interwarehouse/plan` | Plan | plan_api_inventory_interwarehouse_plan_post |
| GET | `/api/inventory/interwarehouse/warehouses/{ware_id}` | Queue | queue_api_inventory_interwarehouse_warehouses__ware_id__get |
| POST | `/api/inventory/interwarehouse/unload` | Unload | unload_api_inventory_interwarehouse_unload_post |
| POST | `/api/inventory/interwarehouse/receive` | Receive | receive_api_inventory_interwarehouse_receive_post |
| POST | `/api/inventory/interwarehouse/group-receive` | Group Receive | group_receive_api_inventory_interwarehouse_group_receive_post |
| POST | `/api/inventory/interwarehouse/group-placement` | Group Placement | group_placement_api_inventory_interwarehouse_group_placement_post |
| POST | `/api/inventory/interwarehouse/group-onward` | Group Onward | group_onward_api_inventory_interwarehouse_group_onward_post |
| POST | `/api/inventory/interwarehouse/placement` | Placement | placement_api_inventory_interwarehouse_placement_post |
| POST | `/api/inventory/interwarehouse/release-custody` | Release Custody | release_custody_api_inventory_interwarehouse_release_custody_post |
| POST | `/api/inventory/interwarehouse/prepare-onward` | Prepare Onward | prepare_onward_api_inventory_interwarehouse_prepare_onward_post |
| GET | `/api/inventory/interwarehouse/plans/{plan_id}/units` | Source Units | source_units_api_inventory_interwarehouse_plans__plan_id__units_get |
| POST | `/api/inventory/interwarehouse/decisions` | Dispatch Decision | dispatch_decision_api_inventory_interwarehouse_decisions_post |
| POST | `/api/inventory/interwarehouse/temperature-decisions` | Temperature Decision | temperature_decision_api_inventory_interwarehouse_temperature_decisions_post |
| GET | `/api/inventory/interwarehouse/trips/{trip_id}/incoming` | Incoming | incoming_api_inventory_interwarehouse_trips__trip_id__incoming_get |
| GET | `/api/inventory/interwarehouse/plans/{plan_id}/decisions` | Decisions | decisions_api_inventory_interwarehouse_plans__plan_id__decisions_get |
| POST | `/api/inventory/interwarehouse/incident-closures` | Close Incident | close_incident_api_inventory_interwarehouse_incident_closures_post |
| GET | `/api/inventory/interwarehouse/receipts/{receipt_id}/shortage` | Shortage | shortage_api_inventory_interwarehouse_receipts__receipt_id__shortage_get |
| POST | `/api/inventory/interwarehouse/shortage-reports` | Report Shortage | report_shortage_api_inventory_interwarehouse_shortage_reports_post |
| POST | `/api/inventory/interwarehouse/shortage-confirmations` | Confirm Shortage | confirm_shortage_api_inventory_interwarehouse_shortage_confirmations_post |
| POST | `/api/inventory/interwarehouse/recovery-reports` | Report Recovery | report_recovery_api_inventory_interwarehouse_recovery_reports_post |
| POST | `/api/inventory/interwarehouse/recovery-approvals` | Approve Recovery | approve_recovery_api_inventory_interwarehouse_recovery_approvals_post |
| POST | `/api/inventory/interwarehouse/recovery-receipts` | Receive Recovery | receive_recovery_api_inventory_interwarehouse_recovery_receipts_post |
| POST | `/api/inventory/interwarehouse/recovery-placement` | Recovery Placement | recovery_placement_api_inventory_interwarehouse_recovery_placement_post |
| POST | `/api/inventory/interwarehouse/prepare-recovery-onward` | Prepare Recovery Onward | prepare_recovery_onward_api_inventory_interwarehouse_prepare_recovery_onward_post |
| POST | `/api/inventory/interwarehouse/recovery-cancellations` | Cancel Recovery | cancel_recovery_api_inventory_interwarehouse_recovery_cancellations_post |
| POST | `/api/inventory/trace-manifests` | Import Manifest | import_manifest_api_inventory_trace_manifests_post |
| GET | `/api/inventory/trace-manifests/warehouses/{ware_id}` | Manifests | manifests_api_inventory_trace_manifests_warehouses__ware_id__get |
| POST | `/api/inventory/trace-manifests/inventory-context` | Inventory Context | inventory_context_api_inventory_trace_manifests_inventory_context_post |
| POST | `/api/inventory/trace-manifests/mes-context` | Mes Context | mes_context_api_inventory_trace_manifests_mes_context_post |
| POST | `/api/inventory/trace-manifests/aggregations/invalidate` | Invalidate Aggregate | invalidate_aggregate_api_inventory_trace_manifests_aggregations_invalidate_post |
| GET | `/api/inventory/trace-manifests/warehouses/{ware_id}/pallets/{origin}/aggregations` | Aggregate Lifecycle | aggregate_lifecycle_api_inventory_trace_manifests_warehouses__ware_id__pallets__origin__aggregations_get |
| POST | `/api/transport/warehouse-forecast/warehouses/{ware_id}/view` | Forecast | forecast_api_transport_warehouse_forecast_warehouses__ware_id__view_post |
| POST | `/api/transport/warehouse-forecast/warehouses/{ware_id}/project` | Project | project_api_transport_warehouse_forecast_warehouses__ware_id__project_post |
| POST | `/api/transport/warehouse-forecast/source` | Project Source | project_source_api_transport_warehouse_forecast_source_post |
| POST | `/api/resources/workload/norms` | Save Norm | save_norm_api_resources_workload_norms_post |
| POST | `/api/resources/workload/attendance` | Plan Attendance | plan_attendance_api_resources_workload_attendance_post |
| POST | `/api/resources/workload/attendance/replace` | Replace Attendance | replace_attendance_api_resources_workload_attendance_replace_post |
| POST | `/api/resources/workload/attendance/cancel` | Cancel Attendance | cancel_attendance_api_resources_workload_attendance_cancel_post |
| GET | `/api/resources/workload/warehouses/{ware_id}` | Read Configuration | read_configuration_api_resources_workload_warehouses__ware_id__get |
| POST | `/api/resources/workload/forecast-scopes` | Save Forecast Scope | save_forecast_scope_api_resources_workload_forecast_scopes_post |
| POST | `/api/resources/workload/warehouses/{ware_id}/preview` | Preview | preview_api_resources_workload_warehouses__ware_id__preview_post |
| GET | `/api/resources/workload/waves/{wave_id}/time-context` | Context | context_api_resources_workload_waves__wave_id__time_context_get |
| POST | `/api/resources/workload/waves/approve-time` | Approve | approve_api_resources_workload_waves_approve_time_post |
| POST | `/api/inventory/slotting/warehouses/{ware_id}/articles/{article}/scenario` | Preview | preview_api_inventory_slotting_warehouses__ware_id__articles__article__scenario_post |
| PATCH | `/api/admin/transport/operations/{op_id}/fact` | Update Operation Fact | update_operation_fact_api_admin_transport_operations__op_id__fact_patch |
| GET | `/api/resources/workload/warehouses/{ware_id}/attendance/{plan_id}/history` | History | history_api_resources_workload_warehouses__ware_id__attendance__plan_id__history_get |
| POST | `/api/inventory/slotting/warehouses/{ware_id}/articles/{article}/recommendations` | Save | save_api_inventory_slotting_warehouses__ware_id__articles__article__recommendations_post |
| GET | `/api/inventory/slotting/warehouses/{ware_id}/articles/{article}/recommendations/{proposal_id}` | Get | get_api_inventory_slotting_warehouses__ware_id__articles__article__recommendations__proposal_id__get |
| POST | `/api/inventory/slotting/warehouses/{ware_id}/articles/{article}/recommendations/{proposal_id}/cancel` | Cancel | cancel_api_inventory_slotting_warehouses__ware_id__articles__article__recommendations__proposal_id__cancel_post |
| POST | `/api/inventory/slotting/warehouses/{ware_id}/articles/{article}/recommendations/{proposal_id}/approve` | Approve | approve_api_inventory_slotting_warehouses__ware_id__articles__article__recommendations__proposal_id__approve_post |
| POST | `/api/inventory/slotting/warehouses/{ware_id}/articles/{article}/recommendations/actions/close-drain` | Close Drain | close_drain_api_inventory_slotting_warehouses__ware_id__articles__article__recommendations_actions_close_drain_post |
| GET | `/api/transport/preflight/trips/{trip_id}/time-context` | Time Context | time_context_api_transport_preflight_trips__trip_id__time_context_get |
| GET | `/api/transport/preflight/trips/{trip_id}/coordination` | Coordination Preflight | coordination_preflight_api_transport_preflight_trips__trip_id__coordination_get |
| POST | `/api/transport/preflight/time-approvals` | Approve Time | approve_time_api_transport_preflight_time_approvals_post |
| POST | `/api/transport/preflight/trips/{trip_id}/time` | Trip Time Preflight | trip_time_preflight_api_transport_preflight_trips__trip_id__time_post |
| GET | `/api/transport/preflight/plans/{plan_id}` | Plan Preflight | plan_preflight_api_transport_preflight_plans__plan_id__get |
| POST | `/api/transport/preflight/trips/{trip_id}` | Trip Preflight | trip_preflight_api_transport_preflight_trips__trip_id__post |
| GET | `/api/transport/preflight/trips/{trip_id}/route-context` | Route Context | route_context_api_transport_preflight_trips__trip_id__route_context_get |
| POST | `/api/transport/preflight/route-inputs` | Route Input | route_input_api_transport_preflight_route_inputs_post |
| GET | `/api/transport/preflight/trips/{trip_id}/road-legs` | Road Legs | road_legs_api_transport_preflight_trips__trip_id__road_legs_get |
| GET | `/api/transport/preflight/trips/{trip_id}/delivery-windows` | Delivery Windows | delivery_windows_api_transport_preflight_trips__trip_id__delivery_windows_get |
| POST | `/api/case-pick/tasks/{task}/sscc-label` | Issue | issue_api_case_pick_tasks__task__sscc_label_post |
| GET | `/api/case-pick/tasks/{task}/sscc-label` | Current | current_api_case_pick_tasks__task__sscc_label_get |
| POST | `/api/case-pick/tasks/{task}/sscc-label/confirm` | Confirm | confirm_api_case_pick_tasks__task__sscc_label_confirm_post |
| GET | `/api/case-pick/tasks/{task}/sscc-label/document` | Document | document_api_case_pick_tasks__task__sscc_label_document_get |
| POST | `/api/integrations/sap/store-decisions` | Receive Decision | receive_decision_api_integrations_sap_store_decisions_post |
| GET | `/api/integrations/sap/store-orders/{order_id}/preparation-readiness` | Readiness | readiness_api_integrations_sap_store_orders__order_id__preparation_readiness_get |
| POST | `/api/integrations/sap/store-orders/{order_id}/preparation-layout` | Layout | layout_api_integrations_sap_store_orders__order_id__preparation_layout_post |
| POST | `/api/integrations/sap/store-orders/{order_id}/automatic-layout` | Auto Preview | auto_preview_api_integrations_sap_store_orders__order_id__automatic_layout_post |
| POST | `/api/integrations/sap/store-orders/{order_id}/prepare-st/automatic` | Auto Prepare | auto_prepare_api_integrations_sap_store_orders__order_id__prepare_st_automatic_post |
| POST | `/api/integrations/sap/store-orders/{order_id}/prepare-st/automatic/resolve` | Auto Resolve | auto_resolve_api_integrations_sap_store_orders__order_id__prepare_st_automatic_resolve_post |
| GET | `/api/finance/day-reconciliation/warehouses/{ware_id}/review-context` | Context | context_api_finance_day_reconciliation_warehouses__ware_id__review_context_get |
| POST | `/api/finance/day-reconciliation/reviews` | Record | record_api_finance_day_reconciliation_reviews_post |
| POST | `/api/finance/day-reconciliation/reviews/resolve` | Resolve | resolve_api_finance_day_reconciliation_reviews_resolve_post |
| GET | `/api/finance/day-reconciliation/reviews/warehouses/{ware_id}/history` | History | history_api_finance_day_reconciliation_reviews_warehouses__ware_id__history_get |
| GET | `/api/finance/day-reconciliation/reviews/{operation}` | Detail | detail_api_finance_day_reconciliation_reviews__operation__get |
| GET | `/api/finance/day-reconciliation/warehouses/{ware_id}/shipping-register` | Shipping Register | shipping_register_api_finance_day_reconciliation_warehouses__ware_id__shipping_register_get |
| GET | `/api/finance/day-reconciliation/reviews/{review_id}/shipping-inspections` | Inspection | inspection_api_finance_day_reconciliation_reviews__review_id__shipping_inspections_get |
| POST | `/api/finance/day-reconciliation/shipping-inspections` | Inspect | inspect_api_finance_day_reconciliation_shipping_inspections_post |
| POST | `/api/finance/day-reconciliation/shipping-inspections/resolve` | Resolve Inspection | resolve_inspection_api_finance_day_reconciliation_shipping_inspections_resolve_post |
| GET | `/api/transport/st-deferrals/context` | Context | context_api_transport_st_deferrals_context_get |
| POST | `/api/transport/st-deferrals` | Defer | defer_api_transport_st_deferrals_post |
| GET | `/api/transport/st-deferrals/history` | History | history_api_transport_st_deferrals_history_get |
| GET | `/api/transport/st-deferrals/trip-candidates` | Trip Candidates | trip_candidates_api_transport_st_deferrals_trip_candidates_get |
| GET | `/api/transport/warehouse-depots/{warehouse_id}` | Context | context_api_transport_warehouse_depots__warehouse_id__get |
| POST | `/api/transport/warehouse-depots` | Configure | configure_api_transport_warehouse_depots_post |
| POST | `/api/transport/warehouse-depots/resolve` | Resolve | resolve_api_transport_warehouse_depots_resolve_post |
| POST | `/api/admin/transport/vehicle-profiles` | Configure | configure_api_admin_transport_vehicle_profiles_post |
| GET | `/api/admin/transport/vehicles/{vehicle_id}/profile` | Read | read_api_admin_transport_vehicles__vehicle_id__profile_get |
| GET | `/api/admin/transport/vehicle-profiles/tare-types` | Tare Types | tare_types_api_admin_transport_vehicle_profiles_tare_types_get |
| POST | `/api/receiving/st-deferrals/waiting-tasks` | Plan Waiting | plan_waiting_api_receiving_st_deferrals_waiting_tasks_post |
| GET | `/api/receiving/st-deferrals/waiting-tasks` | Read Waiting | read_waiting_api_receiving_st_deferrals_waiting_tasks_get |
| GET | `/api/inventory/pallet-floor-types` | Read | read_api_inventory_pallet_floor_types_get |
| POST | `/api/inventory/pallet-floor-types` | Confirm | confirm_api_inventory_pallet_floor_types_post |
| GET | `/api/case-pick/tasks/{task_id}/pallet-type` | Read | read_api_case_pick_tasks__task_id__pallet_type_get |
| POST | `/api/case-pick/tasks/{task_id}/pallet-type` | Change | change_api_case_pick_tasks__task_id__pallet_type_post |
| GET | `/api/customer-orders/{order_id}/prepared-layout` | Read | read_api_customer_orders__order_id__prepared_layout_get |
| POST | `/api/customer-orders/{order_id}/prepared-layout/preview` | Preview | preview_api_customer_orders__order_id__prepared_layout_preview_post |
| POST | `/api/customer-orders/{order_id}/prepared-layout/move-row` | Move | move_api_customer_orders__order_id__prepared_layout_move_row_post |
| GET | `/api/inventory/quality-policies/warehouses/{warehouse}` | Read | read_api_inventory_quality_policies_warehouses__warehouse__get |
| POST | `/api/inventory/quality-policies/warehouses/{warehouse}` | Save | save_api_inventory_quality_policies_warehouses__warehouse__post |
