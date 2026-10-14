# NI08.1: прогноз трудозатрат по действующим нормам

2026-10-14, dev RABAEV/orcl. Реализован K-0003; frontend Claude переиспользован, серверная математика не продублирована.

## Функционал
- Явная версия связи warehouse + CASE_DISPATCH/FULLPAL_DISPATCH/OUTBOUND_WORKLOAD → SITE_CODE. Настраивает ответственный с resource_shift_edit, текущим складом и expected_version.
- Существующий RRL_WORKLOAD_CONFIG_API/RRL_WORKLOAD_OPERATION сохраняет решение, hash, автора, версию; append-only RRL_WORKLOAD_SCOPE_SITE и native guard. Retry возвращает прежнюю версию; устаревшая версия и другое содержимое прежнего ID отвергаются.
- Resources владеет нормами; transport получает публичную bounded read model в том же Oracle READ ONLY snapshot, что и история. Один batchJSON_TABLE до500SKU, без N+1.
- Для каждого готового товарного ряда: estimated_quantity/base_per_hour, Decimal80, вверх до9знаков часа. Применяется последняя версия нормы для точных SKU/base_uom и настроенного участка. Неактивная последняя версия не заменяется старой активной.
- Полный итог доступен только при покрытии всех рядов. Неполное покрытие даёт отдельный known_person_hours/partial status, total_person_hours=null. Заблокированный прогноз, отсутствующая связь/норма явно показаны.
- UI раскрывает основание по SKU и версию; отдельная форма связи с участком, сохранённый запрос, повтор после потери ответа, блокировка повреждённого локального запроса и архив.
- Не рассчитывает и не назначает людей без доступных смен/перерывов/квалификации, оборудование и слоты. Остатки/явка/задания не изменяются.

## Реальная проверка
Использованы две собственные завершённые погрузки B01/склад9807:18+18EA. Existing projector перенёс только эти2источника.
Тестовые нормы OWN_B01_FULLPAL: A12EA/ч, B6EA/ч. Это synthetic производительность, не промышленный норматив.
До связи — NO_SCOPE_MAPPING. После сохранения — COMPLETE_ESTIMATE: в снимке1334 прогноз45EA на SKU, часы3.75+7.5=11.25. Включён неполный текущий день: к снимку1340 прогноз44EA и часы3.666666667+7.333333334=11.000000001; изменение ожидаемо, не фиксированный нормативный план.

Реальный ответ сохранения FORECAST.SCOPE:590b4dea-f4a2-476b-a04e-a88b27c6fa3e был потерян на клиенте; после перезагрузки отправлены те же ID/body, ответ совпал, в Oracle одна версия2 для этого ID. Версия1 возникла в предыдущем проходе до исправления повторного входа тестового браузера; не скрыта и не удалена.
Другой payload прежнего ID→409PAYLOAD_CONFLICT. НовыйID/старыйexpected_version→409VERSION_CHANGED.
Три адресных domain-case PASS: дробный partial не выдаётся за полный итог, inactive/blocked не дают часов, точная десятичная арифметика и отключённая связь.

Миграция1328 применена4/0, USER_ERRORS=[], INVALID=[]. Manifest содержит startup-schema и полный актуальный package contract/body; полный runtimebundle не применялся.
Qualitygate735files/0cycles/74debt,24tests+обаTS PASS; предупреждение только pytestcache. JS syntax PASS.
[Скриншот расчёта](screenshots/87-ni081-forecast-hours.png). Evidence:tmp/result1334.json,verify1338.json; scripts/browser1334_forecast.mjs,tests/test_forecast_labour.py.

SQLрешение: metadataDDL545.746мс однократно, неоперационный путь; configscope81.709мс/216buffers холодный, versioninsert31.709мс/635buffers за2. Сохраняем составнойPK/один batchnormread, новыеиндексы не нужны; resources владеет повторным анализом при регулярном>500мс.
Внешний пилот/independent acceptance не подтверждены; полный NI08.1 остаётся открыт для других сценариев ресурсов/слотов.
