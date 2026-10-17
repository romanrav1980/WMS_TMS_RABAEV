"""C-0049/C0056: справочники ролевой модели — семейства, области, устройства, новые права, SoD и паспорт KPI."""

FAMILIES = {
    "leadership": "Руководство сети и РЦ",
    "warehouse_ops": "Управление складскими операциями",
    "warehouse_exec": "Складское исполнение",
    "stock_control": "Запас, качество, возвраты и тара",
    "transport": "Транспорт",
    "store": "Магазины",
    "support": "Финансы, аналитика, ИТ и контроль",
}

# Виды областей приняты в wiki/architecture/retailcase_scoped_access_and_knowledge.md.
SCOPES = {
    "WAREHOUSE": "склад",
    "DC": "распределительный центр",
    "ZONE": "подсклад/участок склада",
    "STORE": "магазин",
    "REGION": "регион магазинов",
    "CARRIER": "перевозчик",
    "ORG_BRANCH": "организационная ветвь (ВИД:КОД)",
    "GROUP": "именованная группа объектов одного вида",
    "SELF": "свои объекты (проверенная серверная привязка)",
    "NETWORK": "вся сеть",
    "PLATFORM": "системные полномочия платформы",
}

DEVICES = {"desktop": "desktop", "tablet": "планшет", "mobile": "телефон", "tsd": "ТСД"}

# Состояние рабочего места роли. Справочник не выдаётся за реализованный UI.
WORKSPACE_STATUS = {
    "existing_screens": "работает на существующих экранах без ролевой главной",
    "planned": "ролевое рабочее место спроектировано, не реализовано",
    "in_c0056": "реализуется в C0056 (блок 4)",
    "gap": "основного экрана нет",
}

# Права, которых нет ни в API, ни в RIGHTS. Права модуля доступа/знаний — из ACCESS_KNOWLEDGE_API_V1 (реализует Codex).
NEW_RIGHTS = {
    "stock_adjust_approve": "Утверждение расхождения пересчёта выше порога (КРО). Сейчас POST …/inventory/counts проводит результат сразу под stock_inventory_count.",
    "cell_availability_edit": "Блокировка ячеек для карантина без права редактировать топологию (сейчас warehouse_topology_edit на /api/admin/topology-cells).",
    "network_kpi_view": "Сводка нескольких РЦ. Все KPI-чтения сейчас в области одного склада (require_warehouse).",
    "store_region_view": "Чтение приёмок/кейсов/возвратов магазинов ветви без права подтверждать.",
    "carrier_manage": "Карточка перевозчика, договор, закрепление машин/водителей. Модуля перевозчиков нет.",
    "yard_gate_manage": "Очередь машин у ворот, прибытие/убытие. Сейчас ворота меняются legacy change_tt_dock и transport_dispatch_edit.",
}

# Права, которые проверяются native/Oracle (не декоратором маршрута); реализованы Codex.
ORACLE_RIGHTS = {
    "access_admin_view": "модуль доступа: просмотр каталога/групп/назначений (C-0058)",
    "access_role_manage": "модуль доступа: состав ролей; в первой редакции ROLE_SAVE — только GLOBAL_ADMIN (C-0057)",
    "access_group_manage": "модуль доступа: группы объектов, native coverage мандата (C-0058/C-0064)",
    "access_assign_manage": "модуль доступа: назначения в пределах мандата (C-0058)",
    "knowledge_edit": "база знаний: черновики (C-0058)",
    "knowledge_publish": "база знаний: публикация/архив и права чтения статьи (C-0058)",
    "expense_logist_approve": "стадия LOGIST расхода по фактическому складу, без права ставок (C-0066)",
    "expense_finance_approve": "стадия FINANCE расхода по фактическому складу, без права ставок (C-0066)",
}

# Разделение обязанностей на уровне ЧЕЛОВЕКА: совокупность всех активных назначений одного пользователя.
# (право A, право B, почему, как обеспечено сейчас)
PERSON_RULES = [
    ("stock_inventory_count", "stock_adjust_approve", "пересчитавший не утверждает расхождения склада, где сам считает", "GAP: утверждения нет"),
]

# Разделение на уровне ОБЪЕКТА: автор конкретного документа не выполняет следующий шаг по нему. Проверка — только на сервере.
# (объект, шаг автора, шаг проверяющего, почему, текущее обеспечение)
OBJECT_RULES = [
    ("Недостача комплектации (RRL case-pick short)", "POST …/lines/{line_id}/short (created_by)", "POST /api/case-pick/shorts/{short_id}/approve (approved_by)",
     "комплектовщик не подтверждает собственную недостачу", "GAP: в ответе есть created_by/approved_by, запрет совпадения не найден"),
    ("Дополнительный расход", "POST /api/finance/logistics-expenses/report (edit_bill_tt)", "POST …/decide LOGIST (expense_logist_approve) и FINANCE (expense_finance_approve)",
     "автор расхода не решает стадии; LOGIST и FINANCE — разные люди", "обеспечено native: RRL_LOG_EXPENSE_GUARD / RRL_LOG_EXP_DECISION_GUARD, в т. ч. для GLOBAL_ADMIN (C-0066)"),
    ("Приёмка поставки SAP", "POST …/supply-orders/{id}/pallets (warehouse_receipt_confirm)", "POST …/stock-posting receipt-reverse (stock_receipt_reverse)",
     "принявший не сторнирует свою приёмку", "GAP: проверка автора не найдена"),
    ("Акт приёмки магазина", "POST /api/delivery/store-receipts/confirm (store_receipt_confirm)", "POST /api/delivery/case-work/{case_id}/loss (store_loss_confirm)",
     "подписавший акт не утверждает потерю по нему", "GAP: проверка автора не найдена"),
    ("Недостача тары", "POST /api/inventory/tare/loss-report (tare_loss_report)", "POST /api/inventory/tare/loss-decide (tare_writeoff)",
     "сообщивший не списывает", "обеспечено native: RRL_STOCK_TARE_LOSS — TARE_INDEPENDENT_LOSS_DECISION_REQUIRED (C-0065)"),
    ("Возврат магазина", "приём водителем (driver_return_accept)", "POST /api/delivery/store-returns/{id}/approve (store_return_approve)",
     "принявший возврат не утверждает его", "GAP: проверка автора не найдена"),
]

# Параметры профиля РЦ (настройка склада, не константа UI). Значения по ТЗ resource_management.md — пример основного РЦ.
WAREHOUSE_PROFILE = {
    "reach_shift_start": "старт смены ричтраков (ТЗ: 18:00 основного РЦ)",
    "picking_start_offset": "сдвиг старта комплектации от ричтраков (ТЗ: ~2 ч)",
    "waves_secured_before_end": "все волны обеспечены за N ч до конца смены (ТЗ: 2 ч)",
    "pick_recovery_limit_min": "предел восстановления отбора, мин (ТЗ: 5)",
    "orders_cutoff": "приём заказов сети (ТЗ: до 16:00)",
}


def K(name, unit, formula, fields, period, scope, zero, src, status="proposal"):
    """Паспорт KPI. status: proposal (не утверждён владельцем) | gap (нет данных). Значения не выдумываются."""
    return dict(name=name, unit=unit, formula=formula, fields=fields, period=period, scope=scope, zero=zero, source=src, status=status)


NO_DATA = "знаменатель 0 → «нет данных», не 0%"
