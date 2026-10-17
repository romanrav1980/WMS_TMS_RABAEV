# Рабочие места retailcase — матрица (C0074, 15.10.2026)

Все места живут в `features/platform/workspaces/`, вход — `/?page=workspace&workspace=<id>`. Выбор места не выдаёт прав: каждое чтение проверяет сервер. **Ни одно место не отправляет бизнес-команд**: действия выполняются переходом в экран-владелец. Единственный POST — `shift-overview`, он только читает.

| Место (`workspace`) | Роль C0049 | Реальные источники (GET, если не указано) | Права источников | Действия → экран-владелец | Справка | Остаётся от API |
|---|---|---|---|---|---|---|
| Директор РЦ (`director`) | dc_director | transport/tasks, vehicles/gantt, picking/waves, case-pick/tasks?scope=all, resources/sessions, sap/supply-orders, recovery-shorts, resources/timeline | transport_dispatch_view, pick_wave_view, case_pick_view, resource_session_view, sap_supply_view, resource_gantt_view (+ источники Ганта) | рейс → `?page=transport&task_id`; панель смены, задания, приёмка (raw) | workspaces, resource-gantt | пояс РЦ; фильтр сборки по складу на сервере |
| Старший смены (`shift`) | shift_supervisor | picking/waves?status&ware_id, POST picking/shift-overview, case-pick/tasks?scope=all&ware_id, case-pick/shorts?ware_id, resources/sessions?ware_id, recovery-shorts, access/workspaces, resources/timeline | pick_wave_view (native), case_pick_view, resource_session_view, resource_gantt_view | запуск и разрешение отбора → shift-supervisor-wave.html; пополнение; загрузка ресурсов; разбор недостач | shift-supervisor, resource-gantt | идемпотентный launch (проверяется, C-0090); квалификации и окна ворот волны; пояс |
| Приёмка (`receiving`) | lead_receiving | sap/supply-orders, sap/supply-orders/{id}, warehouse-tasks PUTAWAY | sap_supply_view, warehouse_task_view | приём паллет и закрытие → receiving.html | receiving-lead | фильтр даты поставок; расхождение по паллетам |
| Хранение и ричтраки (`storage`) | lead_storage | warehouse-tasks ×3 статуса &ware_id, resources/warehouse-tasks/{id}/candidates, resources/sessions, resources/timeline | warehouse_task_view, resource_management_view, resource_session_view, resource_gantt_view | назначение ресурса → warehouse-tasks.html; пополнение волны | storage-lead, resource-gantt | идемпотентный dispatch-nearest (склад обязателен, `ware_id` на сервере — C-0091) |
| Диспетчер (`dispatcher`) | dispatcher | transport/tasks, vehicles/gantt, resources/sessions, resources/timeline (ворота, машины) | transport_dispatch_view (native scoped, C-0080), resource_gantt_view | рейс → диспетчеризация; Гант рейсов | workspaces, dispatcher, resource-gantt | выделение рейса и операции в Ганте; опоздания (пояс) |
| Двор и ворота (`yard`) | yard_coordinator | transport/tasks, vehicles/gantt, resources/timeline (ворота, машины) | transport_dispatch_view, resource_gantt_view | назначение ворот — у диспетчера | workspaces | модуль двора: прибытие, очередь, время у ворот (gap) |
| Комплектовщик, ТСД (`picker`) | picker | case-pick/tasks (mine), case-pick/tasks/{id} | case_pick_view | сканы → case-pick-tsd.html | workspaces, tsd-case-pick | — |
| Ричтрак, ТСД (`reach`) | reach_driver | warehouse-tasks?status&assigned_to | warehouse_task_view | сканы и завершение → reachtruck-tsd.html | reach-driver | идемпотентное завершение размещения |
| Водитель, телефон (`driver`) | driver | /api/driver/* под учётной записью водителя (не admin, без cookie, проверено) | привязка водителя | отметки операций (существующий контракт transport) | workspaces | — |

**Справка.** 312 элементов, 0 пропусков (`block5/help_audit`). Опубликованные статьи:
- `workspaces` v6, `resource-gantt` v4, `shift-supervisor` v4;
- `storage-lead`, `receiving-lead`, `reach-driver`, `dispatcher`, `tsd-case-pick` — все v2.

**Не сделано по каталогу:** контролёр качества (нет очереди проверок), грузчик/экспедиция, кросс-док, магазины, транспортное планирование и прочие роли C0049 — без отдельного места. Сами экраны у них существуют (см. `proposals/C0049/ui_map.md`).

**Состояние спринта.** Это read-only проекции и переходы. Полное закрытие спринтов AK05–AK08 по C0074 не заявляется: нет пояса склада, команд с квитанцией на рабочих местах, места контролёра и пилотной или физической приёмки.
