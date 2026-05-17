# Production Release File Exchange

Этот каталог нужен для приема заданий на выпуск готовой продукции из внешней системы через файловый обмен.

Worker читает UTF-8 JSON из `in/`, переносит файл в `processing/`, выполняет MES-выпуск через Oracle/API слой, пишет ответ в `out/`, а исходный файл переносит в `archive/` или `error/`.

## Каталоги

- `in/` - входящие JSON-файлы.
- `processing/` - файл на время обработки.
- `archive/` - успешно обработанные файлы.
- `error/` - файлы с ошибками.
- `out/` - результат обработки по `messageId`.

## Минимальный JSON

```json
{
  "messageId": "FILE-MES-20260517-0001",
  "sourceSystem": "FACTORY-MES",
  "orderNo": "FILE-MES-ORDER-0001",
  "targetArticul": "FG-FILE-PETFOOD",
  "plannedQty": 100,
  "factQty": 100,
  "unitCode": "KG",
  "wareId": 9102,
  "productionLine": "LINE-FILE",
  "prodBatchNo": "FILE-MES-LOT-0001",
  "rawIssues": [
    {
      "uidPallet": "FILE-MES-RAW-0001",
      "rawArticul": "RM-MEAT-BEEF-FROZ-01",
      "quantity": 50,
      "unitCode": "KG",
      "sourceLocation": "RM-A01-01",
      "productionLocation": "MES_PROD"
    }
  ],
  "pallets": [
    {
      "uidPallet": "FILE-MES-FG-0001",
      "palletNo": 1,
      "quantity": 100,
      "packCount": 10,
      "sscc": "000000000000000001"
    }
  ],
  "applyWms": true
}
```

## Идемпотентность

`messageId` является ключом идемпотентности и хранится в Oracle `RRL_FILE_EXCHANGE_LOG`.

- Повтор того же файла с тем же hash после успешной обработки вернет `DUPLICATE`.
- Повтор с тем же `messageId`, но другим содержимым считается ошибкой `HASH_CONFLICT`.
- Создание заказа и завершение производства также получают idempotency keys вида `{messageId}:order` и `{messageId}:complete`.

## Запуск

```bat
production-exchange.bat
```

Переменная `WMS_PRODUCTION_EXCHANGE_ROOT_DIR` позволяет указать другой корень обмена.
