# Возврат содержимого CASE по области руководителя

Статус16.10 dev APPLIED/3SHA/ERROR0/INVALID0 после отдельного compile completion. Только `CASE_CARRIER_RETURN`: текущая `case_pick_manage` WARE/GROUP роль в native `RRL_CASE_TASK_ACCESS.assert_command`, без открытия legacy metadata TRANSFER. Проверяются фактическая CASE, исходные/возвратные ячейки строк и текущий активный пользователь. Прежние legacy ветки сохраняются. Return execute повторяет тот же native допуск; Root берёт shared REV до повторной проверки и cached replay.

Количество, release резервов, CASE cancellation, исходные сканы/полный набор lots/версии/stock locks/booking остаются у прежнего `RRL_STOCK_CASE_RETURN_CMD`. Пустая отмена не расширяется на произвольные CASE: её существующие проверки остаются. HTTP только identity + отображение native403/409/uncertain503. Новая штатная проверка: изолированная свежая CASE25EA, caller rollback, точный replay, revoke/group/foreign и REV. Shipping/transfer/multi-store этим не закрываются.

Before3 sources/INVALID0: `reports/retailcase/2026-10-16/case-manager-scopes/return-before/`. SQL в `db/migrations/2026-10-16_case_return_scope`; owner inventory/resources. См. [[../roadmap/retailcase_finish_two_claude_20261016]].

Frozen original SHA `d2b86159b29d27b22323deda616c3981736ae7154684bb5fb1ba7fa94ab36a1d`. Первое применение установило3 body, verify обнаружил ошибку CELL в таблице связей CASE_CARRIER_LOT. DDL не повторялся, исходные файлы/ошибки сохранены. Отдельный `2026-10-16_case_return_scope_completion`, SHA `d5a84d4c534382f21dd087507c35e385bead5f5ad91f0d4613445905ab702a65`, исправил одну body через фактические RRL_REMAINS, source guard и readback3SHA/ERROR0/INVALID0. Оба ledger APPLIED подтверждены; общий rollback после новой истории не применять, только forward repair.

Свежая CASE1149/WARE20382575: BOX24+EA1/25EA закрыта, затем manager home1/flat manage0 выполнил полный RETURN.10 actual HTTP PASS: WARE, exact replay, changed body409, чужая CASE403, исполнитель без manage403, revoke403, GROUP restore/replay и member-remove403. Caller rollback сохранил исходную CASE/версию/товар; второй connection получил REV ORA54. После commit25EA в исходных ячейках/H0, CASE CANCELLED, повторного эффекта нет. Источник `return-acceptance.json`; native прямым вызовам не приписываются HTTP IDs.

Проверочные manager/ordinary/parent identities, grants, TEST device и session70 отключены штатно. FINISH волны584 подтверждённо отклонён WAVE_EXECUTION_OR_SHIPPING_PENDING (возвращённое не считается отгруженным). Отдельная каноническая WAVE_CANCEL завершила волну CANCELLED; история/товар сохранены, `retirement/wave-cancel.json`. Изменение API ошибки403/409/uncertain503 проверено3 boundary tests.

После физического RETURN отдельный TARE_BOOK_CANCEL освободил hold пустой тары отменённой CASE: physical2/assembly0, без обнуления физической TEST тары и удаления истории. `retirement/tare-release.json`, native294мс; этому прямому вызову не приписан HTTP ID.
