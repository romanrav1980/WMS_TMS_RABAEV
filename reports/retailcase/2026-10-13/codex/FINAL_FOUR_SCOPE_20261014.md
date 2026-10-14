# Конечная сверка NI02.2 / NI06.3 / NI07.1 / NI08.1

14 октября 2026. Ведомый Codex → ведущему. Сопоставлены актуальные исходники, активные карточки и сохранённые сценарии NS15/17/24/33/55/56/57/59/60, отчёты Claude C0015/C0018/C0020/K0015 и root47/54/57/61. Новых тестов, Oracle-операций, миграций и массового аудита в этой сверке нет.

**Вывод: три спринта не требуют повторной разработки перечисленных функций; NI08.1 имеет конкретный кодовый остаток общего расписания с перерывами и финального допуска.** Последние UI-отчёты не используются как доказательство полного выполнения всех бизнес-правил.

| Спринт | Готовые обязательные функции | Подтверждённый кодовый остаток | Отдельные условия приёмки |
|---|---|---|---|
| NI02.2 (NS15/17/24) | Calendar OPEN/CLOSED, возраст нового адреса, неизменяемый SAP-source/late hold, ACCEPT/REJECT с original demand; поздний ST в существующий незавершённый рейс; общая проверка массы/тары/температуры; тип паллеты адресата с физическим override; времена/ворота и ожидаемый фреш без создания физического запаса; C0018/C0021 страницы/серверные фильтры/compound row key. | По указанным функциональным критериям отсутствующая функция не обнаружена. NI08.1-R1 ниже — общая граница полной временной выполнимости, не новая система назначения. | Реальные SAP decisions/ACK, коммерческие нормативы машин/температуры/адресов, независимая полная приёмка. Отдельный технический критерий: broad historical GET <2с ещё не подтверждён — report53 3.911с, C0018 0.358–0.526с относится к ограниченному периоду и не доказывает всю историю. |
| NI06.3 (NS15/55) | Баланс по владельцу/держателю/типу/состоянию, OFFER/ACCEPT, долг/срок SAME_DAY, вложенная тара без умножения мест; DAMAGE→возврат→независимый WRITE_OFF; LOSS_REPORT→REJECT или WRITE_OFF; recovery/replay и React→raw переход. | Обязательный отсутствующий код не найден. **LOSS WRITE_OFF существует**, отсутствие нового C0020 прогона WRITE_OFF не является отсутствием ветки. | Физическая передача/сканер, независимая полная сверка держателей и оборудования. Новые повторные прогоны не назначены. |
| NI07.1 (NS56/57) | Складские BOX/CASE затраты по фактическому load/trip/дате; месячная общая работа внутри версии ставки; transport norm source/recognition/округление; неизменяемые исходники и once-only claims/outbox; допрасходы TRIP/WARE/VEHICLE, LOGIST+FINANCE, распределение с сохранением копеек, подписанная коррекция и exact поиск; invoice basis/раздельные валюты. | По перечисленным обязательным критериям отсутствующий код не найден. MultiWARE внутри одного TT не нужно добавлять: native один склад на выезд; разные склады агрегируются между рейсами счёта (уточнение615–616). Mixed-date partition уже реализован; отсутствие нового многодневного физического прогона не означает отсутствие алгоритма. | Реальный финансовый SAP mapping/ACK и коммерческие ставки/договоры; независимая денежная приёмка. Declared monthly box base явно не автоматический фактический объём. |
| NI08.1 (NS33/59/60) | История исполненных источников/прогноз без повторного спроса; explicit site norms/Decimal hours; плановые интервалы/merged person capacity/дефициты/перенос wave/выход сотрудника; scoped norms/attendance; диапазоны recommendation→proposal→approve→DRAINING→close; текущий road provider/depot/windows/driver-day diagnostics; existing OR-Tools и shared native capacity/atomic apply. | **NI08.1-R1: перерывы существующей проектной политики ещё не включены в расписание остановок; read-only coordination не является общим финальным временным валидатором manual/auto.** Точные callsites и границы ниже. | Геопривязка настоящего депо/адресов, реальные окна/нормы и полнота предшествующей занятости водителя; независимая приёмка. Юридический режим не придумывать; использовать явно заданную проектную политику. |

## Основания, исключающие повторную разработку

### NI02.2

- Calendar264, source scope265–266, ERP267, multipleST270 и planned source layout278 описаны в active/ni02_2.md и подтверждены существующими API/native owners. Позднее добавлены recipient floor/type, vehicle temperature/floor variants, physical TOP/CASE/STOCK типизация. Раннее «next physical TOP» в странице1190 историческое, не текущая задача.
- `transport/api/vehicle_profile_routes.py` принимает floor_variants; native `RRL_TRANSPORT_PLAN_RULES.check_vehicle` вызывает `RRL_VEHICLE_PROFILE_API.check_floor_capacity`. `transport/infrastructure/loading_floor_read.py`/loading_status.py читают фактические типы.
- `admin/.../features/transport/useAvailableStPages.ts`: page_size200, AbortController/serial, очистка при смене запроса, JSON key [ST_NUMBER,ADDR,WARE_ID]. C0018 + C0021 подтверждают использование в существующем диспетчере. `available_sts_page.py` и RRL_ST_PAGE_KEYS_I уже внедрены report53.
- Нужна отдельная запись о производительности всей истории; не удалять её из-за быстрого обычного scoped запроса. Owner transport; решение report53 — ограниченный операторский запрос/существующий индекс, при возвращении к broad SLA уточнение статистики/плана. Нового измерения здесь нет.

### NI06.3

