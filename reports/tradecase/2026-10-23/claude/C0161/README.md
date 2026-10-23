# C-0161 — добивка после начала погрузки основного груза (Claude)

Native-комплект **NOT_APPLIED**. Python, UI и справку включать **только вместе** с apply и restart. До apply старый native save/confirm по-прежнему отказывает `TOPUP_LOADING_ALREADY_STARTED`.

## Основание и найденное (READ ONLY, `src/`)
- Программа rev27, строки 145–159: добивку повторяют до погрузки, после закрытия сборки и при частично погруженном основном грузе. Основные заказы учитываются один раз, задания создаются только для добавляемого товара. При начатой погрузке проверяются доступ к грузу каждой точки и время отправления.
- Было четыре запрета «погрузка началась»: Python allocate и capacity_preview, native TOPUP_API.save и TOPUP_CMD.confirm. `loading_started` смешивал LOADED и DEPARTED.
- Что уже есть:
  - `capacity_context.planned` содержит весь основной план, погруженный и нет, один раз; `_confirmed` вычитает добивку, уже включённую в TRIP;
  - LOAD (`RRL_STOCK_HU_LOAD_CORE`) и DEPART держат ROW `RRL_TRANSPORT_TASK`;
  - факт погрузки хранит GROSS_WEIGHT_KG, BOUNDING_VOLUME_M3, CONTENT_VERSION и состав (узлы STOCK: article/quantity/base_uom).
- Документ TRIP не содержит последовательности точек.
- В БД 5 торговых рейсов с фактами погрузки, все уже DEPARTED.

## Кандидат `db/migrations/2026-10-23_topup_after_load/`
| Объект | Изменение |
|---|---|
| `RRL_TRADE_TOPUP_READ` spec (+3) | функция `departed` |
| `RRL_TRADE_TOPUP_READ` body (+18) | `trip_basis` дополнительно включает машину native task и каждый факт погрузки (op:status:content_version): любой LOAD/UNLOAD/DEPART, смена состава или машины делает расчёт устаревшим. `departed` = факт DEPARTED или применённый TRIP_DEPART |
| `RRL_TRADE_TOPUP_API` body (+3) | save: вместо «погрузка началась» — только `TOPUP_TRIP_DEPARTED`, после точного повтора и текущих прав (порядок прежний) |
| `RRL_TRADE_TOPUP_CMD` body (+8) | `common_plan` берёт ROW `RRL_TRANSPORT_TASK` привязанного native task, ту же блокировку, что LOAD и DEPART: confirm и cancel сериализуются с ними. confirm отказывает только после выезда — под этой блокировкой и до сверки basis с фактами |

Порядок apply: preflight (4 before SHA) → read spec → read body → api → cmd → recompile (только INVALID) → verify (4 after SHA) → ledger. Откат — before-тексты.

## Python (`modules/integrations/infrastructure/`)
- `trade_capacity._loaded`: погруженное считается один раз. План уже содержит этот товар теоретическими коробами; добавляется только подтверждённый излишек каждого места, max(0, факт − теория) по весу и объёму. Более лёгкий факт место не освобождает.
- Отказы с причиной:
  - `TOPUP_TRIP_DEPARTED`;
  - `TOPUP_AFTER_LOAD_VEHICLE_MISMATCH` — факт или native task в другой машине;
  - `…_FACT_MEASURE_REQUIRED`;
  - `…_UNPLANNED_GOODS` — артикул вне плана или погружено больше плана;
  - `…_BASE_UOM_UNSUPPORTED`;
  - `…_FACT_BOUND_200`.
- `after_load_admission`:
  - `TOPUP_DEPARTURE_TIME_PASSED` — по плановому времени TRIP;
  - `TOPUP_AFTER_LOAD_ROUTE_ORDER_UNVERIFIED` — у рейса несколько получателей, а порядка точек в документах нет, поэтому доступ к грузу не доказуем;
  - `TOPUP_AFTER_LOAD_RECIPIENT_NOT_ON_TRIP`.
- capacity_preview: вместо блокировки — расчёт с местами и упаковкой, `floor_places_checked=false`.
- allocate: те же проверки, а также по получателю каждой потребности. Погруженное входит в подпись расчёта.
- Задания создаются только для заказа добивки (существующая передача удержания C0146/C0157); основной груз заново не собирается.

