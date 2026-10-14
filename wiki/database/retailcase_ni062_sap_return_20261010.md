# NI06.2 — SAP-документ возврата через шлюз
10.10.2026, ticket093. [Проект](retailcase_ni062_sap_return_design_20261010.md), [миграция](../../db/migrations/2026-10-10_ni062_sap_return/apply.sql). 2026-10-10-093-sap-store-return-binding APPLIED, package/body/root/guard VALID в RABAEV.

Предполагаемый XML WarehouseStoreReturn version1 содержит Sender,MessageId,ReturnDocumentNumber,ApprovalOperationId,OriginalReceiptOperationId,OriginalLineNumber,WarehouseId,ReceiveCell,Article,LotId,Quantity unit,Disposition. Это явный локальный gateway-контракт, не заявленный стандартный SAP IDoc. Один документ связан с одним approval092. Поля и исходные количества сверяются Oracle с approval, XMLTABLE сверяет оригинальный XML с переданными metadata. UTF-8 bytes сохраняются base64+SHA256. DTD/entities запрещены, XML≤16KiB.

Root STORE_RETURN_SAP_BIND использует существующий short transaction/outbox/exact replay. Unique approval/sender-message/sender-document, sorted source/doc locks и повторный источник под блокировкой. Никакой закупочной накладной или рождения P. API POST /api/integrations/sap/store-returns, право sap_return_import. Импортированный контракт отдельно от внешнего SAP ACK.

Worker [sap_store_return_worker.py](../../api/wms_api_server/app/workers/sap_store_return_worker.py) использует существующий exclusive file gateway/archive/error/recovery и явно выбранного активного RUSERS actor. Пример из API directory: .venv/Scripts/python -m app.workers.sap_store_return_worker --actor SERVICE_USER --watch. SERVICE_USER должен быть настроен с sap_return_import; пользователь/секрет автоматически не создаётся. Default exchange/sap_store_returns. Реального SAP sender/configuration нет в авторском случае.

Фактический авторский case связал собственный SUPPLIER approval bea258a7dd с warehouse9104/FG-A01-01. Exact raw/retry/hash/source/quantity/foreign cell/direct raw-field spoof/duplicate binding/immutable guard прошли. Events0, outbox1. Исходный XML восстановлен byte-for-byte. Store return dossier показывает реальный SAP return document по каждому approval; фактическая приёмка склада отдельно.

Slow SQL: XMLTABLE20.746ms average, duplicate lookup20.132ms, insert16.483ms. Решение: bounded16KiB single document, существующие unique indexes approval/sender-doc/message; capacity не заявляется. При росте потока owner integrations проверяет plan OR lookup и split indexed exists, без раннего cache mutable admission.

Логистический вывоз и физическая приёмка/размещение ещё не выполнены; NI06.2 in_progress. Маркированный возврат не пропускается без exact unit lifecycle.
