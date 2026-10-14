# NI01.1 — внутренний идентификатор SAP-приёмки
Для локальной Qwen. Не запускать широкий regression/load и не пересоздавать источники669/670/671/672/688.

Прочитать wiki/database/nicora_ni011_internal_receipt_identifier_20261012.md. Авторский actual688 выполнен: tmp/context688.json stageDONE, UID47, новая паллетаP3H0, три единицы/шесть кодов, PUTAWAY DONE. UID паллеты отличен от регуляторного SSCC.

1. Read-only подтвердить точный UID/исходный SAP order/line и task из контекста. PALLETS.SSCC и TASK.SSCC=NULL; нет CRPT parent aggregation/PARENT_SSCC. Коды единиц присутствуют; это не внешний legal ACK.
2. Только сохранённый birth operation_id/body можно повторить; должен вернуться прежний результат. Старый receipt669 уже отгружен и повторён689 без нового P/H; не восстанавливать его.
3. В новом изолированном fixture проверить старое имя sscc, новое pallet_identifier и оба одинаковых имени после GS1-prefix normalization. Конфликт двух имён, пробелы, непечатные символы, >50char/>150UTF8bytes и неверный18-digit check digit дают422 или confirmed business refusal без P/H/units/event/outbox.
4. Raw receiving.html: поле называется «Идентификатор паллеты», принимает legacy47. Передача/восстановление pending intent сохраняют точный UID и operation_id; нативное размещение сканирует UID, не выдуманный SSCC.
5. Отдельный настоящий GS1 PALLET aggregate при внутреннем UID должен иметь собственный подтверждённый SSCC и связь с тем же UID через существующий parent resolver125. Эта новая комбинация не проверена688: там CRPT UNIT и EGAIS BOX.
6. Этикетки677: текущий warehouse scope для HTML/ZPL и USED confirmation. RRL_RECEIPT_LABEL был пуст на678, поэтому нужен отдельный metadata label fixture; аппаратная печать не подтверждается по DTO или HTML.

Отчёт: точный источник/состав/P,H/unit-key/code-count до/после, отрицательный случай/повтор/current actor-WARE; slow SQL и решение. Не выдавать XML fixture за production SAP IDoc или реальные государственные коды.
