# Инвентаризация API (статический разбор, 686 маршрутов)

Источник: `tools/api_inventory.py`. Право — `require_permission` или его алиас; «dep:» — проверка выполняется внутри зависимости (смотреть файл).

## `/api/admin/adapter-requests`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/admin/adapter-requests` | external_outbox_view | app/routers/traceability.py |
| GET | `/api/admin/adapter-requests/{adapter_request_id}` | external_outbox_view | app/routers/traceability.py |

## `/api/admin/api-calls`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/admin/api-calls` | api_audit_view | app/routers/api_audit.py |
| GET | `/api/admin/api-calls/{api_call_id}` | api_audit_view | app/routers/api_audit.py |
| POST | `/api/admin/api-calls/replay` | api_audit_view | app/routers/api_audit.py |

## `/api/admin/auth`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/admin/auth/login` | wms_admin_login | app/routers/admin_auth.py |
| GET | `/api/admin/auth/me` | wms_admin_login | app/routers/admin_auth.py |

## `/api/admin/event-outbox`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/admin/event-outbox` | external_outbox_view | app/routers/traceability.py |
| GET | `/api/admin/event-outbox/{event_outbox_id}` | external_outbox_view | app/routers/traceability.py |
| POST | `/api/admin/event-outbox/{event_outbox_id}/retry` | external_outbox_view | app/routers/traceability.py |

## `/api/admin/notifications`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/admin/notifications/subscribe` | transport_dispatch_view | app/routers/notifications.py |
| DELETE | `/api/admin/notifications/subscribe` | transport_dispatch_view | app/routers/notifications.py |
| POST | `/api/admin/notifications/broadcast` | transport_dispatch_view | app/routers/notifications.py |
| GET | `/api/admin/notifications/settings` | transport_dispatch_view | app/routers/notifications.py |
| POST | `/api/admin/notifications/settings` | transport_dispatch_view | app/routers/notifications.py |
| POST | `/api/admin/notifications/test-email` | transport_dispatch_view | app/routers/notifications.py |

## `/api/admin/pick-routes`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/admin/pick-routes` | pick_route_admin_view | app/routers/warehouse_topology.py |
| POST | `/api/admin/pick-routes/build` | pick_route_admin_edit | app/routers/warehouse_topology.py |
| POST | `/api/admin/pick-routes/{pick_route_id}/publish` | pick_route_admin_publish | app/routers/warehouse_topology.py |

## `/api/admin/product-shipment-settings`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/admin/product-shipment-settings` | quality_batch_view | app/routers/products.py |
| PATCH | `/api/admin/product-shipment-settings/{articul}` | quality_batch_edit | app/routers/products.py |

## `/api/admin/rights`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/admin/rights/users` | rights_admin_view | app/routers/admin_rights.py |
| GET | `/api/admin/rights/groups` | rights_admin_view | app/routers/admin_rights.py |
| POST | `/api/admin/rights/groups` | rights_admin_edit | app/routers/admin_rights.py |
| GET | `/api/admin/rights/groups/{group_id}/rights` | rights_admin_view | app/routers/admin_rights.py |
| POST | `/api/admin/rights/groups/{group_id}/rights` | rights_admin_edit | app/routers/admin_rights.py |
| DELETE | `/api/admin/rights/groups/{group_id}/rights/{right_name}` | rights_admin_edit | app/routers/admin_rights.py |
| PUT | `/api/admin/rights/users/{user_id}/group` | rights_admin_edit | app/routers/admin_rights.py |

## `/api/admin/slow-sql`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/admin/slow-sql` | slow_sql_view | app/routers/slow_sql.py |
| GET | `/api/admin/slow-sql/top` | slow_sql_view | app/routers/slow_sql.py |
| GET | `/api/admin/slow-sql/oracle-top` | slow_sql_view | app/routers/slow_sql.py |
| GET | `/api/admin/slow-sql/{log_id}` | slow_sql_view | app/routers/slow_sql.py |

## `/api/admin/topology-cells`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| PATCH | `/api/admin/topology-cells/{topology_cell_id}` | warehouse_topology_edit | app/routers/warehouse_topology.py |

## `/api/admin/transport`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| PATCH | `/api/admin/transport/operations/{op_id}/fact` | transport_dispatch_edit | app/modules/transport/api/operation_fact_routes.py |
| POST | `/api/admin/transport/vehicle-profiles` | transport_fleet_edit | app/modules/transport/api/vehicle_profile_routes.py |
| GET | `/api/admin/transport/vehicles/{vehicle_id}/profile` | transport_dispatch_view | app/modules/transport/api/vehicle_profile_routes.py |
| GET | `/api/admin/transport/vehicle-profiles/tare-types` | transport_dispatch_view | app/modules/transport/api/vehicle_profile_routes.py |
| GET | `/api/admin/transport/billing/orders/{order_id}/export/1c` | edit_bill_tt | app/routers/export_1c.py |
| GET | `/api/admin/transport/billing/orders/export/1c` | edit_bill_tt | app/routers/export_1c.py |
| GET | `/api/admin/transport/geofences` | transport_dispatch_view | app/routers/gps.py |
| PATCH | `/api/admin/transport/geofences/{addr_id:path}` | warehouse_settings_edit | app/routers/gps.py |
| GET | `/api/admin/transport/vehicles/positions` | transport_dispatch_view | app/routers/gps.py |
| GET | `/api/admin/transport/vehicles/{vehicle_id}/track` | transport_dispatch_view | app/routers/gps.py |
| GET | `/api/admin/transport/maintenance/stats` | transport_dispatch_view | app/routers/maintenance.py |
| POST | `/api/admin/transport/maintenance/archive` | rights_admin_edit | app/routers/maintenance.py |
| GET | `/api/admin/transport/vehicles` | transport_dispatch_view | app/routers/transport.py |
| GET | `/api/admin/transport/vehicles/full` | transport_dispatch_view | app/routers/transport.py |
| POST | `/api/admin/transport/vehicles` | transport_fleet_edit | app/routers/transport.py |
| PATCH | `/api/admin/transport/vehicles/{vehicle_id}` | transport_fleet_edit | app/routers/transport.py |
| DELETE | `/api/admin/transport/vehicles/{vehicle_id}` | transport_fleet_edit | app/routers/transport.py |
| GET | `/api/admin/transport/drivers` | transport_dispatch_view | app/routers/transport.py |
| GET | `/api/admin/transport/drivers/full` | transport_dispatch_view | app/routers/transport.py |
| POST | `/api/admin/transport/drivers` | transport_fleet_edit | app/routers/transport.py |
| PATCH | `/api/admin/transport/drivers/{driver_id}` | transport_fleet_edit | app/routers/transport.py |
| DELETE | `/api/admin/transport/drivers/{driver_id}` | transport_fleet_edit | app/routers/transport.py |
| GET | `/api/admin/transport/types` | transport_dispatch_view | app/routers/transport.py |
| GET | `/api/admin/transport/available-sts` | transport_dispatch_view | app/routers/transport.py |
| GET | `/api/admin/transport/clusters` | transport_dispatch_view | app/routers/transport.py |
| POST | `/api/admin/transport/clusters/{raion}/create-task` | transport_dispatch_edit | app/routers/transport.py |
| GET | `/api/admin/transport/tasks/export.xlsx` | transport_dispatch_view | app/routers/transport.py |
| GET | `/api/admin/transport/tasks` | transport_dispatch_view | app/routers/transport.py |
| POST | `/api/admin/transport/tasks` | transport_dispatch_edit | app/routers/transport.py |
| GET | `/api/admin/transport/tasks/{task_id}` | transport_dispatch_view | app/routers/transport.py |
| PATCH | `/api/admin/transport/tasks/{task_id}` | transport_dispatch_edit | app/routers/transport.py |
| POST | `/api/admin/transport/tasks/{task_id}/close` | transport_dispatch_close | app/routers/transport.py |
| POST | `/api/admin/transport/tasks/{task_id}/cancel` | transport_dispatch_edit | app/routers/transport.py |
| GET | `/api/admin/transport/tasks/{task_id}/sts` | transport_dispatch_view | app/routers/transport.py |
| POST | `/api/admin/transport/tasks/{task_id}/sts` | transport_dispatch_edit | app/routers/transport.py |
| DELETE | `/api/admin/transport/tasks/{task_id}/sts/{st_number}` | transport_dispatch_edit | app/routers/transport.py |
| PATCH | `/api/admin/transport/tasks/{task_id}/sts/{st_number}/load-type` | transport_dispatch_edit | app/routers/transport.py |
| PATCH | `/api/admin/transport/tasks/{task_id}/sts/{st_number}/order` | transport_dispatch_edit | app/routers/transport.py |
| GET | `/api/admin/transport/sts/{st_number}/pallets` | transport_dispatch_view | app/routers/transport.py |
| GET | `/api/admin/transport/planner/orders` | transport_dispatch_view | app/routers/transport.py |
| GET | `/api/admin/transport/routing/status` | transport_dispatch_view | app/routers/transport.py |
| POST | `/api/admin/transport/distance-matrix/rebuild` | transport_dispatch_edit | app/routers/transport.py |
| POST | `/api/admin/transport/planner/solve` | transport_dispatch_edit | app/routers/transport.py |
| GET | `/api/admin/transport/planner/solve/{job_id}/stream` | transport_dispatch_edit | app/routers/transport.py |
| DELETE | `/api/admin/transport/planner/solve/{job_id}` | transport_dispatch_edit | app/routers/transport.py |
| POST | `/api/admin/transport/planner/apply` | transport_dispatch_edit | app/routers/transport.py |
| GET | `/api/admin/transport/planner/metrics` | transport_dispatch_view | app/routers/transport.py |
| GET | `/api/admin/transport/planner/templates` | transport_dispatch_view | app/routers/transport.py |
| GET | `/api/admin/transport/planner/history` | transport_dispatch_view | app/routers/transport.py |
| GET | `/api/admin/transport/planner/demand-forecast` | transport_dispatch_view | app/routers/transport.py |
| POST | `/api/admin/transport/tasks/{task_id}/plan-operations` | transport_dispatch_edit | app/routers/transport.py |
| GET | `/api/admin/transport/tasks/{task_id}/operations` | transport_dispatch_view | app/routers/transport.py |
| GET | `/api/admin/transport/vehicles/gantt` | transport_dispatch_view | app/routers/transport.py |
| GET | `/api/admin/transport/vehicles/available` | transport_dispatch_view | app/routers/transport.py |
| GET | `/api/admin/transport/plan-fact` | transport_dispatch_view | app/routers/transport.py |
| GET | `/api/admin/transport/billing/orders` | transport_dispatch_view | app/routers/transport.py |
| GET | `/api/admin/transport/billing/orders/export.xlsx` | transport_dispatch_view | app/routers/transport.py |
| POST | `/api/admin/transport/billing/orders` | edit_bill_tt | app/routers/transport.py |
| GET | `/api/admin/transport/billing/orders/{order_id}` | transport_dispatch_view | app/routers/transport.py |
| PATCH | `/api/admin/transport/billing/orders/{order_id}/close` | edit_bill_tt | app/routers/transport.py |
| PATCH | `/api/admin/transport/billing/orders/{order_id}/pay` | edit_bill_tt | app/routers/transport.py |
| GET | `/api/admin/transport/billing/orders/{order_id}/tasks` | transport_dispatch_view | app/routers/transport.py |
| GET | `/api/admin/transport/billing/orders/{order_id}/export.xlsx` | transport_dispatch_view | app/routers/transport.py |
| POST | `/api/admin/transport/billing/orders/{order_id}/tasks` | edit_bill_tt | app/routers/transport.py |
| GET | `/api/admin/transport/tasks/{task_id}/billing` | transport_dispatch_view | app/routers/transport.py |
| POST | `/api/admin/transport/tasks/{task_id}/billing/open` | edit_bill_tt | app/routers/transport.py |
| DELETE | `/api/admin/transport/billing/orders/{order_id}/tasks/{tt_id}` | edit_bill_tt | app/routers/transport.py |
| POST | `/api/admin/transport/tasks/{task_id}/recalculate-price` | calc_tt_price | app/routers/transport.py |
| PATCH | `/api/admin/transport/tasks/{task_id}/price` | create_tt_price | app/routers/transport.py |
| GET | `/api/admin/transport/billing/companies` | transport_dispatch_view | app/routers/transport.py |
| GET | `/api/admin/transport/ws/status` | transport_dispatch_view | app/routers/transport.py |
| GET | `/api/admin/transport/kpi/fleet` | transport_dispatch_view | app/routers/transport_kpi.py |
| GET | `/api/admin/transport/kpi/summary` | transport_dispatch_view | app/routers/transport_kpi.py |
| GET | `/api/admin/transport/kpi/regions` | transport_dispatch_view | app/routers/transport_kpi.py |
| GET | `/api/admin/transport/kpi/billing` | transport_dispatch_view | app/routers/transport_kpi.py |
| GET | `/api/admin/transport/kpi/billing/by-company` | transport_dispatch_view | app/routers/transport_kpi.py |
| GET | `/api/admin/transport/tariffs` | transport_dispatch_view | app/routers/transport_tariffs.py |
| GET | `/api/admin/transport/tariffs/table-info` | transport_dispatch_view | app/routers/transport_tariffs.py |

