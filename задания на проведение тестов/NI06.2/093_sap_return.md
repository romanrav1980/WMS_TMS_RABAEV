# Qwen ticket093
Использовать собственный approved ordinary return; scripts/ni062_sap_return_case.py уже связал его конкретное основание, не повторять на том же approval.
Проверить UTF-8 XML WarehouseStoreReturn v1, original receipt/line/lot/article/BASE qty/disposition, configured warehouse receiving zone. Отказать неизвестным/duplicate fields, DTD/entities, XML>16KiB, ошибочному qty/unit, чужому approval и blocked/foreign receiving cell.

В Oracle проверить raw bytes base64+SHA, XMLTABLE source metadata matching, no direct spoof, immutable guard, exact original message replay, same MessageId/different bytes conflict, duplicate document/approval refusal. P/H/events unchanged, one outbox. Не объявлять synthetic XML real SAP ACK.

Worker exclusive gateway должен сохранить archive/result и повторить abandoned claim без второго binding. Настроить отдельного разрешённого service actor, не использовать реальные секреты в отчёте. После meaningful case — slow SQL decision.
