# NI01.1: доступ к этикетке приёмки в текущем складе

Checkpoint677–678, 12.10.2026. inventory владеет существующим ReceiptLabels. Нового генератора или проводки нет.

Выдача этикетки уже проверяла склад; чтение HTML/ZPL и подтверждение скана проверяли только общее HTTP-право. Теперь тот же действующий RRL_SSCC_ALLOCATOR.assert_scope проверяет пользователя, право warehouse_receipt_confirm и склад исходного SAP order перед чтением и подтверждением. При подтверждении склад источника перечитывается после ожидания блокировки этикетки. Сохранённый USED-результат не обходит текущий допуск. Ошибка20882 превращается в403 для выдачи/чтения/подтверждения; GLOBAL_ADMIN остаётся разрешённым.

LabelPort.document и единственный API caller передают actor. HTML/ZPL, исходный SSCC, статус и прежняя логика печати сохранены. Этикетка не подтверждает физическую приёмку и не является государственным кодом агрегации.

Источники: [labels.py](../../api/wms_api_server/app/modules/inventory/infrastructure/labels.py), [LabelPort](../../api/wms_api_server/app/modules/inventory/application/ports.py), [API](../../api/wms_api_server/app/modules/inventory/api/receiving_routes.py).

Python compilation и architecture678/0cycles/76debt PASS. [Native678](../../scripts/check678_native_label_access.py): настоящий READ ONLY Oracle разрешает admin и отклоняет отсутствующего пользователя через тот же native scope; без изменения данных. В dev RRL_RECEIPT_LABEL пуст: положительный HTML/ZPL и отказ чужого склада на USED-кэше ещё не подтверждены. case678_label_scope.py оставлен как адресное задание на существующий label fixture; не заявлять его PASS. Нового fixture/SSCC/печатного устройства не создавали.

SQL состоит из точных LABEL_ID PK → ORDER_ID PK joins и действующего native scope. Решение inventory: сохранить эти ограниченные запросы; реальных label-операций для slow-SQL замера сейчас нет, дополнительный индекс не обоснован. Полный NI01.1/аппаратная печать не закрыты.