## `/api/admin/users`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/admin/users` | rights_admin_view | app/routers/users.py |
| GET | `/api/admin/users/groups` | rights_admin_view | app/routers/users.py |
| GET | `/api/admin/users/rights` | rights_admin_view | app/routers/users.py |
| POST | `/api/admin/users` | rights_admin_edit | app/routers/users.py |
| PATCH | `/api/admin/users/{login}` | rights_admin_edit | app/routers/users.py |
| DELETE | `/api/admin/users/{login}` | rights_admin_edit | app/routers/users.py |
| PATCH | `/api/admin/users/{login}/password` | rights_admin_edit | app/routers/users.py |
| POST | `/api/admin/users/groups/{group}/rights` | rights_admin_edit | app/routers/users.py |
| DELETE | `/api/admin/users/groups/{group}/rights/{right}` | rights_admin_edit | app/routers/users.py |
| POST | `/api/admin/users/groups` | rights_admin_edit | app/routers/users.py |

## `/api/admin/warehouse-map`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/admin/warehouse-map/warehouses/{ware_id}/canvases` | warehouse_topology_view | app/routers/warehouse_map.py |
| GET | `/api/admin/warehouse-map/warehouses/{ware_id}/state` | warehouse_topology_view | app/routers/warehouse_map.py |
| GET | `/api/admin/warehouse-map/canvases/{canvas_id}` | warehouse_topology_view | app/routers/warehouse_map.py |
| POST | `/api/admin/warehouse-map/canvases/{canvas_id}/archive` | warehouse_topology_edit | app/routers/warehouse_map.py |
| POST | `/api/admin/warehouse-map/warehouses/{ware_id}/canvases` | warehouse_topology_edit | app/routers/warehouse_map.py |
| POST | `/api/admin/warehouse-map/canvases/{canvas_id}/cameras` | warehouse_topology_edit | app/routers/warehouse_map.py |
| POST | `/api/admin/warehouse-map/cameras/{camera_id}/clone` | warehouse_topology_edit | app/routers/warehouse_map.py |
| POST | `/api/admin/warehouse-map/cameras/{camera_id}/archive` | warehouse_topology_edit | app/routers/warehouse_map.py |
| PATCH | `/api/admin/warehouse-map/cameras/{camera_id}/objects` | warehouse_topology_edit | app/routers/warehouse_map.py |
| PATCH | `/api/admin/warehouse-map/cameras/{camera_id}/passages` | warehouse_topology_edit | app/routers/warehouse_map.py |
| PATCH | `/api/admin/warehouse-map/canvases/{canvas_id}/camera-links` | warehouse_topology_edit | app/routers/warehouse_map.py |

## `/api/admin/warehouse-map-drafts`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/admin/warehouse-map-drafts` | warehouse_topology_view | app/routers/warehouse_map_drafts.py |
| POST | `/api/admin/warehouse-map-drafts` | warehouse_topology_edit | app/routers/warehouse_map_drafts.py |
| POST | `/api/admin/warehouse-map-drafts/load-from-db` | warehouse_topology_edit | app/routers/warehouse_map_drafts.py |
| GET | `/api/admin/warehouse-map-drafts/{draft_id}` | warehouse_topology_view | app/routers/warehouse_map_drafts.py |
| PATCH | `/api/admin/warehouse-map-drafts/{draft_id}/cells` | warehouse_topology_edit | app/routers/warehouse_map_drafts.py |
| GET | `/api/admin/warehouse-map-drafts/{draft_id}/diff` | warehouse_topology_view | app/routers/warehouse_map_drafts.py |
| POST | `/api/admin/warehouse-map-drafts/{draft_id}/save-to-db` | warehouse_topology_edit | app/routers/warehouse_map_drafts.py |
| PATCH | `/api/admin/warehouse-map-drafts/{draft_id}/metadata` | warehouse_topology_edit | app/routers/warehouse_map_drafts.py |
| POST | `/api/admin/warehouse-map-drafts/{draft_id}/route/build` | warehouse_topology_edit | app/routers/warehouse_map_drafts.py |
| PATCH | `/api/admin/warehouse-map-drafts/{draft_id}/route` | warehouse_topology_edit | app/routers/warehouse_map_drafts.py |
| POST | `/api/admin/warehouse-map-drafts/{draft_id}/route/save-to-db` | warehouse_topology_edit | app/routers/warehouse_map_drafts.py |
| POST | `/api/admin/warehouse-map-drafts/{draft_id}/publish-oracle` | warehouse_topology_edit | app/routers/warehouse_map_drafts.py |
| POST | `/api/admin/warehouse-map-drafts/{draft_id}/bulk-role` | warehouse_topology_edit | app/routers/warehouse_map_drafts.py |
| POST | `/api/admin/warehouse-map-drafts/{draft_id}/pick-face-addresses/generate` | warehouse_topology_edit | app/routers/warehouse_map_drafts.py |
| POST | `/api/admin/warehouse-map-drafts/{draft_id}/small-pick-faces/generate` | warehouse_topology_edit | app/routers/warehouse_map_drafts.py |
| PATCH | `/api/admin/warehouse-map-drafts/{draft_id}/small-pick-faces/{small_pick_face_id}` | warehouse_topology_edit | app/routers/warehouse_map_drafts.py |
| POST | `/api/admin/warehouse-map-drafts/{draft_id}/small-pick-faces/renumber` | warehouse_topology_edit | app/routers/warehouse_map_drafts.py |
| POST | `/api/admin/warehouse-map-drafts/{draft_id}/storage-slots/generate` | warehouse_topology_edit | app/routers/warehouse_map_drafts.py |
| PATCH | `/api/admin/warehouse-map-drafts/{draft_id}/storage-slots/{storage_slot_id}` | warehouse_topology_edit | app/routers/warehouse_map_drafts.py |
| POST | `/api/admin/warehouse-map-drafts/{draft_id}/validate` | warehouse_topology_view | app/routers/warehouse_map_drafts.py |
| POST | `/api/admin/warehouse-map-drafts/{draft_id}/projection/preview` | warehouse_topology_view | app/routers/warehouse_map_drafts.py |
| POST | `/api/admin/warehouse-map-drafts/{draft_id}/projection/save-to-topology` | warehouse_topology_edit | app/routers/warehouse_map_drafts.py |
| POST | `/api/admin/warehouse-map-drafts/{draft_id}/publish` | warehouse_topology_edit | app/routers/warehouse_map_drafts.py |

## `/api/admin/warehouse-topologies`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/admin/warehouse-topologies` | warehouse_topology_view | app/routers/warehouse_topology.py |
| POST | `/api/admin/warehouse-topologies` | warehouse_topology_edit | app/routers/warehouse_topology.py |
| GET | `/api/admin/warehouse-topologies/{topology_id}/map` | warehouse_topology_view | app/routers/warehouse_topology.py |
| POST | `/api/admin/warehouse-topologies/{topology_id}/generate-cells` | warehouse_topology_edit | app/routers/warehouse_topology.py |
| POST | `/api/admin/warehouse-topologies/{topology_id}/generate-gates` | warehouse_topology_edit | app/routers/warehouse_topology.py |
| POST | `/api/admin/warehouse-topologies/{topology_id}/distances/recalculate` | warehouse_topology_edit | app/routers/warehouse_topology.py |
| POST | `/api/admin/warehouse-topologies/{topology_id}/validate` | warehouse_topology_view | app/routers/warehouse_topology.py |
| POST | `/api/admin/warehouse-topologies/{topology_id}/normalize-cell-codes` | warehouse_topology_edit | app/routers/warehouse_topology.py |
| POST | `/api/admin/warehouse-topologies/{topology_id}/publish` | warehouse_topology_publish | app/routers/warehouse_topology.py |

## `/api/admin/warehouses`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/admin/warehouses` | warehouse_settings_view | app/routers/warehouses.py |
| PATCH | `/api/admin/warehouses/{ware_id}` | warehouse_settings_edit | app/routers/warehouses.py |

## `/api/aggregations/{aggregation_id}`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/aggregations/{aggregation_id}/items` | — | app/routers/production.py |

## `/api/bom`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/bom` | bom_view | app/routers/bom.py |
| POST | `/api/bom` | bom_edit | app/routers/bom.py |

## `/api/bom/default`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/bom/default` | bom_view | app/routers/bom.py |

## `/api/bom/{bom_id}`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/bom/{bom_id}` | bom_view | app/routers/bom.py |
| PATCH | `/api/bom/{bom_id}` | bom_edit | app/routers/bom.py |
| POST | `/api/bom/{bom_id}/lines` | bom_edit | app/routers/bom.py |
| PATCH | `/api/bom/{bom_id}/lines/{line_id}` | bom_edit | app/routers/bom.py |
| DELETE | `/api/bom/{bom_id}/lines/{line_id}` | bom_edit | app/routers/bom.py |
| POST | `/api/bom/{bom_id}/approve` | bom_approve | app/routers/bom.py |
| POST | `/api/bom/{bom_id}/block` | bom_block | app/routers/bom.py |
| POST | `/api/bom/{bom_id}/archive` | bom_block | app/routers/bom.py |
| POST | `/api/bom/{bom_id}/make-primary` | bom_make_primary | app/routers/bom.py |
| POST | `/api/bom/{bom_id}/clone` | bom_edit | app/routers/bom.py |
| POST | `/api/bom/{bom_id}/calculate` | bom_view | app/routers/bom.py |

## `/api/case-pick/pallet-types`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/case-pick/pallet-types` | case_pick_view | app/routers/case_pick.py |
| POST | `/api/case-pick/pallet-types` | case_pick_manage | app/routers/case_pick.py |

## `/api/case-pick/shorts`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/case-pick/shorts/{short}/weight-preview` | case_pick_short_approve | app/modules/inventory/api/weighted_case_routes.py |
| GET | `/api/case-pick/shorts` | case_pick_view | app/routers/case_pick.py |
| POST | `/api/case-pick/shorts/{short_id}/approve` | case_pick_short_approve | app/routers/case_pick.py |
| POST | `/api/case-pick/shorts/{short_id}/reject` | case_pick_short_approve | app/routers/case_pick.py |

