# Маппинг ролей на права и области (сгенерировано)

R — чтение, X — исполнение, A — подтверждение, M — администрирование. Статус права: API / API без групп / legacy / новое.

| Роль | Группа | Область | Рабочее место | R | X | A | M |
|---|---|---|---|---|---|---|---|
| Директор логистики сети | `RL_LOG_DIR` | NETWORK | gap | `transport_dispatch_view`, `pick_wave_view`, `store_case_investigate`, `network_kpi_view`* | — | — | — |
| Директор распределительного центра | `RL_DC_DIR` | WAREHOUSE | in_c0056 | `transport_dispatch_view`, `pick_wave_view`, `warehouse_task_view`, `resource_shift_view`, `resource_management_view`, `inventory_task_view`, `traceability_view` | `pick_wave_launch` | `resource_shift_edit` | — |
| Директор транспорта | `RL_TR_DIR` | NETWORK | existing_screens | `transport_dispatch_view`, `vehicle_type_view`, `tare_view` | — | — | — |
| Руководитель складских операций | `RL_WH_OPS` | WAREHOUSE | existing_screens | `pick_wave_view`, `warehouse_task_view`, `resource_session_view`, `resource_management_view`, `resource_shift_view`, `warehouse_settings_view`, `pick_topology_view` | — | `resource_shift_edit`, `resource_management_edit` | `warehouse_settings_edit` |
| Начальник смены | `RL_SHIFT` | WAREHOUSE | existing_screens | `pick_wave_view`, `warehouse_task_view`, `resource_session_view`, `resource_management_view`, `resource_shift_view`, `pick_shortage_view`, `pick_reservation_view`, `inventory_task_view`, `case_pick_view`, `pick_wave_audit_view`, `view_route` | `pick_wave_launch`, `pick_wave_cancel`, `pick_wave_release_reserves`, `warehouse_task_edit`, `warehouse_task_assign`, `case_pick_manage`, `resource_dispatch_manage`, `internal_move`, `komplect` | `case_pick_short_approve`, `warehouse_task_force_assign`, `resource_shift_edit` | — |
| Старший участка приёмки | `RL_ST_RECV` | ZONE | existing_screens | `sap_supply_view`, `warehouse_task_view`, `traceability_view`, `view_route` | `warehouse_task_assign` | `warehouse_receipt_reconcile`, `stock_receipt_reverse` | — |
| Старший участка хранения и пополнения (диспетчер ричтраков) | `RL_ST_STOR` | ZONE | existing_screens | `warehouse_task_view`, `pick_wave_view`, `resource_session_view`, `resource_management_view`, `pick_topology_view` | `warehouse_task_assign`, `resource_dispatch_manage` | `resource_shift_edit` | — |
| Старший участка отбора | `RL_ST_PICK` | ZONE | existing_screens | `case_pick_view`, `pick_shortage_view`, `warehouse_task_view`, `inventory_task_view` | `case_pick_manage` | — | — |
| Старший участка контроля (руководитель качества) | `RL_ST_QC` | ZONE | existing_screens | `warehouse_task_view`, `case_pick_view`, `traceability_view`, `warehouse_settings_view`, `quality_batch_view`, `check_weight`, `view_vesov` | — | `quality_batch_edit` | — |
| Старший участка экспедиции | `RL_ST_EXP` | ZONE | existing_screens | `transport_dispatch_view`, `warehouse_task_view`, `tare_view`, `view_route` | `stock_posting_shipping`, `interwarehouse_receive`, `load_st`, `divide_st` | — | — |
| Оператор SAP и документов | `RL_SAP_DOC` | WAREHOUSE | existing_screens | `sap_supply_view`, `customer_order_view`, `external_outbox_view` | `sap_article_import`, `sap_supply_import`, `sap_store_order_import`, `sap_store_decision_import`, `sap_return_import`, `customer_order_import` | — | — |
| Специалист справочников | `RL_MDM` | WAREHOUSE | existing_screens | `warehouse_settings_view`, `customer_view`, `customer_rule_view`, `pick_topology_view`, `vehicle_type_view` | `warehouse_settings_edit`, `customer_edit`, `customer_rule_edit`, `pick_topology_edit` | — | — |
| Планировщик волн и обеспечения | `RL_WAVE_PLAN` | WAREHOUSE | existing_screens | `pick_wave_view`, `pick_plan_view`, `pick_reservation_view`, `pick_shortage_view`, `stock_reservation_view`, `customer_order_view` | `pick_wave_create`, `pick_wave_calculate`, `pick_wave_cancel`, `pick_plan_create`, `pick_plan_cancel` | — | — |
| Оператор приёмки | `RL_RECV` | ZONE | existing_screens | `sap_supply_view`, `traceability_view` | `warehouse_receipt_confirm`, `warehouse_task_execute` | — | — |
| Водитель ричтрака | `RL_REACH` | ZONE | existing_screens | `warehouse_task_view` | `warehouse_task_execute` | — | — |
| Водитель погрузчика | `RL_FORK` | ZONE | existing_screens | `warehouse_task_view` | `warehouse_task_execute`, `interwarehouse_receive` | — | — |
| Комплектовщик | `RL_PICKER` | SELF | in_c0056 | `case_pick_view` | `case_pick_execute`, `inventory_task_execute` | — | — |
| Контролёр качества, веса и маркировки | `RL_QC` | ZONE | existing_screens | `case_pick_view`, `traceability_view`, `view_vesov` | `outgoing_pallet_check`, `outgoing_pallet_edit`, `warehouse_scale_ingest`, `check_weight` | — | — |
| Грузчик / оператор погрузки | `RL_LOADER` | ZONE | existing_screens | `transport_dispatch_view` | `stock_posting_shipping`, `load_st` | — | — |
| Контролёр остатков (КРО) | `RL_STOCK_CTL` | WAREHOUSE | gap | `inventory_task_view`, `traceability_view`, `stock_reservation_view`, `view_pall_hist`, `stock_manager` | — | `stock_adjust_approve`* | — |
| Инвентаризатор | `RL_INV_AUD` | ZONE | existing_screens | `inventory_task_view` | `inventory_task_execute`, `stock_inventory_count` | — | — |
| Специалист брака, карантина и возвратов | `RL_RETURNS` | WAREHOUSE | existing_screens | `warehouse_task_view`, `traceability_view` | `warehouse_return_receive`, `warehouse_return_place`, `warehouse_return_dispatch` | `cell_availability_edit`* | — |
| Ответственный за оборотную тару | `RL_TARE` | WAREHOUSE | existing_screens | `tare_view` | `tare_loss_report`, `tare_plan`, `tare_damage` | — | — |
| Начальник кросс-дока | `RL_XDOCK` | WAREHOUSE | existing_screens | `transport_dispatch_view`, `warehouse_task_view` | `interwarehouse_receive` | — | — |
| Руководитель транспортного планирования | `RL_TR_PLAN_HD` | WAREHOUSE | existing_screens | `transport_dispatch_view`, `view_route`, `view_adress` | `transport_dispatch_edit`, `plan_tt_time`, `create_route`, `change_route` | — | — |
| Маршрутный планировщик | `RL_ROUTE_PLAN` | WAREHOUSE | existing_screens | `transport_dispatch_view`, `view_route` | `transport_dispatch_edit`, `change_route` | — | — |
| Транспортный диспетчер | `RL_DISPATCH` | GROUP | in_c0056 | `transport_dispatch_view`, `tare_view`, `view_route` | `transport_dispatch_edit`, `change_voditel`, `change_tt_dock` | `transport_dispatch_close` | — |
| Координатор двора и ворот | `RL_YARD` | WAREHOUSE | gap | `transport_dispatch_view` | `yard_gate_manage`* | — | — |
| Водитель автомобиля | `RL_DRIVER` | SELF | in_c0056 | — | `driver_return_accept`, `tare_offer`, `tare_accept` | — | — |
| Ответственный за автопарк и ремонт | `RL_FLEET` | WAREHOUSE | existing_screens | `transport_dispatch_view`, `vehicle_type_view` | `transport_fleet_edit` | — | — |
| Менеджер перевозчиков | `RL_CARRIER` | CARRIER | gap | `transport_dispatch_view` | `carrier_manage`* | — | — |
| Региональный руководитель магазинов | `RL_REGION` | REGION | gap | `store_region_view`* | — | — | — |
| Управляющий магазином | `RL_STORE_DIR` | STORE | gap | `store_case_investigate` | — | `store_loss_confirm`, `store_return_approve` | — |
| Приёмщик магазина | `RL_STORE_RECV` | STORE | existing_screens | — | `store_receipt_confirm` | — | — |
| Экономист / транспортный биллинг | `RL_BILLING` | WAREHOUSE | existing_screens | `transport_dispatch_view`, `view_billing`, `view_tt_billing` | `edit_bill_tt` | `expense_logist_approve` | — |
| Согласующий затрат | `RL_COST_APPR` | WAREHOUSE | existing_screens | `transport_dispatch_view` | — | `expense_finance_approve` | — |
| Аналитик | `RL_ANALYST` | GROUP | existing_screens | `transport_dispatch_view`, `pick_wave_view`, `warehouse_task_view` | — | — | — |
| Администратор доступа | `RL_ACCESS_ADM` | NETWORK | in_c0056 | `access_admin_view`, `rights_admin_view` | `access_assign_manage`, `access_group_manage` | — | `rights_admin_edit` |
| Специалист интеграций | `RL_INTEGR` | NETWORK | existing_screens | `external_outbox_view`, `api_audit_view`, `slow_sql_view` | `external_outbox_retry` | — | — |
| Аудитор (только чтение) | `RL_AUDITOR` | GROUP | gap | `traceability_view`, `transport_dispatch_view`, `warehouse_task_view`, `inventory_task_view` | — | — | — |
| Редактор базы знаний | `RL_KNOWLEDGE` | NETWORK | in_c0056 | — | `knowledge_edit` | — | — |

\* — новое право (NEW_RIGHTS).

## Конфликты при совмещении ролей

- Контролёр остатков (КРО) + Инвентаризатор: `stock_inventory_count+stock_adjust_approve` — пересчитавший не утверждает расхождения склада, где сам считает
