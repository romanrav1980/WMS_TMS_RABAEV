const reasons: Record<string, string> = {
 REGISTERED_TIME_IS_NOT_CERTIFIED_ALL_WORK: "Не подтверждено, что зарегистрирована вся работа смены.",
 NATIVE_APPLIED_CLOCK_NOT_PHYSICAL_PICK_TIME: "Время отбора — момент подтверждения сервером; при задержке связи оно может отличаться от физического действия.",
 HISTORICAL_PACKAGING_NOT_BACKFILLED: "Исторические отборы без сохранённой упаковки не пересчитываются по сегодняшнему справочнику.",
 OPEN_INTERVALS_PROJECTED_TO_AS_OF: "Текущие интервалы времени ограничены моментом наблюдения сервера.",
 NO_LEGACY_TIMEZONE_BACKFILL: "Для старых записей без подтверждённого часового пояса время не восстанавливается догадкой.",
 UNKNOWN_NOT_COUNTED_AS_SUCCESS: "Неизвестный результат не считается успешной доставкой.",
 PENDING_EXCLUDED_FROM_OBSERVED_PERCENT: "Ожидающие события показаны отдельно и не включены в проценты по завершённым наблюдениям.",
 HISTORICAL_QUALITY_WITHOUT_AWARE_CLOCK_NOT_BACKFILLED: "Старые события качества без подтверждённого времени с часовым поясом не восстанавливаются.",
 WHOLE_BOXES_AND_LOOSE_PIECES_SEPARATE: "Коробки считаются только целыми; остаток меньше коробки показан отдельно штуками.",
 APPROVED_SHORT_CREDIT_AT_LAST_PHYSICAL_PICK: "Строка с согласованной недостачей засчитывается последнему физически отобравшему сотруднику во время его отбора, а не согласовавшему руководителю.",
 RETURNS_RETAIN_WORK_LINE_QUALITY_SEPARATE: "Возврат не отменяет выполненную работу; связанные количества показаны отдельно как события качества.",
 QUALITY_IS_NOT_EMPLOYEE_FAULT_ATTRIBUTION: "События качества по заданию не означают вину конкретного сотрудника.",
 PACKAGING_PROOF_UNAVAILABLE: "В исходном отборе нет подтверждённых сведений об упаковке.",
 HISTORICAL_PACKAGING_PROOF_UNAVAILABLE: "В историческом отборе не была сохранена упаковка.",
};

export const sourceReason = (code: string) => reasons[code] ?? "Источник сообщил дополнительное ограничение расчёта.";
export const receiptMode = (mode: string | null) => mode === "WEIGHT_PHOTO" ? "Вес и фотографии"
 : mode === "PAPER_COUNT" ? "Пересчёт по бумаге" : mode === "BARCODE" ? "Сканирование в приложении" : "Нет подтверждённого способа";