## `/api/case-pick/tasks`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/case-pick/tasks/{task}/sscc-label` | case_pick_execute | app/modules/inventory/api/case_label_routes.py |
| GET | `/api/case-pick/tasks/{task}/sscc-label` | case_pick_execute | app/modules/inventory/api/case_label_routes.py |
| POST | `/api/case-pick/tasks/{task}/sscc-label/confirm` | case_pick_execute | app/modules/inventory/api/case_label_routes.py |
| GET | `/api/case-pick/tasks/{task}/sscc-label/document` | case_pick_execute | app/modules/inventory/api/case_label_routes.py |
| GET | `/api/case-pick/tasks/{task_id}/pallet-type` | case_pick_view | app/modules/inventory/api/case_type_routes.py |
| POST | `/api/case-pick/tasks/{task_id}/pallet-type` | case_pick_execute | app/modules/inventory/api/case_type_routes.py |
| GET | `/api/case-pick/tasks/{task_id}/partial-shipment-layout` | case_pick_short_approve | app/modules/inventory/api/partial_shipment_routes.py |
| POST | `/api/case-pick/tasks/{task_id}/partial-shipment-layout` | case_pick_short_approve | app/modules/inventory/api/partial_shipment_routes.py |
| POST | `/api/case-pick/tasks/{task}/lines/{line}/weighted-box` | case_pick_execute | app/modules/inventory/api/weighted_case_routes.py |
| POST | `/api/case-pick/tasks/{task}/lines/{line}/weigh-line` | case_pick_execute | app/modules/inventory/api/weighted_case_routes.py |
| GET | `/api/case-pick/tasks/{task}/lines/{line}/order-weight-preview` | case_pick_execute | app/modules/inventory/api/weighted_case_routes.py |
| GET | `/api/case-pick/tasks` | case_pick_view | app/routers/case_pick.py |
| GET | `/api/case-pick/tasks/{case_pick_task_id}` | case_pick_view | app/routers/case_pick.py |
| POST | `/api/case-pick/tasks/{case_pick_task_id}/claim` | case_pick_execute | app/routers/case_pick.py |
| POST | `/api/case-pick/tasks/{case_pick_task_id}/start` | case_pick_execute | app/routers/case_pick.py |
| POST | `/api/case-pick/tasks/{case_pick_task_id}/transfer` | case_pick_manage | app/routers/case_pick.py |
| POST | `/api/case-pick/tasks/{case_pick_task_id}/move-carrier` | case_pick_execute | app/routers/case_pick.py |
| GET | `/api/case-pick/tasks/{case_pick_task_id}/lines/{line_id}/marking-policy` | case_pick_execute | app/routers/case_pick.py |
| POST | `/api/case-pick/tasks/{case_pick_task_id}/lines/{line_id}/confirm` | case_pick_execute | app/routers/case_pick.py |
| POST | `/api/case-pick/tasks/{case_pick_task_id}/lines/{line_id}/short` | case_pick_execute | app/routers/case_pick.py |
| POST | `/api/case-pick/tasks/{case_pick_task_id}/close-pallet` | case_pick_execute | app/routers/case_pick.py |
| POST | `/api/case-pick/tasks/{case_pick_task_id}/bind-shipment` | case_pick_execute | app/routers/case_pick.py |
| POST | `/api/case-pick/tasks/{case_pick_task_id}/return-carrier` | case_pick_manage | app/routers/case_pick.py |

## `/api/case-pick/waves`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/case-pick/waves/{pick_wave_id}/ensure` | case_pick_manage | app/routers/case_pick.py |

## `/api/crpt-codes/status`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/crpt-codes/status` | — | app/routers/production.py |

## `/api/customer-orders`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/customer-orders` | customer_order_view | app/routers/customer_orders.py |

## `/api/customer-orders/import-legacy`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/customer-orders/import-legacy/{legacy_order_id}` | customer_order_import | app/routers/customer_orders.py |

## `/api/customer-orders/{customer_order_id}`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/customer-orders/{customer_order_id}` | customer_order_view | app/routers/customer_orders.py |
| GET | `/api/customer-orders/{customer_order_id}/fulfillment` | customer_fulfillment_view | app/routers/customer_orders.py |

## `/api/customer-orders/{order_id}`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/customer-orders/{order_id}/delivery` | customer_fulfillment_view | app/modules/delivery/api/order_delivery_routes.py |
| GET | `/api/customer-orders/{order_id}/execution` | customer_fulfillment_view | app/modules/fulfillment/api/execution_routes.py |
| GET | `/api/customer-orders/{order_id}/prepared-layout` | customer_order_view | app/modules/fulfillment/api/prepared_layout_routes.py |
| POST | `/api/customer-orders/{order_id}/prepared-layout/preview` | customer_order_view | app/modules/fulfillment/api/prepared_layout_routes.py |
| POST | `/api/customer-orders/{order_id}/prepared-layout/move-row` | outgoing_pallet_edit | app/modules/fulfillment/api/prepared_layout_routes.py |

## `/api/customers`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/customers` | customer_view | app/routers/customer_orders.py |
| POST | `/api/customers` | customer_edit | app/routers/customer_orders.py |

## `/api/customers/{customer_id}`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/customers/{customer_id}` | customer_view | app/routers/customer_orders.py |
| PATCH | `/api/customers/{customer_id}` | customer_edit | app/routers/customer_orders.py |
| POST | `/api/customers/{customer_id}/addresses` | customer_edit | app/routers/customer_orders.py |
| GET | `/api/customers/{customer_id}/product-rules` | customer_rule_view | app/routers/customer_rules.py |
| POST | `/api/customers/{customer_id}/product-rules` | customer_rule_edit | app/routers/customer_rules.py |
| GET | `/api/customers/{customer_id}/shelf-life-rules` | customer_rule_view | app/routers/customer_rules.py |
| POST | `/api/customers/{customer_id}/shelf-life-rules` | customer_rule_edit | app/routers/customer_rules.py |
| GET | `/api/customers/{customer_id}/stack-rules` | customer_rule_view | app/routers/customer_rules.py |
| POST | `/api/customers/{customer_id}/stack-rules` | customer_rule_edit | app/routers/customer_rules.py |
| GET | `/api/customers/{customer_id}/vehicle-rules` | customer_rule_view | app/routers/customer_rules.py |
| POST | `/api/customers/{customer_id}/vehicle-rules` | customer_rule_edit | app/routers/customer_rules.py |

## `/api/delivery/case-work`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/delivery/case-work/{case_id}/assign` | store_case_manage | app/modules/delivery/api/case_work_routes.py |
| POST | `/api/delivery/case-work/{case_id}/finding` | store_case_investigate | app/modules/delivery/api/case_work_routes.py |
| POST | `/api/delivery/case-work/{case_id}/loss` | store_loss_confirm | app/modules/delivery/api/case_work_routes.py |
| GET | `/api/delivery/case-work/mine` | store_case_investigate | app/modules/delivery/api/case_work_routes.py |
| GET | `/api/delivery/case-work/{case_id}/investigation` | store_case_investigate | app/modules/delivery/api/case_work_routes.py |
| GET | `/api/delivery/case-work/{case_id}/loss-review` | store_loss_confirm | app/modules/delivery/api/case_work_routes.py |
| GET | `/api/delivery/case-work/{case_id}/management` | store_case_manage | app/modules/delivery/api/case_work_routes.py |
| POST | `/api/delivery/case-work/{case_id}/close` | store_loss_confirm | app/modules/delivery/api/case_work_routes.py |

## `/api/delivery/store-photos`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/delivery/store-photos/upload` | store_receipt_confirm | app/modules/delivery/api/store_evidence_routes.py |
| GET | `/api/delivery/store-photos/list` | store_receipt_confirm | app/modules/delivery/api/store_evidence_routes.py |
| GET | `/api/delivery/store-photos/{photo_id}/content` | store_receipt_confirm | app/modules/delivery/api/store_evidence_routes.py |

## `/api/delivery/store-receipts`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/delivery/store-receipts/preview` | store_receipt_confirm | app/modules/delivery/api/store_receipt_routes.py |
| GET | `/api/delivery/store-receipts/trips/{trip_id}/places` | store_receipt_confirm | app/modules/delivery/api/store_receipt_routes.py |
| POST | `/api/delivery/store-receipts/confirm` | store_receipt_confirm | app/modules/delivery/api/store_receipt_routes.py |
| PUT | `/api/delivery/store-receipts/policy` | warehouse_settings_edit | app/modules/delivery/api/store_receipt_routes.py |
| POST | `/api/delivery/store-receipts/receivers` | warehouse_settings_edit | app/modules/delivery/api/store_receipt_routes.py |
| GET | `/api/delivery/store-receipts/cases` | transport_dispatch_view | app/modules/delivery/api/store_receipt_routes.py |
| GET | `/api/delivery/store-receipts/cases/{case_id}` | transport_dispatch_view | app/modules/delivery/api/store_receipt_routes.py |
| POST | `/api/delivery/store-receipts/load-custody/release` | transport_dispatch_close | app/modules/delivery/api/store_receipt_routes.py |
| POST | `/api/delivery/store-receipts/unloading/start` | store_receipt_confirm | app/modules/delivery/api/store_receipt_routes.py |
| GET | `/api/delivery/store-receipts/unloading` | store_receipt_confirm | app/modules/delivery/api/store_receipt_routes.py |

## `/api/delivery/store-return-custody`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/delivery/store-return-custody/handover` | store_return_handover | app/modules/delivery/api/return_custody_routes.py |
| POST | `/api/delivery/store-return-custody/pickup` | driver_return_accept | app/modules/delivery/api/return_custody_routes.py |
| GET | `/api/delivery/store-return-custody/store` | store_return_handover | app/modules/delivery/api/return_custody_routes.py |
| GET | `/api/delivery/store-return-custody/driver` | driver_return_accept | app/modules/delivery/api/return_custody_routes.py |

## `/api/delivery/store-return-transport`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/delivery/store-return-transport/plan` | store_return_transport | app/modules/delivery/api/return_transport_routes.py |
| GET | `/api/delivery/store-return-transport/eligible` | store_return_transport | app/modules/delivery/api/return_transport_routes.py |
| GET | `/api/delivery/store-return-transport/trips/{task_id}` | store_return_transport | app/modules/delivery/api/return_transport_routes.py |

## `/api/delivery/store-returns`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/delivery/store-returns/{receipt_id}/approve` | store_return_approve | app/modules/delivery/api/store_return_routes.py |
| GET | `/api/delivery/store-returns/{receipt_id}` | store_return_approve | app/modules/delivery/api/store_return_routes.py |
| GET | `/api/delivery/store-returns/{receipt_id}/reuse-preview` | store_return_approve | app/modules/delivery/api/store_return_routes.py |

## `/api/delivery/store-scales`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| PUT | `/api/delivery/store-scales/devices/{device_id}` | warehouse_settings_edit | app/modules/delivery/api/store_scale_routes.py |
| POST | `/api/delivery/store-scales/captures` | store_scale_ingest | app/modules/delivery/api/store_scale_routes.py |
| GET | `/api/delivery/store-scales/captures/{capture_key}` | store_receipt_confirm | app/modules/delivery/api/store_scale_routes.py |
| GET | `/api/delivery/store-scales/captures` | store_receipt_confirm | app/modules/delivery/api/store_scale_routes.py |

## `/api/driver/ops`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/driver/ops/{op_id}/start` | dep: driver_workspace_service, get_current_user | app/modules/transport/api/driver_workspace_routes.py |
| POST | `/api/driver/ops/{op_id}/done` | dep: driver_workspace_service, get_current_user | app/modules/transport/api/driver_workspace_routes.py |