## UI и справка
- `TopupPreview.tsx`, `TopupProposals.tsx`: понятные тексты всех новых кодов; в результате — «Часть основного груза уже в машине: мест N… учтены один раз; +кг/+м³ упаковки; паллетоместа не проверялись».
- Восстановление команды — прежний журнал предложений.
- Справка `tradecase-documents.html#topup.decide`: раздел «Если погрузка уже началась».

## Проверки
| Что | Результат | Тип |
|---|---|---|
| Кандидат `departed`/`trip_basis` на 5 реальных торговых рейсах с фактами | departed=1 у всех; basis отличается от нынешнего (факты вошли) | LIVE READ ONLY анонимный блок |
| Python after-load на тех же рейсах | `TOPUP_TRIP_DEPARTED` (2 рейса) или прежний `TRADE_CAPACITY_PACKAGE_MEASUREMENTS_REQUIRED` (3); места не считаются | LIVE READ ONLY (код этой копии) |
| pytest `test_topup_after_load.py` 12/12 | учёт один раз и только упаковка; пустая или непривязанная погрузка; 7 отказов по фактам; допуск по времени, точкам, получателю; гейты, basis, порядок блокировок, replay до проверки выезда; хэши | offline |
| Прежние тесты topup/capacity/adoption/pool | 49 вместе с новыми — PASS | offline |
| UI `scripts/c0161_ui.cjs` 14/14 при 1440/390 | LIVE: открытие рейса R1.1168; FIXTURE: результат частичной погрузки, 409 нескольких точек, 409 выезда; title и help; нет горизонтального скролла; статическая справка 200 с новым разделом | LIVE + FIXTURE |
| Gate, encoding | PASS | — |

Живые сценарии root после apply и restart:
- LOAD части основного груза, затем расчёт и confirm добивки с учётом один раз;
- UNLOAD или новый LOAD делают сохранённый расчёт устаревшим;
- DEPART блокирует confirm, в том числе параллельно;
- одновременные LOAD/DEPART/CONFIRM;
- точный повтор и конфликт;
- отзыв owner;
- другая машина;
- место без мер.

Подставные ответы UI не являются исходом сервера.

## Ограничения
- **Несколько точек**: после начала погрузки отказ, пока в данных нет последовательности точек. Доступ к грузу каждой точки — решение диспетчера вне системы.
- **Паллетоместа и укладка**: расчёт коробный (BOX_FIXED_ORIENTATION). Факты TOP-мест (`RRL_TT_LOAD_FLOOR_FACT`) и `RRL_STOCK_LOAD_FLOOR` (accessible by закрыт) в допуск не входят, `floor_places_checked=false`. `approval_available` не включался.
- **Упаковка**: излишек считается по разнице факт − теоретические короба одного места. Если товар места не сопоставлен с планом, расчёт отказывает.
- После apply ранее сохранённые неподтверждённые предложения потребуют пересчёта: basis теперь включает факты погрузки и машину.
- Реальные SAP/СКМ не проверялись.

## Ревизия 1 (по ревью Codex до apply)
1. **Переполнение basis.** `trip_basis` больше не дописывает в `acc varchar2(32767)` каждую операцию погрузки. История фактов native task складывается в цепочку SHA-256: `lh:=sha(lh||'|L:'||op||':'||status||':'||content_version)` в порядке LOAD_OPERATION_ID. В `acc` попадает `|T:task:машина:число:lh` — 64 символа на задание, при этом каждый переход LOAD/UNLOAD/DEPART учитывается, ничего не усекается.
   Доказательство (`revision-proofs-live.json`, READ ONLY): 3000 переходов (~186K символов) дают `acc` длиной 90; результат детерминирован; изменение любого статуса меняет basis. Прежняя конкатенация на том же входе даёт ORA-06502.
2. **Время отправления при confirm.** Если погрузка началась, confirm под ROW RRL_TRANSPORT_TASK (после replay runner и текущих прав, после проверки выезда, до сверки basis) читает `planned_departure_at` принятого TRIP: `json_value(... returning timestamp with time zone error on error)`, ISO-8601 со смещением, как при приёме. Прошло — `TOPUP_DEPARTURE_TIME_PASSED`; нет или не читается — `TOPUP_DEPARTURE_TIME_INVALID`. До погрузки поведение прежнее.
   Граница: план на 1 с впереди — допуск (сохранение до выезда); на 1 с позади — `TOPUP_DEPARTURE_TIME_PASSED` (подтверждение после); реальный TRIP с временем вида `…Z` читается.
- Исходные before-хэши не менялись; after-хэши, manifest, verify и тесты обновлены. pytest 13 (43 с прежними topup/capacity/adoption), gate PASS, encoding PASS.
