# Задание ведомому Codex — NI07.2

Ведущий: root. Исполнитель: /root/codex_finance. Начато 14.10.2026 по прямому поручению владельца.

Цель: в существующей сверке дня показать до20 реальных ключей UID+CELL для конфликтов остатков, точные количества и объяснение нарушенного условия. Переиспользовать существующие SQL predicates и согласованный snapshot. Никакого автоматического исправления остатков.

Владение: finance/infrastructure/reconciliation_stock.py, новый helper документов остатков, day_reconciliation.py, wiki-raw/wms_admin_ui_reference/day-reconciliation-documents.js. Общие планы/index/log обновляет ведущий. Claude сохраняет СТ/тару.

Контракт согласован: additive STOCK_ROW / CURRENT_STOCK_SNAPSHOT, однозначные составные document_ids, stock_rows с UID/CELL/base_uom/physical/hard точными строками. has_more от уже полученного count. Ссылки только при наличии действующего точного контракта.

Результат: работающий backend/UI, адресное read-only доказательство API/Oracle, решение по долгим SQL, отчёт reports/nicora/2026-10-13/codex/NI072. Никакого commit/push/DDL. Общий quality gate согласуется с ведущим.

Связь: сообщения агента /root/codex_finance ↔ /root и эта папка. После сдачи ведущий принимает результат и выдаёт следующий независимый блок. Внешний Claude: coordination/nicora-claude; выдача задания не означает его ACK.