## `/api/driver/trips`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/driver/trips` | dep: driver_workspace_service, get_current_user | app/modules/transport/api/driver_workspace_routes.py |
| GET | `/api/driver/trips/{task_id}/sts` | dep: driver_workspace_service, get_current_user | app/modules/transport/api/driver_workspace_routes.py |
| GET | `/api/driver/trips/{task_id}/ops` | dep: driver_workspace_service, get_current_user | app/modules/transport/api/driver_workspace_routes.py |

## `/api/finance/day-reconciliation`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/finance/day-reconciliation/warehouses/{ware_id}` | transport_dispatch_view | app/modules/finance/api/day_reconciliation_routes.py |
| GET | `/api/finance/day-reconciliation/warehouses/{ware_id}/stock-conflicts` | transport_dispatch_view | app/modules/finance/api/day_reconciliation_routes.py |
| GET | `/api/finance/day-reconciliation/warehouses/{ware_id}/review-context` | transport_dispatch_view | app/modules/finance/api/day_review_routes.py |
| POST | `/api/finance/day-reconciliation/reviews` | transport_dispatch_edit | app/modules/finance/api/day_review_routes.py |
| POST | `/api/finance/day-reconciliation/reviews/resolve` | transport_dispatch_edit | app/modules/finance/api/day_review_routes.py |
| GET | `/api/finance/day-reconciliation/reviews/warehouses/{ware_id}/history` | transport_dispatch_view | app/modules/finance/api/day_review_routes.py |
| GET | `/api/finance/day-reconciliation/reviews/{operation}` | transport_dispatch_view | app/modules/finance/api/day_review_routes.py |
| GET | `/api/finance/day-reconciliation/warehouses/{ware_id}/shipping-register` | transport_dispatch_view | app/modules/finance/api/day_review_routes.py |
| GET | `/api/finance/day-reconciliation/reviews/{review_id}/shipping-inspections` | transport_dispatch_view | app/modules/finance/api/day_review_routes.py |
| POST | `/api/finance/day-reconciliation/shipping-inspections` | transport_dispatch_view | app/modules/finance/api/day_review_routes.py |
| POST | `/api/finance/day-reconciliation/shipping-inspections/resolve` | transport_dispatch_view | app/modules/finance/api/day_review_routes.py |

## `/api/finance/expense-allocation`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/finance/expense-allocation` | calc_tt_price | app/modules/finance/api/expense_allocation_routes.py |
| GET | `/api/finance/expense-allocation/billing-orders/{invoice_id}` | transport_dispatch_view | app/modules/finance/api/expense_allocation_routes.py |

## `/api/finance/logistics-costs`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/finance/logistics-costs/rates` | create_tt_price | app/modules/finance/api/logistics_cost_routes.py |
| POST | `/api/finance/logistics-costs/rates/monthly` | create_tt_price | app/modules/finance/api/logistics_cost_routes.py |
| GET | `/api/finance/logistics-costs/warehouses/{ware_id}/rates` | transport_dispatch_view | app/modules/finance/api/logistics_cost_routes.py |
| GET | `/api/finance/logistics-costs/warehouses/{ware_id}/rates/history` | transport_dispatch_view | app/modules/finance/api/logistics_cost_routes.py |
| POST | `/api/finance/logistics-costs/calculate` | calc_tt_price | app/modules/finance/api/logistics_cost_routes.py |
| GET | `/api/finance/logistics-costs/trips/{trip_id}` | transport_dispatch_view | app/modules/finance/api/logistics_cost_routes.py |
| GET | `/api/finance/logistics-costs/billing-orders/{invoice_id}` | transport_dispatch_view | app/modules/finance/api/logistics_cost_routes.py |
| GET | `/api/finance/logistics-costs/trips/{trip_id}/assembly-period` | transport_dispatch_view | app/modules/finance/api/logistics_cost_routes.py |
| GET | `/api/finance/logistics-costs/warehouses/{ware_id}/period-policy` | transport_dispatch_view | app/modules/finance/api/logistics_cost_routes.py |
| POST | `/api/finance/logistics-costs/warehouses/{ware_id}/period-policy` | create_tt_price | app/modules/finance/api/logistics_cost_routes.py |
| GET | `/api/finance/logistics-costs/billing-orders/{invoice_id}/summary` | transport_dispatch_view | app/modules/finance/api/logistics_cost_routes.py |
| GET | `/api/finance/logistics-costs/trips/{trip_id}/transport-tariff-sources` | transport_dispatch_view | app/modules/finance/api/logistics_cost_routes.py |
| POST | `/api/finance/logistics-costs/transport-norms` | create_tt_price | app/modules/finance/api/logistics_cost_routes.py |
| GET | `/api/finance/logistics-costs/warehouses/{ware_id}/transport-norms/{source_price_id}/history` | transport_dispatch_view | app/modules/finance/api/logistics_cost_routes.py |
| GET | `/api/finance/logistics-costs/trips/{trip_id}/transport-cost-facts` | transport_dispatch_view | app/modules/finance/api/logistics_cost_routes.py |
| GET | `/api/finance/logistics-costs/trips/{trip_id}/transport-cost-preview` | transport_dispatch_view | app/modules/finance/api/logistics_cost_routes.py |
| POST | `/api/finance/logistics-costs/transport-costs/conduct` | calc_tt_price | app/modules/finance/api/logistics_cost_routes.py |
| GET | `/api/finance/logistics-costs/trips/{trip_id}/transport-costs` | transport_dispatch_view | app/modules/finance/api/logistics_cost_routes.py |
| GET | `/api/finance/logistics-costs/billing-orders/{invoice_id}/transport-costs` | transport_dispatch_view | app/modules/finance/api/logistics_cost_routes.py |

## `/api/finance/logistics-expenses`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/finance/logistics-expenses/articles` | transport_dispatch_view | app/modules/finance/api/logistics_expense_routes.py |
| POST | `/api/finance/logistics-expenses/articles` | create_tt_price | app/modules/finance/api/logistics_expense_routes.py |
| POST | `/api/finance/logistics-expenses/report` | dep: get_current_user, logistics_expense_service | app/modules/finance/api/logistics_expense_routes.py |
| POST | `/api/finance/logistics-expenses/decide` | dep: get_current_user, logistics_expense_service | app/modules/finance/api/logistics_expense_routes.py |
| GET | `/api/finance/logistics-expenses/warehouses/{ware_id}` | transport_dispatch_view | app/modules/finance/api/logistics_expense_routes.py |
| GET | `/api/finance/logistics-expenses/warehouses/{ware_id}/normative-costs` | transport_dispatch_view | app/modules/finance/api/logistics_expense_routes.py |

## `/api/finished-goods/batches`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/finished-goods/batches` | finished_goods_batch_view | app/routers/finished_goods.py |

## `/api/finished-goods/remains`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/finished-goods/remains` | finished_goods_stock_view | app/routers/finished_goods.py |

## `/api/finished-goods/skus`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/finished-goods/skus/{articul}/receiving-policy` | finished_goods_view | app/modules/master_data/api/routes.py |
| PUT | `/api/finished-goods/skus/{articul}/receiving-policy` | finished_goods_edit | app/modules/master_data/api/routes.py |
| GET | `/api/finished-goods/skus` | finished_goods_view | app/routers/finished_goods.py |
| PATCH | `/api/finished-goods/skus/{articul}` | finished_goods_edit | app/routers/finished_goods.py |

## `/api/finished-goods/warehouses`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/finished-goods/warehouses` | finished_goods_view | app/routers/finished_goods.py |

## `/api/gps/track`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/gps/track` | — | app/routers/gps.py |

## `/api/integrations/regulatory`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/integrations/regulatory/runtime` | external_outbox_view | app/modules/integrations/api/regulatory_runtime_routes.py |

## `/api/integrations/sap`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/integrations/sap/store-orders/{order_id}/preparation-readiness` | customer_order_view | app/modules/fulfillment/api/preparation_read_routes.py |
| POST | `/api/integrations/sap/store-orders/{order_id}/preparation-layout` | customer_order_view | app/modules/fulfillment/api/preparation_read_routes.py |
| POST | `/api/integrations/sap/store-orders/{order_id}/automatic-layout` | customer_order_view | app/modules/fulfillment/api/preparation_read_routes.py |
| POST | `/api/integrations/sap/store-orders/{order_id}/prepare-st/automatic` | customer_order_import | app/modules/fulfillment/api/preparation_read_routes.py |
| POST | `/api/integrations/sap/store-orders/{order_id}/prepare-st/automatic/resolve` | customer_order_import | app/modules/fulfillment/api/preparation_read_routes.py |
| POST | `/api/integrations/sap/store-decisions` | sap_store_decision_import | app/modules/fulfillment/api/store_decision_routes.py |
| GET | `/api/integrations/sap/receipt-events` | sap_supply_view | app/modules/integrations/api/receipt_event_routes.py |
| POST | `/api/integrations/sap/receipt-events/acknowledgements` | sap_supply_import | app/modules/integrations/api/receipt_event_routes.py |
| POST | `/api/integrations/sap/receipt-events/{event_id}/retry` | sap_supply_import | app/modules/integrations/api/receipt_event_routes.py |
| POST | `/api/integrations/sap/artmas` | sap_article_import | app/modules/integrations/api/routes.py |
| GET | `/api/integrations/sap/artmas/{inbox_id}` | sap_article_import | app/modules/integrations/api/routes.py |
| POST | `/api/integrations/sap/store-returns` | sap_return_import | app/modules/integrations/api/store_return_routes.py |
| POST | `/api/integrations/sap/supply-orders` | sap_supply_import | app/modules/integrations/api/supply_routes.py |
| GET | `/api/integrations/sap/supply-orders` | sap_supply_view | app/modules/integrations/api/supply_routes.py |
| GET | `/api/integrations/sap/supply-orders/by-receipt-document/{document_id}` | sap_supply_view | app/modules/integrations/api/supply_routes.py |
| GET | `/api/integrations/sap/supply-orders/{order_id}` | sap_supply_view | app/modules/integrations/api/supply_routes.py |
| POST | `/api/integrations/sap/supply-orders/{order_id}/pallet-plan` | sap_supply_view | app/modules/integrations/api/supply_routes.py |
| GET | `/api/integrations/sap/supply-orders/{order_id}/receipt-history` | sap_supply_view | app/modules/integrations/api/supply_routes.py |

## `/api/inventory/cctv-viewpoints`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| PUT | `/api/inventory/cctv-viewpoints` | warehouse_settings_edit | app/modules/inventory/api/investigation_routes.py |
| GET | `/api/inventory/cctv-viewpoints` | warehouse_settings_edit | app/modules/inventory/api/investigation_routes.py |

