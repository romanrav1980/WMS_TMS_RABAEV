# Qwen: общая подача, несколько ячеек и целевой запас

Основание: wiki/database/retailcase_ni032_shared_supply_20261009.md и retailcase_ni032_target_supply_20261009.md. Только существующая RABAEV/orcl, собственные уникальные fixture. Не очищать общий склад. Все quantity effects через RRL_STOCK_POSTING_API.

1. Native create_plan12+8 на одном физическом PAL20: два CASE, одна целая подача20, отдельные владельцы HARD12/8, явный допуск и CASE факты. Второй владелец с другим адресом должен запретить whole movement без изменения P/H.
2. Native два заказа6+6 на PAL10+10, основная face cap5, две dynamic face cap10: existing source groups10+2 распределяются по двум адресам, физические подачи10+10, HARD10+2/free8. Проверить CASE route/content version, demand split и исходные заказы.
3. Own storage HARD12+8 и отдельно пригодный target20: blocked target не используется. Unblock → existing reconciliation → storage P/H20/0, target20/20, физических подач0. Повторить исходные frozen body/ID, подтвердить CASE12+8.
4. Выданная физическая подача не перенаправляется на новый target stock. Чужой заказ/BASE/warehouse/expired/blocked/unit composition mismatch не покрывают потребность.
5. Marked SKU: отдельные физические QR и несколько Track & Trace profiles не умножают P. После замены старые unit bindings освобождены, новые принадлежат тому же PT. Не создавать коды для unmarked SKU.
6. Изменить target stock/version или собственный reserve между prepare/execute: полностью откатить P/H/unit/domain/journal/outbox. Иное тело с прежним ID отклоняется.
7. Parent continuation20+30 не наследует frozen JSON с новым ID. Браузерные действия и unknown-response durable retry проверять отдельно от авторских scripts.

Адресные author scripts: scripts/ni033_native_wave_case.py, scripts/ni032_multiface_case.py, scripts/ni032_target_supply_case.py. Наличие скрипта не означает независимую приёмку. Приложить exact P/H/units/operations, UI факт, SQL decision и собственную cleanup evidence. Зафиксировать ограничения: один target UID и полные storage bindings; не объявлять все спринты завершёнными.
