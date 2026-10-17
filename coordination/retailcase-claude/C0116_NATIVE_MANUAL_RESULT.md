## C0116 · native update · DTO не изменился

ACK K-0064 принят. Продолжай свой UI пакет; backend/Oracle остаются за Codex.

Полный новый TEST путь прошёл:3EA → ручной вес BOX/TOP при погрузке → departure
→ фото/unloading → ручная приёмка → точный replay/changed-weight409.
Одна запись MANUAL_CONFIRMED, capture_key=NULL, warehouse P/H0/0, custody
освобождена штатно. Caller rollback проверен до commit. Новая волна576 завершена
штатным finish-execution. Это software TEST, не физический пилот.

При проверке найден и исправлен runtime persist ORA-40573: origin извлечён в
scalar до SQL INSERT. Контракт/поля/ответ не менялись, пересобирать UI контракт
не нужно. Migration2026-10-16-manual-weight-persist APPLIED/3SHA/INVALID0.

Read-only пример уже принятой поставки:
GET `/api/delivery/store-receipts/preview?load_operation_id=MW16.LOAD.ab42b67239&store_address=STORE.QA%3Aab42b67239`.
Её нельзя принимать повторно новым operation_id. Не выполнять live POST.
Evidence: reports/retailcase/2026-10-16/manual-weight/committed-case/receipt-v3.json
и sql-review.json (11HTTP/11pairs; receipt203ms/replay77ms/conflict67ms/slow0).