## `/api/inventory/interwarehouse`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/inventory/interwarehouse/source-loads/{load_id}/group-composition` | transport_dispatch_edit | app/modules/inventory/api/interwarehouse_routes.py |
| GET | `/api/inventory/interwarehouse/group-warehouses/{ware_id}` | transport_dispatch_view | app/modules/inventory/api/interwarehouse_routes.py |
| GET | `/api/inventory/interwarehouse/group-plans/{plan_id}` | transport_dispatch_view | app/modules/inventory/api/interwarehouse_routes.py |
| GET | `/api/inventory/interwarehouse/source-loads/{load_id}/group-proof` | transport_dispatch_edit | app/modules/inventory/api/interwarehouse_routes.py |
| POST | `/api/inventory/interwarehouse/group-plan` | transport_dispatch_edit | app/modules/inventory/api/interwarehouse_routes.py |
| POST | `/api/inventory/interwarehouse/plan` | transport_dispatch_edit | app/modules/inventory/api/interwarehouse_routes.py |
| GET | `/api/inventory/interwarehouse/warehouses/{ware_id}` | transport_dispatch_view | app/modules/inventory/api/interwarehouse_routes.py |
| POST | `/api/inventory/interwarehouse/unload` | interwarehouse_receive | app/modules/inventory/api/interwarehouse_routes.py |
| POST | `/api/inventory/interwarehouse/receive` | interwarehouse_receive | app/modules/inventory/api/interwarehouse_routes.py |
| POST | `/api/inventory/interwarehouse/group-receive` | interwarehouse_receive | app/modules/inventory/api/interwarehouse_routes.py |
| POST | `/api/inventory/interwarehouse/group-placement` | warehouse_task_execute | app/modules/inventory/api/interwarehouse_routes.py |
| POST | `/api/inventory/interwarehouse/group-onward` | outgoing_pallet_edit | app/modules/inventory/api/interwarehouse_routes.py |
| POST | `/api/inventory/interwarehouse/placement` | interwarehouse_receive | app/modules/inventory/api/interwarehouse_routes.py |
| POST | `/api/inventory/interwarehouse/release-custody` | interwarehouse_receive | app/modules/inventory/api/interwarehouse_routes.py |
| POST | `/api/inventory/interwarehouse/prepare-onward` | outgoing_pallet_edit | app/modules/inventory/api/interwarehouse_routes.py |
| GET | `/api/inventory/interwarehouse/plans/{plan_id}/units` | interwarehouse_receive | app/modules/inventory/api/interwarehouse_routes.py |
| POST | `/api/inventory/interwarehouse/decisions` | transport_dispatch_edit | app/modules/inventory/api/interwarehouse_routes.py |
| POST | `/api/inventory/interwarehouse/temperature-decisions` | transport_dispatch_edit | app/modules/inventory/api/interwarehouse_routes.py |
| GET | `/api/inventory/interwarehouse/trips/{trip_id}/incoming` | transport_dispatch_view | app/modules/inventory/api/interwarehouse_routes.py |
| GET | `/api/inventory/interwarehouse/plans/{plan_id}/decisions` | transport_dispatch_view | app/modules/inventory/api/interwarehouse_routes.py |
| POST | `/api/inventory/interwarehouse/incident-closures` | transport_dispatch_edit | app/modules/inventory/api/interwarehouse_routes.py |
| GET | `/api/inventory/interwarehouse/receipts/{receipt_id}/shortage` | transport_dispatch_view | app/modules/inventory/api/interwarehouse_routes.py |
| POST | `/api/inventory/interwarehouse/shortage-reports` | transport_dispatch_edit | app/modules/inventory/api/interwarehouse_routes.py |
| POST | `/api/inventory/interwarehouse/shortage-confirmations` | store_return_approve | app/modules/inventory/api/interwarehouse_routes.py |
| POST | `/api/inventory/interwarehouse/recovery-reports` | transport_dispatch_edit | app/modules/inventory/api/interwarehouse_routes.py |
| POST | `/api/inventory/interwarehouse/recovery-approvals` | store_return_approve | app/modules/inventory/api/interwarehouse_routes.py |
| POST | `/api/inventory/interwarehouse/recovery-receipts` | interwarehouse_receive | app/modules/inventory/api/interwarehouse_routes.py |
| POST | `/api/inventory/interwarehouse/recovery-placement` | interwarehouse_receive | app/modules/inventory/api/interwarehouse_routes.py |
| POST | `/api/inventory/interwarehouse/prepare-recovery-onward` | transport_dispatch_edit | app/modules/inventory/api/interwarehouse_routes.py |
| POST | `/api/inventory/interwarehouse/recovery-cancellations` | store_return_approve | app/modules/inventory/api/interwarehouse_routes.py |

## `/api/inventory/minimax`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/inventory/minimax/{warehouse}` | pick_wave_view | app/modules/inventory/api/minimax_routes.py |
| POST | `/api/inventory/minimax/{warehouse}/reconcile` | pick_wave_launch | app/modules/inventory/api/minimax_routes.py |

## `/api/inventory/pallet-floor-types`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/inventory/pallet-floor-types` | stock_posting_shipping | app/modules/inventory/api/pallet_floor_routes.py |
| POST | `/api/inventory/pallet-floor-types` | stock_posting_shipping | app/modules/inventory/api/pallet_floor_routes.py |

## `/api/inventory/quality-policies`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/inventory/quality-policies/warehouses/{warehouse}` | warehouse_settings_view | app/modules/inventory/api/quality_scope_routes.py |
| POST | `/api/inventory/quality-policies/warehouses/{warehouse}` | warehouse_settings_edit | app/modules/inventory/api/quality_scope_routes.py |

## `/api/inventory/recovery-shorts`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/inventory/recovery-shorts` | case_pick_view | app/modules/inventory/api/recovery_routes.py |

## `/api/inventory/replenishment-progress`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/inventory/replenishment-progress` | pick_wave_view | app/modules/inventory/api/replenishment_progress_routes.py |

## `/api/inventory/return-disposal`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/inventory/return-disposal/report` | warehouse_return_dispatch | app/modules/inventory/api/return_disposal_routes.py |
| POST | `/api/inventory/return-disposal/dispose` | store_return_approve | app/modules/inventory/api/return_disposal_routes.py |
| GET | `/api/inventory/return-disposal/warehouses/{ware_id}` | warehouse_return_dispatch | app/modules/inventory/api/return_disposal_routes.py |

## `/api/inventory/shorts`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/inventory/shorts/{short_id}/investigation` | inventory_task_view | app/modules/inventory/api/investigation_routes.py |
| POST | `/api/inventory/shorts/{short_id}/investigation` | case_pick_short_approve | app/modules/inventory/api/investigation_routes.py |

## `/api/inventory/slotting`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/inventory/slotting/warehouses/{ware_id}/articles/{article}/recommendations` | pick_topology_edit | app/modules/inventory/api/range_proposal_routes.py |
| GET | `/api/inventory/slotting/warehouses/{ware_id}/articles/{article}/recommendations/{proposal_id}` | pick_topology_view | app/modules/inventory/api/range_proposal_routes.py |
| POST | `/api/inventory/slotting/warehouses/{ware_id}/articles/{article}/recommendations/{proposal_id}/cancel` | pick_topology_edit | app/modules/inventory/api/range_proposal_routes.py |
| POST | `/api/inventory/slotting/warehouses/{ware_id}/articles/{article}/recommendations/{proposal_id}/approve` | pick_topology_edit | app/modules/inventory/api/range_proposal_routes.py |
| POST | `/api/inventory/slotting/warehouses/{ware_id}/articles/{article}/recommendations/actions/close-drain` | pick_topology_edit | app/modules/inventory/api/range_proposal_routes.py |
| POST | `/api/inventory/slotting/warehouses/{ware_id}/articles/{article}/scenario` | pick_topology_view | app/modules/inventory/api/slotting_routes.py |

## `/api/inventory/soft-pools`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/inventory/soft-pools/{warehouse}/{article}` | stock_reservation_view | app/modules/inventory/api/pool_routes.py |
| POST | `/api/inventory/soft-pools/{warehouse}/{article}/allocate` | stock_reservation_edit | app/modules/inventory/api/pool_routes.py |

## `/api/inventory/stock-posting`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/inventory/stock-posting/inventory/{revision_id}/lots` | stock_inventory_count | app/modules/inventory/api/inventory_count_routes.py |
| POST | `/api/inventory/stock-posting/inventory/counts` | stock_inventory_count | app/modules/inventory/api/inventory_count_routes.py |
| POST | `/api/inventory/stock-posting/inventory/revisions` | stock_inventory_count | app/modules/inventory/api/inventory_count_routes.py |
| POST | `/api/inventory/stock-posting/inventory/lots` | stock_inventory_count | app/modules/inventory/api/inventory_count_routes.py |
| GET | `/api/inventory/stock-posting/source-availability` | pick_wave_view | app/modules/inventory/api/source_routes.py |
| POST | `/api/inventory/stock-posting/manual-moves` | stock_posting_manual_move | app/modules/inventory/api/stock_command_routes.py |
| POST | `/api/inventory/stock-posting/compatibility-setting` | stock_compatibility_admin | app/modules/inventory/api/stock_command_routes.py |
| POST | `/api/inventory/stock-posting/compatibility/manual-moves` | stock_posting_manual_move | app/modules/inventory/api/stock_command_routes.py |
| POST | `/api/inventory/stock-posting/receipt-documents/{document_id}/reverse` | stock_receipt_reverse | app/modules/inventory/api/stock_command_routes.py |
| GET | `/api/inventory/stock-posting/status` | stock_reservation_view | app/modules/inventory/api/stock_routes.py |
| GET | `/api/inventory/stock-posting/operations/{operation_id}` | stock_reservation_view | app/modules/inventory/api/stock_routes.py |

## `/api/inventory/store-return-putaway`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| PUT | `/api/inventory/store-return-putaway/warehouses/{ware_id}/targets` | warehouse_settings_edit | app/modules/inventory/api/return_putaway_routes.py |
| GET | `/api/inventory/store-return-putaway/warehouses/{ware_id}/pending` | warehouse_return_place | app/modules/inventory/api/return_putaway_routes.py |
| POST | `/api/inventory/store-return-putaway/plan` | warehouse_return_place | app/modules/inventory/api/return_putaway_routes.py |

## `/api/inventory/store-returns`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| PUT | `/api/inventory/store-returns/warehouses/{ware_id}/policy` | warehouse_settings_edit | app/modules/inventory/api/store_return_receiving_routes.py |
| GET | `/api/inventory/store-returns/warehouses/{ware_id}/policy` | warehouse_settings_edit | app/modules/inventory/api/store_return_receiving_routes.py |
| GET | `/api/inventory/store-returns/warehouses/{ware_id}/pending` | warehouse_return_receive | app/modules/inventory/api/store_return_receiving_routes.py |
| POST | `/api/inventory/store-returns/receive` | warehouse_return_receive | app/modules/inventory/api/store_return_receiving_routes.py |
| PUT | `/api/inventory/store-returns/warehouses/{ware_id}/reuse-receiving` | warehouse_settings_edit | app/modules/inventory/api/store_return_receiving_routes.py |
| GET | `/api/inventory/store-returns/warehouses/{ware_id}/pending-page` | warehouse_return_receive | app/modules/inventory/api/store_return_receiving_routes.py |
| GET | `/api/inventory/store-returns/warehouses/{ware_id}/pickups/{pickup_id}/source` | warehouse_return_receive | app/modules/inventory/api/store_return_receiving_routes.py |

## `/api/inventory/supplier-handover`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/inventory/supplier-handover/record` | warehouse_return_dispatch | app/modules/inventory/api/supplier_handover_routes.py |
| POST | `/api/inventory/supplier-handover/confirm` | store_return_approve | app/modules/inventory/api/supplier_handover_routes.py |
| GET | `/api/inventory/supplier-handover/warehouses/{ware_id}` | warehouse_return_dispatch | app/modules/inventory/api/supplier_handover_routes.py |

## `/api/inventory/supplier-returns`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/inventory/supplier-returns/prepare` | store_return_approve | app/modules/inventory/api/supplier_return_routes.py |
| GET | `/api/inventory/supplier-returns/warehouses/{ware_id}` | warehouse_return_dispatch | app/modules/inventory/api/supplier_return_routes.py |
| GET | `/api/inventory/supplier-returns/suppliers` | store_return_approve | app/modules/inventory/api/supplier_return_routes.py |

