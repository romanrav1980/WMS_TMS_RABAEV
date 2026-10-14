# NI05.3: страницы грузовых мест магазина

731–736 расширяют прежний places API, без второго реестра. Cursor — исходный load operation, limit1..200 (default200 сохраняет список/контракт). Сортировка исходный LOADED_AT + operation_id, сравнение timestamp выполняется в Oracle без потери точности Python/JSON. Anchor принадлежит тому же eligible набору: рейс/адрес/receiver/source members; чужой cursor даёт422. Уже принятые места видны с прежним receipt_state.

Нативный RRL_STOCK_STORE_RECEIPT_READ.require_receiver проверяет текущего получателя перед каждой страницей. Сам запрос повторно проверяет DELETED/right/current receiver binding и GLOBAL_ADMIN wildcard. Повреждённый intent нельзя очищать на основании пустого списка неавторизованного пользователя. Каждый запрос bounded, нет полного replay склада или количества.

В существующей форме страницы100 и кнопка продолжения; дубли строк при перечитывании не добавляются, смена контекста сбрасывает cursor/more. Восстановление725 использует тот же разрешённый список. Check732: исходный доставленный mixed group717/current receiver/page1/empty continuation/foreign cursor/0 и201 bounds. Многорядный same-timestamp источник не проверен. Architecture682/0cycles/76debt и adminTS PASS после замены Array.at на совместимый текущей target обращение по индексу.

SQL735 lookup19.080мс/70.5buffers и page11.724мс/33buffers. Решение delivery: сохранить bounded CTE и существующие load/trip/recipient индексы; индекс без плана не добавлять. Перед промышленным fanout владелец delivery проверяет материализацию eligible/plan по текущей статистике. Browser acceptance и HTTP после API735 reload ещё открыты.

[Service](../../api/wms_api_server/app/modules/delivery/infrastructure/store_receipt.py), [форма](../../admin/wms_admin_frontend/src/features/delivery/StoreReceiptPanel.tsx). Stock/native quantity API не менялись.
