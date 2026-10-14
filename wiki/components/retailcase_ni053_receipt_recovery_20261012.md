# NI05.3: восстановление приёмки магазина

725–728 исправляют существующий useStoreReceipt. Сохранённое тело проходит parseReceiptIntent: текущий адрес, обязательные идентификаторы/подпись/bool, точные decimal количества, UNIT/BOX/PALLET массивы и ограничения UTF8. Malformed intent блокирует новую отправку. Явное восстановление сохраняет исходный raw в архив, перечитывает серверный список грузовых мест и только затем удаляет неизменившийся damaged intent. Ошибка чтения/архивирования или изменение другой вкладкой сохраняет блокировку.

Retry/send/restart проверяют loaded actor/API/trip/address scope и неизменное сохранённое тело. Ответ не удаляет подменённую во время запроса команду. При неизвестном ответе сохраняются исходные operation_id/body. 401/403 и OPERATION_CONFLICT не объявляются подтверждённым неприменением операции; исправление исходного тела по таким ответам не предлагается. Native whole-place unique и original stock core сохранены.

Check727 parser: valid original aggregate body, чужой адрес, malformed array, profile81UTF8bytes и строковый bool проверены. Architecture682files/0cycles/76debt, admin TypeScript PASS. Полноценный браузерный network-loss/recovery и чужая вкладка пока не приняты. Quality71824+оба TypeScript был до этих изменений; после725–726 изменённые architecture/TS проверки пройдены.

[Hook](../../admin/wms_admin_frontend/src/features/delivery/useStoreReceipt.ts), [parser](../../admin/wms_admin_frontend/src/features/delivery/receiptIntentValidation.ts). Товарные SQL не менялись. Серверный список остаётся bounded201 с отказом свыше200; новых запросов на каждую строку нет. Решение delivery: сохранить существующий предел, перед большим числом мест добавить cursor на тот же API, не безграничный список.
