const rules: Record<string, string> = {
 STORE_RECEIVER_ADDRESS_BINDING_REQUIRED: "Получатель не назначен на этот адрес магазина.",
 STORE_RECEIPT_FROZEN_SINGLE_DESTINATION_REQUIRED: "Адрес грузового места не соответствует этому магазину или ещё не подтверждён.",
 STORE_RECEIPT_WEIGHT_AND_PHOTOS_REQUIRED: "Для этого адреса обязательны взвешивание и фотографии.",
 STORE_RECEIPT_PAPER_REFERENCE_REQUIRED: "Для пересчёта по бумаге нужен номер/реквизит бумажного документа.",
 STORE_MARKED_RECIPIENT_FLOW_REQUIRED: "Требуются сверка маркированных единиц и необходимые внешние подтверждения.",
 STORE_PLACE_ALREADY_RECEIVED: "Грузовое место уже принято.",
 STORE_RECEIPT_PHYSICAL_PLACE_SCAN_REQUIRED: "Скан не соответствует выбранному грузовому месту.",
 STORE_RECEIPT_BEFORE_CAMERAS_REQUIRED: "Установите грузовое место перед камерами перед подтверждением.",
 STORE_RECEIPT_ACTUAL_DEPARTURE_REQUIRED: "Сначала требуется подтверждение выезда загруженного рейса.",
 STORE_RECEIPT_FORBIDDEN: "Нет права подтверждать приёмку этого магазина.",
 PHOTO_ARCHIVE_LIMIT_12: "В архиве этого грузового места уже 12 фотографий.",
 OPERATION_CONFLICT: "Идентификатор операции связан с другими данными. Проверьте состояние приёмки.",
 RESULT_UNCERTAIN: "Результат пока не подтверждён. Повторите сохранённую операцию.",
 CLOSURE_CHANGED: "Состояние места или настройки изменились. Обновите данные.",
 NOT_VISIBLE: "Запись недоступна для вашей учётной записи. Это не подтверждение отмены.",
};

export function humanStoreMessage(reason: string): string {
 for (const [rule, text] of Object.entries(rules)) if (reason.includes(rule)) return text;
 return /[А-Яа-яЁё]/.test(reason) && !reason.includes("ORA-") ? reason : "Действие не подтверждено. Обновите состояние и повторите сохранённые данные.";
}