- [C0015](../claude/C0015/report.md): фактическая цепочка DAMAGE→магазин/водитель/склад→независимое списание; один результат/баланс/outbox, товарных событий0.
- [C0020](../claude/C0020/report.md): LOSS_REPORT и REJECT с потерянным ответом/точным повтором. Он честно не проводил новый WRITE_OFF; это граница его проверки.
- WRITE_OFF присутствует в `tare-loss.html` option, `tare-loss.js` decide(), `inventory/api/tare_loss_routes.py` Literal[WRITE_OFF,REJECT], `db/migrations/2026-10-10_ni063_holder_loss/002_command.sql`: независимое решение и QUANTITY − v_qty для WRITE_OFF. Wiki holder_loss106 содержит более раннее фактическое списание магазина и уменьшение исходного долга. Не создавать второй loss engine.
- Старый C0020 CONTRACT_REQUEST о raw URL уже закрыт root61: TareLossCase.tsx импортирует RAW_ADMIN_BASE из src/api.ts; default API_BASE+/wms-admin. Не держать это блокером.

### NI07.1

- `finance/infrastructure/cost_period_lines.py` группирует box_assembly_clocks по business_date, выбирает соответствующую версию ставки и Decimal cost_amount. `period_policy.py` хранит явный режим/зону. Старая wiki revision_summary со словами «multi-date пока отказ» дополнена более поздним cost_periods512–522.
- `transport_cost_preview.py`, transport_cost_facts.py/read.py и normative_correction.py сохраняют первоначальную сумму и утверждённую коррекцию. Transport recognition582–616: одна claim на выезд, тот же preview/conduct, существующий invoice scope между складами; normative correction598–611 уже применена.
- K0015: реальный дополнительный расход12.34→двухфазное согласование→6.17+6.17→коррекция−2.10→итог10.24; preserved history/outbox, stock_changed=false. `expense_register_read.py` имеет latest100 и exact operation_id за окном, обе ветки scoped warehouse. `Billing*` использует готовые read models, не второй расчёт на UI.

### NI08.1 / NS59 явно выполнен

- `inventory/domain/slotting_demand.py`: firm+forecast−consumed, затем вычет old_credit/inbound и округление вверх до целой паллеты; zero_unobserved_demand_assumed=False. Это закрывает NS59-TC01/02/03 без создания нового спроса.
- `slotting_demand_reader.py`/slotting_candidates.py: тот же snapshot, допустимые пустые published faces, явные затраты/геометрия, optional candidate_pick_route_id. Scoped candidates160 уже реализованы; ранний backlog156 не переносить автоматически.
- `inventory/api/range_proposal_routes.py`: draft, approve и actions/close-drain. `range_apply.py` → existing RRL_PICK_RANGE_APPLY_CORE; `slotting-demand.js` содержит соответствующие действия.
- Native range_apply002_policy/006_core: ACTIVE/DRAINING/CLOSED, новый refill старого диапазона запрещён, исходные активные задания сохраняются; close только при P/H0 и отсутствии незавершённой работы. Старый range не превращается в карантин. Это не «NS59 ещё не разработан».
- Root47/54/57/61 закрывают нормированные часы, interval workload, site/time scope, рекомендацию интервала и durable workload/wave-time intents. NS33 не начинать заново.

## NI08.1-R1 — конкретная отсутствующая связка

1. `transport/domain/driver_rest.py` уже задаёт проектную политику CONTINUOUS_MIN120, BREAK_MIN15, TRIP_DRIVE_MIN540; `driver_day.py` учитывает непрерывность между рейсами. Это готовое authoritative правило, а не повод придумать закон.
2. `transport/domain/delivery_windows.py::estimate_windows` сейчас считает только DRIVE→WAIT→UNLOAD и возврат. В ответе явно `driver_breaks_included=False`, `EARLIEST_DRIVE_WAIT_UNLOAD_WITHOUT_DRIVER_BREAKS`. Ожидание и разгрузку нельзя автоматически признать отдыхом.
3. `transport/infrastructure/coordination_preflight.py` объединяет окна, занятость, driver-rest/day и готовность в read-only snapshot; ответ всегда `operational_admission=False`, `departure_authorized=False`. Это диагностика, не финальная авторизация.
4. Точные write callsites: `plan_application.apply_existing_plan` → `RRL_TRANSPORT_PLAN_API.apply_plan`; ручное `st_assignment.assign_sts` → `assign_validated_sts` → того же пакета.assign_sts. Общая текущая проверка — `RRL_TRANSPORT_PLAN_RULES.check_vehicle`; полное расписание с перерывами туда не подключено. Отдельный общий шаг утверждения времени существующего TT: `trip_time_approval.approve_time` → `RRL_TT_TIME_API.approve`.
5. Конечный критерий до закрытия: одно расписание остановок с явными REST и existing policy; одинаковая проверка актуального источника/дороги/окон для materialized manual и solver TT при финальном утверждении. Перерывы должны сдвигать следующие ETA/разгрузку/возврат и выявлять нарушение окна. Устаревшее основание и неизвестный маршрут не превращаются в разрешение.
6. Нельзя просто добавить Python check перед native write: это оставит race. Финальная связь требует согласованного native proof/fence/current source recheck в прежнем порядке блокировок. Это отдельный контракт с ведущим, не новая таблица/solver автоматически.

Ведущий поручил взять R1 после согласования точного native контракта. Этот файл фиксирует состояние **до реализации R1**; NI08.1 не объявлен code-complete. Остальные перечисленные спринты предлагается перевести из общей формулировки «доделать функционал» в «реализованный код / внешняя и независимая приёмка отдельно», сохранив явный performance-критерий NI02.2.