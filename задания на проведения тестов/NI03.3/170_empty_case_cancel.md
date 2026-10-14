#170: отмена пустого CASE существующим ядром

Авторские сценарии scripts/ni033_empty_case_existing_case.py и ni033_empty_case_tare_flow.py. История1033/1034 terminal; повтор не сбрасывает статусы и проверяет сохранённый receipt. Для новой проверки rollback/H1 изучить старый fixture и выделить собственное пустоеCASE; нельзя возвращать CANCELLED назад в ASSIGNED.

CASE_CARRIER_RETURN allow_empty=true, destinations{}, актуальный scan_container/version, причина обязательна. Исторический picked/header/line должен быть0; граф/parent/shared or executed picking/незавершённое физическое picking запрещены. Собственный unused HARD освобождается атомарно с отменой CASE/PT/waveTask; физическое количество не перемещается. Проверить реальный rollback после execute_prepared, сохранив H/status/непроведённыйOP.

ПовторOP exact; другаяпричина409; причинапустая422; безallow_empty пустыеdestinations422. Новый флаг/default не должен менять canonical JSON старого физического return. Старый marked/multi-lot return сохраняет прежние rules/owner.

Тара: CASE cancel не выдаётся за возврат тары. HELD блокирует returned-wave completion; существующая TARE_BOOK_CANCEL освобождает её, затем finish. Авторски actual1034/399 PASS, goodtare0/P20H20 сохранялись. UI отдельная кнопка и причина, scan/версия, durable pending/retry/текущие права.

Отдельно проверить нетиповую shared PT/parent/marked empty-case topology: эти позитивные сценарии не заявлены реализованными. Анализ longestSQL и CURRENT OracleVALID/USER_ERRORS обязателен после meaningful нового сценария.
