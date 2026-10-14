# NI03.3: текущий склад чтения CASE (164)

Владелец resources; inventory public сохраняет физический состав и тару. Найден фактический пробел: /api/case-pick/tasks и /tasks/{id} проверяли case_pick_view, но не использовали пользователя при чтении. Исправлены именно эти входы. Это не заявление проверки всех остальных CASE endpoints.

Текущие RUSERS.DELETED/WARE_ID/USER_GROUP и право читаются в одном READ ONLY snapshot с карточкой/очередью. GLOBAL_ADMIN сохраняет прежний all-rights scope. Чужое задание/ресурс403, отсутствующее404, невалидный scope/limit422. Без склада личный viewer не получает данные. Поля старого списка/карточки, Decimal-text quantities, линии, physical_lots и tare сохранены.

Существующий query reader выделен из CasePickService в resources/infrastructure/case_read_model.py; сервисные internal callers сохраняют совместимый delegate. Public API использует ScopedCaseReads через DI. Старый внутренний reader не объявляется авторизованным API. Команды claim/start/confirm/transfer и ядро проводки не изменены.

Авторский scripts/ni033_case_read_scope_existing_case.py: исходные CASE1031 и личныйQ134. Собственная карточка совпадает с admin, список толькоWARE6667491; чужая403, изменениеWARE9104немедленно403,DELETED401/403,unknownscope422/missing404. Временное собственноеcase_pick_view/WARE/DELETED полностью восстановлены; P20H20/CASE1031NEW0 неизменны. scripts/ni033_case_read_window_case.py: limit1 равен первой строке limit500; итоги целой выбранной волны сохранены. Полная независимая терминальная приёмка остаётся открытой.

Quality gate PASS:530files/0cycles/77debt,24 structuraltests/обаTS; последующее boundedSQL изменение architecturePASS/encodingPASS.

SQL: прежний list агрегировал все CASE истории до лимита:141.885ms (первый cursor). Добавлен выбранный набор≤500 заданий до route/short/event aggregates; wave_totals ограничен их волнами и сохраняет итог всей волны. Новый cold execution256.217ms, последующие два в среднем около4.08ms по накопленному cursor (итого88.126ms/3). Cold parse и промышленный объём не скрываются этим средним. Detail8.431ms/currentactor1.247ms. Новый индекс не создан; owner resources проверяет реальные планы/кардинальность крупных волн и при необходимости read projection/cache. Индустриальная нагрузочная готовность не заявлена.