## `/api/inventory/tare`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/inventory/tare/book` | tare_plan | app/modules/inventory/api/tare_assembly_routes.py |
| POST | `/api/inventory/tare/book-cancel` | tare_plan | app/modules/inventory/api/tare_assembly_routes.py |
| GET | `/api/inventory/tare/warehouses/{ware_id}/availability` | tare_view | app/modules/inventory/api/tare_assembly_routes.py |
| GET | `/api/inventory/tare/warehouses/{ware_id}/bookings` | tare_view | app/modules/inventory/api/tare_assembly_routes.py |
| GET | `/api/inventory/tare/assembly/catalog` | tare_view | app/modules/inventory/api/tare_assembly_routes.py |
| GET | `/api/inventory/tare/warehouses/{ware_id}/trips/{task_id}/loaded-bookings` | tare_view | app/modules/inventory/api/tare_assembly_routes.py |
| GET | `/api/inventory/tare/warehouses/{ware_id}/waves/{wave_id}/forecast` | tare_view | app/modules/inventory/api/tare_assembly_routes.py |
| GET | `/api/inventory/tare/load-recovery-candidates` | tare_view | app/modules/inventory/api/tare_assembly_routes.py |
| POST | `/api/inventory/tare/loss-report` | tare_loss_report | app/modules/inventory/api/tare_loss_routes.py |
| POST | `/api/inventory/tare/loss-decide` | tare_writeoff | app/modules/inventory/api/tare_loss_routes.py |
| GET | `/api/inventory/tare/warehouses/{ware_id}/loss-cases` | tare_view | app/modules/inventory/api/tare_loss_routes.py |
| GET | `/api/inventory/tare/return-policy` | warehouse_settings_edit | app/modules/inventory/api/tare_policy_routes.py |
| PUT | `/api/inventory/tare/return-policy` | warehouse_settings_edit | app/modules/inventory/api/tare_policy_routes.py |
| GET | `/api/inventory/tare/warehouses/{ware_id}/store-debt` | tare_view | app/modules/inventory/api/tare_policy_routes.py |
| POST | `/api/inventory/tare/damage` | tare_damage | app/modules/inventory/api/tare_resolution_routes.py |
| POST | `/api/inventory/tare/writeoff` | tare_writeoff | app/modules/inventory/api/tare_resolution_routes.py |
| GET | `/api/inventory/tare/warehouses/{ware_id}/damage-cases` | tare_view | app/modules/inventory/api/tare_resolution_routes.py |
| POST | `/api/inventory/tare/count` | tare_adjust | app/modules/inventory/api/tare_routes.py |
| POST | `/api/inventory/tare/offer` | tare_offer | app/modules/inventory/api/tare_routes.py |
| POST | `/api/inventory/tare/accept` | tare_accept | app/modules/inventory/api/tare_routes.py |
| POST | `/api/inventory/tare/offer-cancel` | tare_offer | app/modules/inventory/api/tare_routes.py |
| GET | `/api/inventory/tare/warehouses/{ware_id}/balances` | tare_view | app/modules/inventory/api/tare_routes.py |
| GET | `/api/inventory/tare/trips/{task_id}/offers` | tare_view | app/modules/inventory/api/tare_routes.py |
| GET | `/api/inventory/tare/trips/{task_id}/context` | tare_view | app/modules/inventory/api/tare_routes.py |
| GET | `/api/inventory/tare/warehouses/{ware_id}/damage-custody` | tare_view | app/modules/inventory/api/tare_routes.py |

## `/api/inventory/tasks`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/inventory/tasks` | inventory_task_view | app/modules/inventory/api/recovery_routes.py |
| POST | `/api/inventory/tasks/{task_id}/claim` | inventory_task_execute | app/modules/inventory/api/recovery_routes.py |

## `/api/inventory/trace-manifests`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/inventory/trace-manifests` | trace_manifest_import | app/modules/inventory/api/trace_manifest_routes.py |
| GET | `/api/inventory/trace-manifests/warehouses/{ware_id}` | trace_manifest_import | app/modules/inventory/api/trace_manifest_routes.py |
| POST | `/api/inventory/trace-manifests/inventory-context` | stock_inventory_count | app/modules/inventory/api/trace_manifest_routes.py |
| POST | `/api/inventory/trace-manifests/mes-context` | mes_wms_bridge_apply | app/modules/inventory/api/trace_manifest_routes.py |
| POST | `/api/inventory/trace-manifests/aggregations/invalidate` | trace_manifest_import | app/modules/inventory/api/trace_manifest_routes.py |
| GET | `/api/inventory/trace-manifests/warehouses/{ware_id}/pallets/{origin}/aggregations` | traceability_view | app/modules/inventory/api/trace_manifest_routes.py |

## `/api/inventory/warehouse-scales`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| PUT | `/api/inventory/warehouse-scales/devices/{device}` | warehouse_settings_edit | app/modules/inventory/api/warehouse_scale_routes.py |
| POST | `/api/inventory/warehouse-scales/captures` | warehouse_scale_ingest | app/modules/inventory/api/warehouse_scale_routes.py |
| GET | `/api/inventory/warehouse-scales/captures` | case_pick_execute | app/modules/inventory/api/warehouse_scale_routes.py |
| GET | `/api/inventory/warehouse-scales/captures/{key}` | case_pick_execute | app/modules/inventory/api/warehouse_scale_routes.py |
| POST | `/api/inventory/warehouse-scales/final-captures` | warehouse_scale_ingest | app/modules/inventory/api/warehouse_scale_routes.py |
| GET | `/api/inventory/warehouse-scales/final-captures` | case_pick_execute | app/modules/inventory/api/warehouse_scale_routes.py |

## `/api/legacy/tserver`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/legacy/tserver/execute` | — | app/routers/tserver.py |

## `/api/lots/{usscc}`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/lots/{usscc}/items` | — | app/routers/tserver.py |

## `/api/master-data/stores`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/master-data/stores` | dep: store_directory_service, store_reader | app/modules/master_data/api/store_directory_routes.py |
| GET | `/api/master-data/stores/card` | dep: store_directory_service, store_reader | app/modules/master_data/api/store_directory_routes.py |
| GET | `/api/master-data/stores/profile` | dep: store_profile_service, store_reader | app/modules/master_data/api/store_profile_routes.py |
| PUT | `/api/master-data/stores/profile` | warehouse_settings_edit | app/modules/master_data/api/store_profile_routes.py |

## `/api/master-data/warehouses`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/master-data/warehouses/options` | warehouse_settings_view | app/modules/master_data/api/warehouse_options_routes.py |

## `/api/mercury-operations`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/mercury-operations` | — | app/routers/production.py |

## `/api/mercury-operations/{operation_row_id}`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| PATCH | `/api/mercury-operations/{operation_row_id}` | — | app/routers/production.py |

## `/api/mes/movements`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/mes/movements` | mes_production_view | app/routers/mes.py |
| POST | `/api/mes/movements/{movement_id}/retry` | mes_wms_bridge_apply | app/routers/mes.py |

## `/api/mes/production-orders`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/mes/production-orders` | mes_production_view | app/routers/mes.py |
| POST | `/api/mes/production-orders` | mes_production_edit | app/routers/mes.py |
| GET | `/api/mes/production-orders/{production_order_id}` | mes_production_view | app/routers/mes.py |
| POST | `/api/mes/production-orders/{production_order_id}/issue-raw` | mes_production_edit | app/routers/mes.py |
| POST | `/api/mes/production-orders/{production_order_id}/complete` | mes_production_complete | app/routers/mes.py |
| POST | `/api/mes/production-orders/{production_order_id}/apply-wms` | mes_wms_bridge_apply | app/routers/mes.py |
| GET | `/api/mes/production-orders/{production_order_id}/genealogy` | mes_production_view | app/routers/mes.py |
| POST | `/api/mes/production-orders/{production_order_id}/raw-supply/calculate` | mes_raw_supply_calculate | app/routers/mes.py |
| GET | `/api/mes/production-orders/{production_order_id}/raw-supply` | mes_raw_supply_view | app/routers/mes.py |
| POST | `/api/mes/production-orders/{production_order_id}/release-to-production` | mes_raw_transfer_create | app/routers/mes.py |

## `/api/mes/raw-shortages`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/mes/raw-shortages` | mes_raw_supply_view | app/routers/mes.py |

## `/api/mes/raw-transfer-tasks`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/mes/raw-transfer-tasks` | mes_raw_supply_view | app/routers/mes.py |
| GET | `/api/mes/raw-transfer-tasks/{task_id}` | mes_raw_supply_view | app/routers/mes.py |
| POST | `/api/mes/raw-transfer-tasks/{task_id}/confirm` | mes_raw_transfer_confirm | app/routers/mes.py |
| POST | `/api/mes/raw-transfer-tasks/{task_id}/cancel` | mes_raw_transfer_cancel | app/routers/mes.py |

## `/api/outgoing-quality/{identifier}`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/outgoing-quality/{identifier}` | outgoing_pallet_check | app/modules/inventory/api/outgoing_quality_routes.py |
| GET | `/api/outgoing-quality/{identifier}/control-label` | outgoing_pallet_check | app/modules/inventory/api/outgoing_quality_routes.py |
| POST | `/api/outgoing-quality/{identifier}/scan` | outgoing_pallet_check | app/modules/inventory/api/outgoing_quality_routes.py |
| POST | `/api/outgoing-quality/{identifier}/weight` | outgoing_pallet_check | app/modules/inventory/api/outgoing_quality_routes.py |
| POST | `/api/outgoing-quality/{identifier}/plan` | outgoing_pallet_check | app/modules/inventory/api/outgoing_quality_routes.py |
| POST | `/api/outgoing-quality/{identifier}/final-weight` | outgoing_pallet_check | app/modules/inventory/api/outgoing_quality_routes.py |
| GET | `/api/outgoing-quality/{identifier}/final-captures` | outgoing_pallet_check | app/modules/inventory/api/outgoing_quality_routes.py |

## `/api/picking/articul-replenishment-rules`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/picking/articul-replenishment-rules` | pick_topology_view | app/routers/picking.py |
| POST | `/api/picking/articul-replenishment-rules` | pick_topology_edit | app/routers/picking.py |

## `/api/picking/order-rows`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/picking/order-rows/{row}/weighted-box-options` | pick_plan_create | app/modules/inventory/api/weighted_plan_routes.py |
| GET | `/api/picking/order-rows/{row}/weighted-box-approval-preview` | case_pick_short_approve | app/modules/inventory/api/weighted_plan_routes.py |

## `/api/picking/pick-faces`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/picking/pick-faces` | pick_topology_view | app/routers/picking.py |
| POST | `/api/picking/pick-faces` | pick_topology_edit | app/routers/picking.py |
| GET | `/api/picking/pick-faces/{pick_face_id}/articuls` | pick_topology_view | app/routers/picking.py |
| POST | `/api/picking/pick-faces/{pick_face_id}/articuls` | pick_topology_edit | app/routers/picking.py |

## `/api/picking/plans`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/picking/plans` | pick_plan_create | app/routers/picking.py |
| GET | `/api/picking/plans` | pick_plan_view | app/routers/picking.py |
| GET | `/api/picking/plans/{pick_plan_id}` | pick_plan_view | app/routers/picking.py |
| POST | `/api/picking/plans/{pick_plan_id}/cancel` | pick_plan_cancel | app/routers/picking.py |
| GET | `/api/picking/plans/{pick_plan_id}/shortages` | pick_shortage_view | app/routers/picking.py |

## `/api/picking/reservations`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/picking/reservations` | pick_reservation_view | app/routers/picking.py |

## `/api/picking/route-cells`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/picking/route-cells` | pick_topology_view | app/routers/picking.py |
| POST | `/api/picking/route-cells` | pick_topology_edit | app/routers/picking.py |

## `/api/picking/routes`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/picking/routes` | pick_topology_view | app/routers/picking.py |
| POST | `/api/picking/routes` | pick_topology_edit | app/routers/picking.py |

## `/api/picking/shortages`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/picking/shortages` | pick_shortage_view | app/routers/picking.py |

