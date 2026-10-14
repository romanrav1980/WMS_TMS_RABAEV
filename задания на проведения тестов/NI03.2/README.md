# Задания Qwen: NI03.2

09.10.2026. Проверяющий не должен считать авторские PASS независимой приёмкой.

Исходники: [состав и доказательства](../../wiki/database/nicora_ni032_task_recovery_20261009.md), [активный спринт](../../wiki/requirements/nikora_delivery_v55/execution/active/ni03_2.md). Рабочая база — существующая RABAEV/orcl, API — localhost:8088. Данные подключения брать из существующего локального окружения; пароли/Authorization в отчёт не печатать.

1. Сначала сопоставить изменённые handlers/контракты с требованиями NS21, NS26–31, NS38–39. Не объявлять весь спринт завершённым: функциональные пробелы перечислены в wiki.
2. Выполнять только перечисленные ниже адресные случаи, последовательно. Не запускать полную тестовую батарею, load test, seed всего склада, копирование базы или VM snapshot.
3. Создавать собственные QA identifiers; не проводить чужие задания и не менять рабочие карточки SKU. До изменений проверять schema/service. Сохранять все operation_id и ответы.
4. При неопределённом результате повторять точный сохранённый payload/ID. Другой payload с тем же ID должен быть отказом, а не новым движением.
5. После каждого случая вернуть свой запас через INVENTORY_COUNT/CASE_RETURN/RESERVATION_RELEASE. Закрыть свои ресурсы/сессии/незаконченные задания. Историю движения, scan drafts и события не удалять.
6. Отчёт: случай, фактический HTTP/Oracle результат, identifiers, P/H до/после, существенный отказ/повтор, остаточные дефекты. Отдельно отмечать «не запускалось»/«не подтверждено».
7. Посмотреть только относящиеся к случаю SQL через slow-sql/Oracle top SQL, записать одно решение по найденной долгой выборке. Не добавлять индексы без плана/доказательства.

Задания не разрешают менять исходники, применять rollback или публиковать GitHub. Исправления передавать разработчику с точным воспроизведением.

## QW-NI032-01 — частичный факт и потеря ответа

Проверить TASK_COMPLETE: исходное количество3, подтверждение1, новый residual2 без старого ресурса/сессии/техники/времён. Исходное задание DONE отражает только1, доменное пополнение не закрыто до residual. Повтор исходного ID/body не создаёт второго residual или движения. /progress показывает confirmed1/remaining2, после остатка confirmed3/remaining0.

Исходный адресный runner: scripts/ni032_task_cases.py. В UI использовать общий warehouse-task-recovery.js; сохранить подтверждение, прервать ответ, перезагрузить и повторить исходный запрос. Не путать оптимистический UI с фактом базы.

## QW-NI032-02 — роли, квалификация и занятость

Runner --resources. Обычный исполнитель имеет только warehouse_task_execute/view. Назначение чужого оператора без dispatch-права запрещено. Отозванная REPLENISHMENT квалификация запрещает назначение; неподходящий тип, закрытая смена, чужая сессия, неактивная техника также запрещены. После повторного start ровно одно STARTED-событие. Вторая физическая работа оператора не начинается до завершения первой.

Partial освобождает CURRENT_TASK_ID в той же stock transaction. Следующий residual требует нового валидного назначения. Отдельно проверить PUTAWAY: REACHTRUCK/FORKLIFT имеют capability, но без индивидуального допуска проведение запрещено.

## QW-NI032-03 — две системы маркировки, одна штука

Runner --marked. Три физические единицы, каждая содержит CRPT и EGAIS профили. Сохранить scan draft первой единицы, перечитать после reload, подтвердить1. Два профиля дают одну физическую штуку. Остаток2 требует собственного состава. Чужой draft, другой состав с прежним ID, старая stock version или изменившийся profile signature отклоняются без P/H изменений.

Проверить API adapter, а не только прямой PL/SQL: scan_draft_id должен разрешаться на сервере. Государственные ACK и aggregation-only partial этим случаем не проверены.

## QW-NI032-04 — вместимость и точные единицы

Runner --capacity и scripts/ni032_partial_replenishment_case.py. В ячейке занято1, вместимость2, запрос3: подача1, исходная demand3 сохранена. При наличии другого открытого incoming его оставшийся объём вычитается один раз. После частичного факта исходное полное RT.QTY не вычитается повторно.

FULL_PALLET не делить ради вместимости. Нет свободного объёма → WAIT_FREE_CELL. BOX→BASE и объём должны применяться в согласованных единицах, без float. Параллельный arrival не должен превысить вместимость; такой конкурентный случай отдельно согласовать, широкий нагрузочный прогон не назначен.

