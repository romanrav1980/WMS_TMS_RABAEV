// Каталог показателей сверки дня (NI07.2): подпись, процесс, смысл, следующее действие и ссылка.
// Ключи — ровно поля ответа GET /api/finance/day-reconciliation/warehouses/{ware_id}
// (modules/finance/infrastructure/reconciliation_sources.py, day_reconciliation.py).
// Ссылки ведут на существующие реестры: ответ API агрегатный, ID конкретных документов в нём нет.
(() => {
  const registry = (href, label) => ({ href, label, kind: "registry" });
  const section = (href, label) => ({ href, label, kind: "section" });

  const processes = [
    ["warehouse", "Склад"],
    ["interwarehouse", "Межскладские перемещения"],
    ["shipping", "Погрузка и выезд"],
    ["stores", "Магазины"],
    ["returns", "Возвраты"],
    ["tare", "Оборотная тара"],
    ["finance", "Расчёты и расходы"],
    ["stock", "Остатки и состав"],
    ["external", "Внешние подтверждения"]
  ];

  const facts = {
    warehouse_tasks_started: { title: "Начато складских заданий", process: "warehouse", meaning: "Задания с подтверждённым временем начала в выбранных сутках" },
    warehouse_tasks_finished: { title: "Завершено складских заданий", process: "warehouse", meaning: "Статус DONE и подтверждённое время завершения в выбранных сутках" },
    interwarehouse_unloads: { title: "Межскладских выгрузок", process: "interwarehouse", meaning: "Выгрузки межскладского плеча на этом складе" },
    interwarehouse_receipts: { title: "Межскладских приёмок", process: "interwarehouse", meaning: "Подтверждённые приёмки межскладского груза" },
    physical_places_loaded: { title: "Погружено мест", process: "shipping", meaning: "Физические верхние места, погруженные в машины" },
    physical_places_departed: { title: "Выехало мест", process: "shipping", meaning: "Погруженные места с подтверждённым выездом" },
    trips_departed: { title: "Выехало рейсов", process: "shipping", meaning: "Рейсы с хотя бы одним выехавшим местом" },
    store_unloads_started: { title: "Начато выгрузок в магазинах", process: "stores", meaning: "Начало выгрузки по местам этого склада" },
    store_unloads_completed_by_start_day: { title: "Завершено выгрузок (по дню начала)", process: "stores", meaning: "Выгрузки, начатые в эти сутки и уже завершённые" },
    store_receipts: { title: "Приёмок магазинами", process: "stores", meaning: "Подтверждённые приёмки получателями" },
    delivery_cases_closed: { title: "Закрыто разбирательств доставки", process: "stores", meaning: "Закрытые случаи расхождений" },
    return_receipts: { title: "Приёмок возвратов складом", process: "returns", meaning: "Возвраты, физически принятые складом" },
    tare_operations: { title: "Операций с тарой", process: "tare", meaning: "Записи журнала тары с балансом этого склада" },
    warehouse_cost_runs: { title: "Складских расчётов", process: "finance", meaning: "Расчёты складских затрат без транспортной части" },
    transport_cost_runs: { title: "Нормативных транспортных начислений", process: "finance", meaning: "Расчёты, привязанные к выезду рейса" },
    expense_reports: { title: "Расходов и корректирующих актов", process: "finance", meaning: "Зарегистрированные дополнительные расходы" }
  };

  const backlog = {
    open_warehouse_tasks: { title: "Незавершённые складские задания", process: "warehouse", meaning: "Задания не в статусе DONE/CANCELLED, включая прошлые дни", action: "Открыть очередь и довести или отменить задания по процессу", link: registry("warehouse-tasks.html", "Реестр складских заданий") },
    interwarehouse_unload_pending: { title: "Межскладское плечо не выгружено", process: "interwarehouse", meaning: "Есть план плеча на этот склад без факта выгрузки", action: "Проверить прибытие и выполнить выгрузку", link: registry("interwarehouse.html", "Межскладской поток") },
    interwarehouse_receipt_pending: { title: "Выгружено, но не принято", process: "interwarehouse", meaning: "Выгрузка есть, приёмки межскладского груза нет", action: "Выполнить приёмку выгруженного груза", link: registry("interwarehouse.html", "Межскладской поток") },
    interwarehouse_custody_pending: { title: "Нет подтверждения передачи", process: "interwarehouse", meaning: "Приёмка без подтверждения передачи ответственности", action: "Оформить подтверждение передачи", link: registry("interwarehouse.html", "Межскладской поток") },
    interwarehouse_placement_pending: { title: "Принято, но не размещено", process: "interwarehouse", meaning: "Межскладская приёмка без размещения", action: "Выдать и выполнить размещение", link: registry("interwarehouse-groups.html", "Межскладские грузовые места") },
    interwarehouse_onward_pending: { title: "Нет отправки на следующее плечо", process: "interwarehouse", meaning: "Размещённый межскладской груз без дальнейшей отправки", action: "Запланировать следующее плечо", link: registry("interwarehouse.html", "Межскладской поток") },
    store_unloads_open: { title: "Выгрузка в магазине не завершена", process: "stores", meaning: "Начало выгрузки зарегистрировано, завершения нет", action: "Уточнить у получателя и завершить приёмку магазина", link: null },
    delivery_discrepancies: { title: "Открытые расхождения доставки", process: "stores", meaning: "Случаи расхождения не в статусе CLOSED", action: "Разобрать расхождение и принять решение", link: registry("store-investigations.html", "Расследования доставки") },
    return_placement_pending: { title: "Возвраты без размещения", process: "returns", meaning: "Принятые возвраты без размещения и без утилизации", action: "Разместить возврат или оформить утилизацию", link: registry("store-return-putaway.html", "Размещение возвратов") },
    supplier_handover_pending: { title: "Передача поставщику не подтверждена", process: "returns", meaning: "Отправка поставщику без подтверждённой передачи", action: "Получить и внести подтверждение поставщика", link: registry("supplier-handover.html", "Передача поставщику") },
    disposal_pending: { title: "Брак ожидает утилизации", process: "returns", meaning: "Возврат с решением DISPOSAL без факта утилизации", action: "Провести утилизацию по акту", link: registry("return-disposal.html", "Утилизация") },
    tare_offers_unaccepted: { title: "Тара предложена, приём не подтверждён", process: "tare", meaning: "Возврат тары предложен, вторая сторона не приняла и не отменила", action: "Получить подтверждение приёма второй стороной", link: registry("tare-ledger.html", "Оборотная тара") },
    tare_loss_unresolved: { title: "Недостача тары без решения", process: "tare", meaning: "Заявка о недостаче без решения", action: "Принять решение по недостаче", link: registry("tare-loss.html", "Недостача тары") },
    transport_cost_unrecognized: { title: "Выезды без транспортного начисления", process: "finance", meaning: "Архивные выезды склада без нормативного начисления перевозчику", action: "Проверить нормативы и выполнить начисление", link: registry("logistics-costs.html", "Затраты рейса") },
    expense_approval_pending: { title: "Расходы без окончательного решения", process: "finance", meaning: "Нет финансового согласования и нет отказа", action: "Согласовать или отклонить расход", link: registry("logistics-expenses.html", "Дополнительные расходы") },
    expense_allocation_pending: { title: "Расходы рейса без распределения", process: "finance", meaning: "Финансово одобренный расход рейса не распределён", action: "Распределить расход по рейсу", link: registry("logistics-expenses.html", "Дополнительные расходы") }
  };

  // Коды open_items, которые сервер выводит не из current_backlog, а из грузовой зоны, остатков и внешних систем.
  const derived = {
    shipping_register_page_incomplete: { title: "Реестр грузовой зоны прочитан не полностью", process: "shipping", meaning: "В отчёт вошла только первая страница реестра (20 строк)", action: "Пролистать реестр грузовой зоны ниже на этой странице", link: section("#shippingArea", "Грузовая зона на этой странице") },
    shipping_zone_classification_incomplete: { title: "Классификация грузовой зоны неполная", process: "shipping", meaning: "Не все ячейки склада классифицированы в опубликованной топологии — пустота зоны не доказана", action: "Проверить зарегистрированные ячейки грузовой зоны", link: section("#shippingArea", "Грузовая зона на этой странице") },
    shipping_declared_cells_occupied: { title: "Ячейки грузовой зоны заняты", process: "shipping", meaning: "В зарегистрированных ячейках грузовой зоны есть запас или неотгруженные места", action: "Проверить занятые ячейки и отгрузить или переместить груз", link: section("#shippingArea", "Грузовая зона на этой странице") },
    shipping_members_not_departed_in_page: { title: "Места СТ без подтверждённого выезда", process: "shipping", meaning: "Число в пределах прочитанной страницы реестра", action: "Проверить погрузку и выезд", link: section("#shippingArea", "Грузовая зона на этой странице") },
    stock_quantity_invariants: { title: "Некорректные строки запаса", process: "stock", meaning: "Отрицательный или пустой остаток, резерв больше остатка, нет единицы", action: "Передать владельцу ядра остатков для разбора", link: null },
    physical_unit_composition: { title: "Конфликты состава физических единиц", process: "stock", meaning: "Остаток паллеты не совпадает с зарегистрированными единицами", action: "Проверить состав паллеты", link: registry("pallet-composition.html", "Состав и происхождение паллеты") },
    external_erp_ack_pending: { title: "ERP не подтвердила", process: "external", meaning: "Записи для ERP без подтверждения (выгружено или отклонено)", action: "Дождаться ответа ERP или разобрать отказ", link: null },
    regulatory_ack_not_reconciled: { title: "Сообщения маркировки не сверены с госответом", process: "external", meaning: "Отчёт не сверяет принятие государственной системой", action: "Проверить статусы в журнале внешних сообщений", link: registry("external-outbox.html", "Журнал внешних сообщений") },
    regulatory_stock_source_unverified: { title: "Исходные проводки сообщений не подтверждены", process: "external", meaning: "Сообщение ссылается на складскую операцию не в состоянии APPLIED", action: "Проверить исходную операцию сообщения", link: registry("external-outbox.html", "Журнал внешних сообщений") }
  };

  const erpStatus = {
    EXPORTED: { label: "Отправлено в ERP, ответ ожидается", tone: "pending" },
    REJECTED: { label: "ERP отклонила", tone: "bad" },
    PENDING: { label: "Ожидает выгрузки в ERP", tone: "pending" },
    NEW: { label: "Ожидает выгрузки в ERP", tone: "pending" }
  };

  // Для госсистем «отправлено» — только факт доставки сообщения; принятие системой этот отчёт не сверяет.
  const deliveryStatus = {
    DONE: { label: "Отправлено", tone: "sent" },
    EXPORTED: { label: "Отправлено", tone: "sent" },
    ACKNOWLEDGED: { label: "Доставка подтверждена каналом", tone: "sent" },
    NEW: { label: "Ожидает отправки", tone: "pending" },
    PENDING: { label: "Ожидает отправки", tone: "pending" },
    ERROR: { label: "Ошибка отправки", tone: "bad" },
    FAILED: { label: "Ошибка отправки", tone: "bad" }
  };

  window.dayReconCatalog = { processes, facts, backlog, derived, erpStatus, deliveryStatus };
})();