## `/api/picking/waves`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/picking/waves/{wave_id}/execution` | pick_wave_view | app/modules/inventory/api/wave_execution_routes.py |
| POST | `/api/picking/waves/{wave_id}/finish-execution` | pick_wave_launch | app/modules/inventory/api/wave_execution_routes.py |
| GET | `/api/picking/waves/{wave_id}/pick-readiness` | pick_wave_view | app/modules/inventory/api/wave_pick_routes.py |
| POST | `/api/picking/waves/{wave_id}/release-picking` | pick_wave_launch | app/modules/inventory/api/wave_pick_routes.py |
| GET | `/api/picking/waves` | pick_wave_view | app/routers/picking.py |
| POST | `/api/picking/waves` | pick_wave_create | app/routers/picking.py |
| GET | `/api/picking/waves/candidates` | pick_wave_view | app/routers/picking.py |
| GET | `/api/picking/waves/{pick_wave_id}/header` | pick_wave_view | app/routers/picking.py |
| GET | `/api/picking/waves/{pick_wave_id}` | pick_wave_view | app/routers/picking.py |
| GET | `/api/picking/waves/{pick_wave_id}/readiness` | pick_wave_view | app/routers/picking.py |
| POST | `/api/picking/waves/{pick_wave_id}/plans` | pick_wave_create | app/routers/picking.py |
| POST | `/api/picking/waves/{pick_wave_id}/calculate` | pick_wave_calculate | app/routers/picking.py |
| POST | `/api/picking/waves/{pick_wave_id}/launch` | pick_wave_launch | app/routers/picking.py |
| POST | `/api/picking/waves/{pick_wave_id}/cancel` | pick_wave_cancel | app/routers/picking.py |
| POST | `/api/picking/waves/{pick_wave_id}/release-reservations` | pick_wave_release_reserves | app/routers/picking.py |
| POST | `/api/picking/waves/{pick_wave_id}/replenishment/minimax-check` | pick_wave_launch | app/routers/picking.py |
| POST | `/api/picking/waves/{pick_wave_id}/staging/release` | pick_wave_launch | app/routers/picking.py |
| GET | `/api/picking/waves/{pick_wave_id}/reservations` | pick_wave_view | app/routers/picking.py |
| GET | `/api/picking/waves/{pick_wave_id}/replenishment-tasks` | pick_wave_view | app/routers/picking.py |
| GET | `/api/picking/waves/{pick_wave_id}/tasks` | pick_wave_view | app/routers/picking.py |
| POST | `/api/picking/waves/{pick_wave_id}/tasks/{pick_task_id}/complete` | pick_wave_launch | app/routers/picking.py |
| GET | `/api/picking/waves/{pick_wave_id}/audit` | pick_wave_audit_view | app/routers/picking.py |

## `/api/picking/weighted-box-choices`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/picking/weighted-box-choices` | case_pick_short_approve | app/modules/inventory/api/weighted_plan_routes.py |
| POST | `/api/picking/weighted-box-choices/{choice}/cancel` | case_pick_short_approve | app/modules/inventory/api/weighted_plan_routes.py |

## `/api/places/{place_id}`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/places/{place_id}/items` | — | app/routers/tserver.py |

## `/api/production-batches`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/production-batches` | — | app/routers/production.py |

## `/api/production-batches/{prod_batch_id}`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/production-batches/{prod_batch_id}/status` | — | app/routers/production.py |
| POST | `/api/production-batches/{prod_batch_id}/pallets` | — | app/routers/production.py |
| POST | `/api/production-batches/{prod_batch_id}/raw-usage` | — | app/routers/production.py |
| POST | `/api/production-batches/{prod_batch_id}/crpt-codes` | — | app/routers/production.py |
| POST | `/api/production-batches/{prod_batch_id}/aggregations` | — | app/routers/production.py |
| POST | `/api/production-batches/{prod_batch_id}/mercury` | — | app/routers/production.py |
| GET | `/api/production-batches/{prod_batch_id}/regulatory-status` | — | app/routers/production.py |
| POST | `/api/production-batches/{prod_batch_id}/mercury-operations` | — | app/routers/production.py |

## `/api/products/by-barcode`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/products/by-barcode/{barcode}` | — | app/routers/tserver.py |

## `/api/raw-batches`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/raw-batches` | — | app/routers/production.py |

## `/api/raw-batches/{raw_batch_id}`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/raw-batches/{raw_batch_id}` | — | app/routers/production.py |

## `/api/raw-material/remains`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/raw-material/remains` | raw_material_stock_view | app/routers/raw_material.py |

## `/api/raw-material/skus`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/raw-material/skus` | raw_material_view | app/routers/raw_material.py |
| PATCH | `/api/raw-material/skus/{articul}` | raw_material_edit | app/routers/raw_material.py |

## `/api/raw-material/warehouses`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/raw-material/warehouses` | raw_material_view | app/routers/raw_material.py |

## `/api/receiving/labels`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/receiving/labels/{label_id}` | warehouse_receipt_confirm | app/modules/inventory/api/receiving_routes.py |
| POST | `/api/receiving/labels/{label_id}/confirm` | warehouse_receipt_confirm | app/modules/inventory/api/receiving_routes.py |

## `/api/receiving/pallets`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/receiving/pallets/{pallet}/composition` | traceability_view | app/modules/inventory/api/receiving_routes.py |

## `/api/receiving/putaway`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/receiving/putaway/{task_id}/replan` | warehouse_task_assign | app/modules/inventory/api/receiving_routes.py |
| POST | `/api/receiving/putaway/{task_id}/complete` | warehouse_task_execute | app/modules/inventory/api/receiving_routes.py |

## `/api/receiving/st-deferrals`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/receiving/st-deferrals/waiting-tasks` | warehouse_task_edit | app/modules/inventory/api/waiting_task_routes.py |
| GET | `/api/receiving/st-deferrals/waiting-tasks` | warehouse_task_view | app/modules/inventory/api/waiting_task_routes.py |

## `/api/receiving/supply-orders`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/receiving/supply-orders/{order_id}/labels` | warehouse_receipt_confirm | app/modules/inventory/api/receiving_routes.py |
| POST | `/api/receiving/supply-orders/{order_id}/close` | warehouse_receipt_reconcile | app/modules/inventory/api/receiving_routes.py |
| POST | `/api/receiving/supply-orders/{order_id}/reopen` | warehouse_receipt_reconcile | app/modules/inventory/api/receiving_routes.py |
| POST | `/api/receiving/supply-orders/{order_id}/pallets` | warehouse_receipt_confirm | app/modules/inventory/api/receiving_routes.py |

## `/api/receiving/warehouses`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/receiving/warehouses/{warehouse}/settings` | warehouse_settings_view | app/modules/inventory/api/receiving_routes.py |
| PUT | `/api/receiving/warehouses/{warehouse}/settings` | warehouse_settings_edit | app/modules/inventory/api/receiving_routes.py |
| PUT | `/api/receiving/warehouses/{warehouse}/skus/{articul}/placement-rule` | warehouse_settings_edit | app/modules/inventory/api/receiving_routes.py |
| GET | `/api/receiving/warehouses/{warehouse}/skus/{articul}/placement-rule` | warehouse_settings_view | app/modules/inventory/api/receiving_routes.py |
| GET | `/api/receiving/warehouses/{warehouse}/cells/{cell}/placement-rule` | warehouse_settings_view | app/modules/inventory/api/receiving_routes.py |
| PUT | `/api/receiving/warehouses/{warehouse}/cells/{cell}/placement-rule` | warehouse_settings_edit | app/modules/inventory/api/receiving_routes.py |

## `/api/regulatory/journal`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/regulatory/journal` | — | app/routers/production.py |

## `/api/regulatory/mercury-sites`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/regulatory/mercury-sites` | — | app/routers/production.py |
| GET | `/api/regulatory/mercury-sites` | — | app/routers/production.py |

## `/api/regulatory/outbox`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/regulatory/outbox` | — | app/routers/production.py |

## `/api/resources`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/resources` | resource_management_view | app/routers/resource_management.py |
| POST | `/api/resources` | resource_management_edit | app/routers/resource_management.py |

## `/api/resources/equipment`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/resources/equipment` | resource_management_view | app/routers/resource_management.py |
| POST | `/api/resources/equipment` | resource_management_edit | app/routers/resource_management.py |

## `/api/resources/reach-shifts`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/resources/reach-shifts/{base_shift_id}` | resource_shift_view | app/modules/resources/api/reach_shift_routes.py |
| POST | `/api/resources/reach-shifts/{base_shift_id}` | resource_shift_edit | app/modules/resources/api/reach_shift_routes.py |

## `/api/resources/sessions`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/resources/sessions/{session_id}/position` | dep: qualification_service, resource_position_user | app/modules/resources/api/qualification_routes.py |
| GET | `/api/resources/sessions` | resource_session_view | app/routers/resource_management.py |
| POST | `/api/resources/sessions/login` | resource_session_manage | app/routers/resource_management.py |
| POST | `/api/resources/sessions/tsd-login` | resource_session_manage | app/routers/resource_management.py |
| POST | `/api/resources/sessions/{session_id}/heartbeat` | resource_session_manage | app/routers/resource_management.py |
| POST | `/api/resources/sessions/{session_id}/pause` | resource_session_manage | app/routers/resource_management.py |
| POST | `/api/resources/sessions/{session_id}/resume` | resource_session_manage | app/routers/resource_management.py |
| POST | `/api/resources/sessions/{session_id}/logout` | resource_session_manage | app/routers/resource_management.py |

## `/api/resources/shifts`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/resources/shifts` | resource_shift_view | app/routers/resource_management.py |
| POST | `/api/resources/shifts` | resource_shift_edit | app/routers/resource_management.py |

## `/api/resources/types`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/resources/types` | resource_management_view | app/routers/resource_management.py |

## `/api/resources/warehouse-tasks`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/resources/warehouse-tasks/{task_id}/candidates` | resource_management_view | app/modules/resources/api/qualification_routes.py |
| POST | `/api/resources/warehouse-tasks/{task_id}/dispatch-nearest` | resource_dispatch_manage | app/modules/resources/api/qualification_routes.py |

## `/api/resources/workload`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/resources/workload/waves/{wave_id}/time-context` | pick_wave_view | app/modules/resources/api/wave_time_routes.py |
| POST | `/api/resources/workload/waves/approve-time` | pick_wave_launch | app/modules/resources/api/wave_time_routes.py |
| POST | `/api/resources/workload/norms` | resource_shift_edit | app/modules/resources/api/workload_config_routes.py |
| POST | `/api/resources/workload/attendance` | resource_shift_edit | app/modules/resources/api/workload_config_routes.py |
| POST | `/api/resources/workload/attendance/replace` | resource_shift_edit | app/modules/resources/api/workload_config_routes.py |
| POST | `/api/resources/workload/attendance/cancel` | resource_shift_edit | app/modules/resources/api/workload_config_routes.py |
| GET | `/api/resources/workload/warehouses/{ware_id}` | resource_shift_view | app/modules/resources/api/workload_config_routes.py |
| POST | `/api/resources/workload/forecast-scopes` | resource_shift_edit | app/modules/resources/api/workload_config_routes.py |
| GET | `/api/resources/workload/warehouses/{ware_id}/attendance/{plan_id}/history` | resource_shift_view | app/modules/resources/api/workload_history_routes.py |
| POST | `/api/resources/workload/warehouses/{ware_id}/preview` | resource_shift_view | app/modules/resources/api/workload_monitor_routes.py |

## `/api/resources/{resource_id}`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/resources/{resource_id}/qualifications` | resource_management_view | app/modules/resources/api/qualification_routes.py |
| PUT | `/api/resources/{resource_id}/qualifications` | warehouse_settings_edit | app/modules/resources/api/qualification_routes.py |