## QW-NI032-05 — shortage → инвентаризация → подача → CASE

Один адресный runner:
`scripts/ni032_short_case.py --auditor --chunks --case-resource --reachtruck`.

Уже отобрано1/заказ3, shortage2. Повтор сообщения не создаёт второй инцидент; изменённое сообщение с прежним ID даёт409. До подтверждённого пересчёта старый запас не списывается. Pending inventory блокирует источник. Аудитор с правом и квалификацией получает срочное задание. Неполный состав партий и попытка списать ниже чужого HARD отвергаются.

После пересчёта создаётся существующее срочное пополнение priority0, назначенное свободному квалифицированному ричтраку с актуальной позицией. При вместимости1 две подачи по1: после первой CASE факт2, WAIT_REPLENISHMENT и RESTORED_AT=NULL; после второй CASE3/RESUMED. Deadline от первого сообщения не сбрасывается. Подача сама по себе не означает фактическую сборку.

## QW-NI032-06 — передача CASE

Использовать --case-resource. Комплектовщик без CASE_PICK квалификации не может claim. Повтор start не добавляет событие. После первого отобранного товара диспетчер передаёт задание второй активной квалифицированной сессии. ASSIGNED_TO равен второму оператору, UPDATED_BY — диспетчеру; физический carrier, количество и текущая ячейка сохранены. Старый владелец не должен подтверждать следующую строку.

Проверить отказ без подтверждения, wrong carrier, stale content/owner, повтор одного ID с тем же/другим содержимым. Успех сохраняет одно TRANSFERRED событие. Сканы подтверждает диспетчер; независимый полный ТСД сценарий и оборудование ещё не проверены. Нельзя отмечать NS31 полностью принятым.

## QW-NI032-07 — ARM ресурсов и монитор

Открыть resource-management.html без demo=1. После входа таблица содержит данные /api/resources, нет придуманных операторов/процентов/графика. Ошибка API не включает демо автоматически. Refresh перечитывает данные; отсутствие прав не раскрывает список. Демо разрешено только по явному demo=1.

Проверить recovery monitor, inventory queue и replenishment-progress: количества строковые точные, промежуточная подача и остаток заказа различаются; просроченный исходный deadline виден. Авторский браузерный проход не состоялся из-за отсутствия ответа MCP; здесь нужна самостоятельная DOM/console/network проверка.

## QW-NI032-08 — границы приёмки

Составить матрицу «реализовано / GAP / нет evidence» по указанным NS. Общий SOFT пул, generic WAVE HARD без конечного PICK_TASK, complete mini/MAX lifecycle, duty policy, alternate pick face, camera investigation и полный ТСД handoff/независимая приёмка остаются открыты. Проверяющий должен подтвердить этот остаток, а не закрыть его по успешному happy path.

Вывод отчёта: NI03.2 может быть принят только после закрытия функциональных GAP и фактической проверки. SAP обмен, Track & Trace государственная квитанция, промышленная мощность, оборудование и остальные спринты не входят в эти задания.

Добавить к QW-NI032-01: adapter reservation RESULT_UNCERTAIN должен давать503 с outcome_confirmed=false и retry_same_operation_id=true. Проверить, что клиент не создаёт новый operation_id при потере ответа.

Дополнение QW-NI032-01: runner --urgent обязан сохранить original PLANNED_FINISH_AT в residual при PRIORITY=0. У обычного residual даты очищаются. Перед runners остановить loop через scripts/stop-short-recovery.ps1, дождаться завершения записанного PID/time, после cases запустить scripts/start-short-recovery.ps1 -Actor <user>. Не запускать две копии и не прерывать чужой Python процесс.

## Multi-target supply058

Use scripts/ni032_multi_target_supply_case.py (private business warehouse) to inspect one root batch12+8 with target UID11+9: owner1 spans both, owner2 reserves remaining8 on the shared UID; no repeated allocation or stale internal stock version. Verify unchanged P, owner/H relocation, no WH replenishment, release/CASE12+8, exact replay and own cleanup. Add competing orders and marked physical-unit indivisibility independently. Partial target replacement is not declared implemented.

## Partial target059

Inspect ni032_partial_target_supply_case.py: face remaining17 denies whole20 rebind without changing H; remaining27 permits targetH3/sourceH17 and existing whole20 task, then target23/H20/free3 and CASE12+8. Confirm source intent replay and that an open physical task on any owner of source UID/cell prevents rebind. Check remaining SRC reservation/version, no duplicate old reservation entries (array overwrite=true), full multi-target regression. Multiple old bindings, non-whole modes, marked indivisible units and races remain independent tasks.
