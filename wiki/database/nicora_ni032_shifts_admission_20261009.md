# NI03.2: смены, расследование и допуск пополнения
09.10.2026. RABAEV/orcl. Дополнения025–030 APPLIED. NI03.2 ещё не закрыт.

## Реализованное поведение
025: generic consumer binding хранит signature полного ограниченного списка потребителей; повторно проверяет его под anchors после переноса. Изменение очереди/потребности отклоняет всю транзакцию.
026: существующие RESOURCE_SHIFT дополнены BASE_SHIFT_ID, REACH_SHIFT_ROLE, EXPECTED_DRIVERS. Из базовой смены создаются MAIN (начало/конец на2 часа раньше) и DUTY (та же базовая смена,1–2 водителя). Повтор создания идемпотентен. Login блокирует превышение численности; logout требует закончить текущий физический шаг или оформить допустимую передачу. Повторно используются прежние unique active-session индексы.
027: уже начатый в своей открытой смене шаг разрешено подтвердить после окончания времени смены. Новое задание/новый остаточный шаг за пределами окна не начинается. Квалификация, ресурс, состав и запас проверяются прежним ядром. ТСД принимает явный shift_id при пересечении MAIN/DUTY.
028: SHORT имеет отдельную версию/статус расследования. CCTV_VIEWPOINT задаёт HTTP(S) шаблон видеоархива, смещение времени и окно. Existing warehouse map CAMERA — физическая камера хранения, поэтому не использована как видеокамера. Запись вывода версионная, immutable event ID/replay; никаких quantity-effects или автоматического разрешения недостачи. Доступ к реальному NVR не подтверждён.
029: существующий ABC_GROUP определяет категорию. В обычной волне B + занятой отбор + разрешённый partial mode заполняет свободную ёмкость до меньшего из неё и доступного источника, без ограничения величиной спроса. Другие категории не получают правило B. Мини-макс и срочный SHORT сохраняют свои quantity contracts. FULL_PALLET может быть меньше потребности, но целая паллета с чужим HARD не выбирается; финальное исполнение также отказывает при появлении другого резерва.
ALLOW_PICK_BATCH_MIX добавлен в существующий RECEIPT_SKU_RULE: default0, включается в карточке склада/SKU. Смешение другого SKU запрещено всегда; разных партий одного SKU разрешено только в отборе с явным флагом. Идентичность партии: MES batch, SAP supplier batch через STOCK_ORIGIN_UID; для неполного legacy — консервативная идентичность документа/исходной паллеты плюс срок/дата производства. Проверка на планировании и повторно перед физическим переносом под CELL X.
030: generic пополнение при окончании меньшей исходной паллеты сохраняет remaining demand отдельной строкой прежнего REPLENISH_TASK. PARENT_REPLENISH_TASK_ID + unique index исключают двух детей одного шага. Новый row ID/unique anchor заранее входят в closure. История исходной строки/факта остаётся. ROOT создаёт continuation в той же транзакции; qty-effect следующей подачи — отдельная явная root команда. Мини-макс/SHORT используют свои циклы, не получают второй continuation.

## Адресное dev-подтверждение
- reach_shift_case: MAIN/DUTY offset/replay/count conflict, capacity1, запрет выхода при назначенном задании, затем выход.
- investigation_case: собственный SHORT16, archive URL с явным+03:00, версия/replay/конфликт/устаревшая версия; P/H неизменны. Тестовая ссылка nvr.invalid отключена после случая, внешнего HTTP не было.
- partial_replenishment_case: отдельный SKU B, target40/capacity100/demand20/source80 → delivery60/source20. Иная партия отклонена по умолчанию, разрешена только флагом отбора.
- whole_surplus_case: source100/demand50 → целая delivery100, без ошибочного child.
- whole_replenishment_case: source20/demand50 → delivery20 + один child30; нет запаса → нет фиктивного задания; позднее source30 → итогP50/H0, replay без дубля.
Stock собственных fixtures очищен через root count/release, журналы сохранены.

## Фоновое исполнение и SQL
Minimax worker запущен Hidden для warehouse1/actoradmin, PID26652 (identity в runtime/minimax_worker/worker.json, проверять start time). Цикл теперь включает generic continuation; реальные записи stdout20:28–20:29 MSK: OK, continued0, faces0. Это подтверждение idle worker, не приёмка промышленной мощности.
Oracle top SQL после changed cases:2mgfy8y302xw9 source admission45.71ms avg/3 executions;3cmc7v0mfwkdp continuation readiness68.52ms/1 execution; parent lookup1.92ms. Решение owner inventory: оставить ограниченную очередь200 и target lots200, прежние ключи; correlated readiness/FEFO проверять и переработать при steady>500ms. Массовая нагрузка и speculative индексы не запускались.

## Остаток
Альтернативный разрешённый pick-face/slot, real post-shift quantity case, full marking/secured-demand overlap и независимая приёмка. PLANNED derived shifts требуют штатного открытия, реальный NVR/SAP/regulatory ACK остаётся внешним допуском.
Источники: migrations2026-10-09_ni032_binding_snapshot/reach_shifts/finish_started_step/short_investigation/replenishment_admission/replenishment_continuation; inventory/infrastructure/replenishment_continuation.py; scripts/minimax_worker.py.