## `/api/sku-allocation/{warehouse}`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/sku-allocation/{warehouse}/{article}` | stock_reservation_view | app/modules/master_data/api/allocation_routes.py |
| PUT | `/api/sku-allocation/{warehouse}/{article}` | warehouse_settings_edit | app/modules/master_data/api/allocation_routes.py |

## `/api/sku-quality-weight/{warehouse}`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/sku-quality-weight/{warehouse}/{article}` | finished_goods_view | app/modules/master_data/api/quality_weight_routes.py |
| PUT | `/api/sku-quality-weight/{warehouse}/{article}` | warehouse_settings_edit | app/modules/master_data/api/quality_weight_routes.py |

## `/api/stock-reservations`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/stock-reservations` | stock_reservation_view | app/routers/stock_reservations.py |
| POST | `/api/stock-reservations` | stock_reservation_edit | app/routers/stock_reservations.py |

## `/api/stock-reservations/{reservation_id}`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/stock-reservations/{reservation_id}` | stock_reservation_view | app/routers/stock_reservations.py |
| POST | `/api/stock-reservations/{reservation_id}/promote-to-hard` | stock_reservation_edit | app/routers/stock_reservations.py |
| POST | `/api/stock-reservations/{reservation_id}/release` | stock_reservation_edit | app/routers/stock_reservations.py |
| POST | `/api/stock-reservations/{reservation_id}/consume` | stock_reservation_edit | app/routers/stock_reservations.py |
| POST | `/api/stock-reservations/{reservation_id}/cancel` | stock_reservation_edit | app/routers/stock_reservations.py |

## `/api/terminal/auth`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/terminal/auth/me` | — | app/routers/tserver.py |

## `/api/terminal/call-spf`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/terminal/call-spf` | — | app/routers/tserver.py |

## `/api/terminal/lots`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/terminal/lots/{usscc}/check` | — | app/routers/tserver.py |

## `/api/terminal/order-checks`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/terminal/order-checks` | — | app/routers/tserver.py |

## `/api/terminal/place-checks`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/terminal/place-checks` | — | app/routers/tserver.py |

## `/api/terminal/users`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/terminal/users/{user_id}` | — | app/routers/tserver.py |

## `/api/trace/entities`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/trace/entities/{entity_type}/{entity_id}/forward` | traceability_view | app/routers/traceability.py |
| GET | `/api/trace/entities/{entity_type}/{entity_id}/backward` | traceability_view | app/routers/traceability.py |

## `/api/transport/driver-bindings`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| PUT | `/api/transport/driver-bindings/{driver_id}` | warehouse_settings_edit | app/modules/transport/api/driver_binding_routes.py |
| GET | `/api/transport/driver-bindings/{driver_id}` | warehouse_settings_edit | app/modules/transport/api/driver_binding_routes.py |

## `/api/transport/loading`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/transport/loading/{task_id}/status` | transport_dispatch_view | app/modules/transport/api/loading_routes.py |
| POST | `/api/transport/loading/confirm` | stock_posting_shipping | app/modules/transport/api/loading_routes.py |
| POST | `/api/transport/loading/{task_id}/depart` | transport_dispatch_close | app/modules/transport/api/loading_routes.py |
| GET | `/api/transport/loading/single-preview` | stock_posting_shipping | app/modules/transport/api/loading_routes.py |
| POST | `/api/transport/loading/confirm-single` | stock_posting_shipping | app/modules/transport/api/loading_routes.py |
| GET | `/api/transport/loading/reconciliation-preview` | stock_posting_shipping | app/modules/transport/api/loading_routes.py |
| POST | `/api/transport/loading/confirm-reconciliation` | stock_posting_shipping | app/modules/transport/api/loading_routes.py |
| POST | `/api/transport/loading/unload` | stock_posting_shipping | app/modules/transport/api/unloading_routes.py |

## `/api/transport/preflight`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/transport/preflight/trips/{trip_id}/time-context` | transport_dispatch_edit | app/modules/transport/api/preflight_routes.py |
| GET | `/api/transport/preflight/trips/{trip_id}/coordination` | transport_dispatch_edit | app/modules/transport/api/preflight_routes.py |
| POST | `/api/transport/preflight/time-approvals` | transport_dispatch_edit | app/modules/transport/api/preflight_routes.py |
| POST | `/api/transport/preflight/trips/{trip_id}/time` | transport_dispatch_edit | app/modules/transport/api/preflight_routes.py |
| GET | `/api/transport/preflight/plans/{plan_id}` | transport_dispatch_edit | app/modules/transport/api/preflight_routes.py |
| POST | `/api/transport/preflight/trips/{trip_id}` | transport_dispatch_edit | app/modules/transport/api/preflight_routes.py |
| GET | `/api/transport/preflight/trips/{trip_id}/route-context` | transport_dispatch_edit | app/modules/transport/api/preflight_routes.py |
| POST | `/api/transport/preflight/route-inputs` | transport_dispatch_edit | app/modules/transport/api/preflight_routes.py |
| GET | `/api/transport/preflight/trips/{trip_id}/road-legs` | transport_dispatch_edit | app/modules/transport/api/preflight_routes.py |
| GET | `/api/transport/preflight/trips/{trip_id}/delivery-windows` | transport_dispatch_edit | app/modules/transport/api/preflight_routes.py |

## `/api/transport/st-deferrals`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/transport/st-deferrals/context` | transport_dispatch_view | app/modules/transport/api/st_deferral_routes.py |
| POST | `/api/transport/st-deferrals` | transport_dispatch_edit | app/modules/transport/api/st_deferral_routes.py |
| GET | `/api/transport/st-deferrals/history` | transport_dispatch_view | app/modules/transport/api/st_deferral_routes.py |
| GET | `/api/transport/st-deferrals/trip-candidates` | transport_dispatch_view | app/modules/transport/api/st_deferral_routes.py |

## `/api/transport/warehouse-depots`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/transport/warehouse-depots/{warehouse_id}` | warehouse_settings_edit | app/modules/transport/api/warehouse_depot_routes.py |
| POST | `/api/transport/warehouse-depots` | warehouse_settings_edit | app/modules/transport/api/warehouse_depot_routes.py |
| POST | `/api/transport/warehouse-depots/resolve` | warehouse_settings_edit | app/modules/transport/api/warehouse_depot_routes.py |

## `/api/transport/warehouse-forecast`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/transport/warehouse-forecast/warehouses/{ware_id}/view` | transport_dispatch_view | app/modules/transport/api/forecast_routes.py |
| POST | `/api/transport/warehouse-forecast/warehouses/{ware_id}/project` | transport_dispatch_edit | app/modules/transport/api/forecast_routes.py |
| POST | `/api/transport/warehouse-forecast/source` | transport_dispatch_edit | app/modules/transport/api/forecast_routes.py |

## `/api/vehicle-types`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/vehicle-types` | vehicle_type_view | app/routers/customer_rules.py |
| POST | `/api/vehicle-types` | vehicle_type_edit | app/routers/customer_rules.py |

## `/api/warehouse-hus/attach`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/warehouse-hus/attach` | warehouse_task_execute | app/modules/inventory/api/warehouse_hu_routes.py |

## `/api/warehouse-hus/attach-case`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/warehouse-hus/attach-case` | warehouse_task_execute | app/modules/inventory/api/warehouse_hu_routes.py |

## `/api/warehouse-hus/composition`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/warehouse-hus/composition` | warehouse_task_view | app/modules/inventory/api/warehouse_hu_routes.py |

## `/api/warehouse-hus/create`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/warehouse-hus/create` | warehouse_task_execute | app/modules/inventory/api/warehouse_hu_routes.py |

## `/api/warehouse-hus/detach`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/warehouse-hus/detach` | warehouse_task_execute | app/modules/inventory/api/warehouse_hu_routes.py |

## `/api/warehouse-hus/detach-case`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/warehouse-hus/detach-case` | warehouse_task_execute | app/modules/inventory/api/warehouse_hu_routes.py |

## `/api/warehouse-hus/move`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/warehouse-hus/move` | warehouse_task_execute | app/modules/inventory/api/warehouse_hu_routes.py |

## `/api/warehouse-hus/plan-move`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/warehouse-hus/plan-move` | warehouse_task_execute | app/modules/inventory/api/warehouse_hu_routes.py |

## `/api/warehouse-hus/relocate-slot`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/warehouse-hus/relocate-slot` | warehouse_task_execute | app/modules/inventory/api/warehouse_hu_routes.py |

## `/api/warehouse-hus/repack-case-slot`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/warehouse-hus/repack-case-slot` | warehouse_task_execute | app/modules/inventory/api/warehouse_hu_repack_routes.py |

## `/api/warehouse-hus/repack-slot`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/warehouse-hus/repack-slot` | warehouse_task_execute | app/modules/inventory/api/warehouse_hu_repack_routes.py |

## `/api/warehouse-hus/ship`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/warehouse-hus/ship` | stock_posting_shipping | app/modules/inventory/api/warehouse_hu_routes.py |

## `/api/warehouse-hus/target-slots`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/warehouse-hus/target-slots` | warehouse_task_view | app/modules/inventory/api/warehouse_hu_routes.py |

## `/api/warehouse-hus/unpack`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/warehouse-hus/unpack` | warehouse_task_execute | app/modules/inventory/api/warehouse_hu_routes.py |

## `/api/warehouse-hus/unpack-case`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| POST | `/api/warehouse-hus/unpack-case` | warehouse_task_execute | app/modules/inventory/api/warehouse_hu_routes.py |

## `/api/warehouse-tasks`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/warehouse-tasks` | warehouse_task_view | app/routers/warehouse_tasks.py |

## `/api/warehouse-tasks/domain-sync`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/warehouse-tasks/domain-sync` | warehouse_task_view | app/routers/warehouse_tasks.py |

## `/api/warehouse-tasks/{task_id}`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/api/warehouse-tasks/{task_id}/full-pallet-shipment` | warehouse_task_view | app/modules/inventory/api/fullpal_shipment_routes.py |
| POST | `/api/warehouse-tasks/{task_id}/full-pallet-shipment` | warehouse_task_execute | app/modules/inventory/api/fullpal_shipment_routes.py |
| GET | `/api/warehouse-tasks/{task_id}/scan-context` | warehouse_task_view | app/modules/inventory/api/task_scan_routes.py |
| GET | `/api/warehouse-tasks/{task_id}/scan-draft` | warehouse_task_execute | app/modules/inventory/api/task_scan_routes.py |
| POST | `/api/warehouse-tasks/{task_id}/scan-draft` | warehouse_task_execute | app/modules/inventory/api/task_scan_routes.py |
| GET | `/api/warehouse-tasks/{task_id}` | warehouse_task_view | app/routers/warehouse_tasks.py |
| GET | `/api/warehouse-tasks/{task_id}/progress` | warehouse_task_view | app/routers/warehouse_tasks.py |
| GET | `/api/warehouse-tasks/{task_id}/sync` | warehouse_task_view | app/routers/warehouse_tasks.py |
| POST | `/api/warehouse-tasks/{task_id}/assign` | warehouse_task_execute | app/routers/warehouse_tasks.py |
| POST | `/api/warehouse-tasks/{task_id}/start` | warehouse_task_execute | app/routers/warehouse_tasks.py |
| POST | `/api/warehouse-tasks/{task_id}/complete` | warehouse_task_execute | app/routers/warehouse_tasks.py |
| POST | `/api/warehouse-tasks/{task_id}/sync/retry` | warehouse_task_execute | app/routers/warehouse_tasks.py |
| POST | `/api/warehouse-tasks/{task_id}/cancel` | warehouse_task_edit | app/routers/warehouse_tasks.py |

## `/db/ping`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/db/ping` | — | app/routers/health.py |

## `/health`
| Метод | Путь | Право | Файл |
|---|---|---|---|
| GET | `/health` | — | app/routers/health.py |
