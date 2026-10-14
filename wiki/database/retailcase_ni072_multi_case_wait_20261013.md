# NI07.2 — несколько CASE одной СТ

986 PREPARED, migration2026-10-13-007-ni072-multi-case-wait. Current985 spec/body sources captured, SHA/paired rollback/no DBcopy.

Existing ST deferral/WAIT_API/CASE mover reused. OneCASE still PREPARED_CASE with previous shape. Several fully prepared standalone CASEs produce PREPARED_CASES/cases[], each member has oneCASE and onePICKED FF/current ownWARE/complete carrier/own HARD. Up to200 members AND total200 physical lots, distinct carrier identifiers; no sum across different goods/UOM. Mixed FULLPAL/CASE, unfinished/nested/slots/capacity/resource sessions remain explicit refusals.

One plan run registers only needed movements; cases already waiting are recorded as skipped. Each WHT keeps its own immutable child source JSON/CASEID/version and self sourceTaskID; execution freezes that child and current global decision/trip/warehouse config/load state. First sibling completion changes its own CASE/FF/stock, so the second child can still execute against its unchanged source. Root keys/trip lock and current active-load check protect the source; original nativeCASE/ST/FF/lot/reserve/unit locks retained. Same existing Root movement finishes WHT/SYNC/outbox and one FF-version owner974.

No physical parent/residual is invented. Old single CASE plans/replays preserve their original body/shape. Rollback restores code but cannot erase registered multi-place history; unsupported older planner afterrollback needs explicit recovery planning. Need livecompile + private retained12/8 groupedST scenario; no fullsprint closure before actual.

## Checkpoint991

# NI07.2 — несколько CASE одной СТ

986 APPLIED/VALID. Несколько полностью подготовленных самостоятельных CASE однойСТ получают отдельные immutable child plans; первое исполнение не меняет исходник второго. Старый одно-CASE JSON сохранён. До200мест и суммарно200партий; ячейки/WARE/decision/trip/load state текущие, выполняет прежний CASE_CARRIER_MOVE/TRANSFER_CORE/один FF-version owner. MixedFULLPAL, вложенныйHU и ресурсные/slot/capacity ветви пока отдельно.

Actual987: одна новая собственная devСТ изначально содержит два member и CASE1131/1132 с12+8EA. Ни один старый источник не пересоздавался. Оригинальная комплектация, бронирование тары, привязка кСТ и genericCASE move подготовили груз. Штатная TMS переназначила оба места одним решением. План двух WHT rollback/replay прошёл. Task1136 и1137 завершены по1CASE; после первого второй frozen-source корректно исполнился. CASE/FF версии3/3 каждого, P20/H20, WHT journals12+8EA, outbox5114/5115, exact replays. ProtectedWARE6667491P20H20 unchanged. Новые собственные20/H20 retainedдля следующего HU-сценария, не очищены.

SQL988 boundedcurrentCASE/ST queries0.189–12.589ms/1.9–104.4buf. Inventory owner сохраняет200member/total200lot bound и существующие ключи; maxlargeST production profile остаётся отдельнойприёмкой, новыйиндекснеобоснован. Currentnative compileErrors[]/Invalid[]. Rollback сохранён, неиспытан; зарегистрированную многоместнуюисториюнеудаляет. НезависимоеQwen/Gov/оборудование не заявляются выполненными.

Обнаружен следующий связанный пробел в CURRENT RRL_STOCK_HU_CMD (capture990): упаковка/распаковка прямого CASE и движение дерева повышают CASE version, но не обновляют активный boundFF. Подключается существующий binding core974 к этим операциям. Товарныйэффект остаётся в прежнемRoot и листьях; матрёшка HU уже есть.
