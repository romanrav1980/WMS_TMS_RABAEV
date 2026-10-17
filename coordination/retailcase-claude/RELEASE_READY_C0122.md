# RELEASE_READY C0122 — финальный UI-пакет и recovery-фиксы

READY16.10.2026 21:55MSK. Это второй из двух оставшихся пакетов, не запускать отдельный C0120. Владелец просит работать вместе и завершить до17.10 08:00MSK. Multi-store handover отменён. C0121 получен; root проверил серверный контракт и обнаружил указанный ниже блокер доказательства исхода.

## Сначала исправить блокеры C0121

1. `case-handoff.js::proven`: **текущий исполнитель/ресурс/сессия не доказывают конкретный запрос**. Использовать готовый GET `/api/case-pick/tasks/{task_id}/transfer-receipt?offline_event_id=...`.200 содержит `{case_pick_task_id,status:"TRANSFERRED",offline_event_id,actor,outcome_confirmed:true,source:"IMMUTABLE_TRANSFERRED_EVENT",request:{...исходное тело без actor...}}`. Сверить task/id/current actor/source/confirmed и все значимые поля сохранённого тела (nullable omitted эквивалентны null только для nullable DTO полей). Другой ID, другое тело или совпадение карточки без квитанции не дают успех.403/404/503 — исход не подтверждён;404 содержит outcome_confirmed:false, **не означает «никогда не выполнится»**.
2. После прежнего unknown не удалять intent и при400/422. Явный архив браузера **не отменяет поздний серверный запрос**. Пока исход не доказан, сохранить блокировку нового intent; можно сохранить копию для разбора, но не снимать pending и не обещать отмену/разблокировку. Повреждённый журнал также не разблокировать простым архивом. Для снятия неизвестности доступны неизменный повтор и серверная квитанция; отсутствие квитанции — не подтверждение отмены. Исправить подписи/справку. Серверного ABANDON для TRANSFER нет, не изображать его существующим.
3. Мобильная CASE-страница целиком должна работать на390px: убрать локально влияние body min-width1280, устранить наложение кнопки повторения short-decisions на заголовок. Глобальный styles.css не перестраивать; вынести локальный override/компоновку. Не ограничиваться скриншотом dialog.

## Готовые серверные изменения

- CASE TRANSFER native WARE/GROUP + физический handoff,11HTTP/24EA/rollback/REV PASS; новый сотрудник завершил25EA и груз отправлен/принят. История сохраняется.
- Whole HU `/api/transport/loading/confirm`, `/api/warehouse-hus/ship` и `/api/transport/loading/{trip}/depart` больше не требуют плоское право в HTTP: native проверяет текущие области. Whole HU/CASE→BOX→PALLET25EA,37HTTP WARE/GROUP/revoke/replay/rollback/REV→магазин FULL PASS. Native для DEPART требует все ST/load/dock WARE. Не делать partial multi-store.
- Admin `/api/admin/auth/login` и `/me`: legacy PRAVO_ADMIN_LOGIN/global сохранён; **новое назначение wms_admin_login по PLATFORM** тоже открывает shell, не превращая остальные scoped permissions в плоские. Проверено живым пользователем с PRAVO_ADMIN_LOGIN0: permissions ответа содержит только wms_admin_login. Операционные права продолжает решать native.
- `/api/access/workspaces`: `{username,access_revision,warehouses:[{warehouse_id,title,capabilities:{picking,dispatch,waves,warehouse_tasks,resource_timeline,resource_registry,resource_sessions}}],has_more,limit,navigation_only:true}`. Это готовые native READ capabilities для навигации. Не выводить доступ к комплектации из любого ACTIVE назначения (например, одного shell login). Серверная карточка CASE и команды проверяются отдельно.
- Финансы: BOX/monthly rates scoped create_tt_price; XLSX требует все WARE в том же READ ONLY snapshot,20HTTP native matrix PASS. UI финансов заново не делать. KPI API/UI рабочие observed, неполнота источников явно маркирована, спорные правила не объявлять согласованными.

## Работа во втором пакете

Исправить recovery выше, nav «Комплектация» по готовым picking capabilities с текущим складом (не добавлять scoped операционные права в общий auth.permissions). Проверить raw loading UI: сервер уже допускает scoped whole-HU/DEPART; оставшиеся плоские UI gates не должны скрывать эти готовые действия от роли в своей области. Учитывать запрет чужого склада и очистку прежних данных. Затем ограниченный сквозной прогон существующих смена→волна→ресурсы/Гант→консолидация/погрузка→магазин→KPI; сохранять контекст/возврат,4семейства ресурсов, help URL и390px. Готовые React Гант/KPI не переписывать. Если для конкретного семейства нет живых ресурсов, отметить fixture отдельно.

## Безопасные живые данные

`reports/retailcase/2026-10-16/case-transfer-scope/receipt-acceptance.json` — актуальный manager actor `MT16M926cdde30a`, CASE1151, WARE20902283. У него current case view/manage GROUP + отдельное PLATFORM login, обычная legacy группа не даёт view/manage/login. Password читать локально из Oracle/RUSERS штатным механизмом, не писать в файлы/отчёты. Live GET login/case/receipt/workspaces подтверждены8HTTP. Фактическое задание уже отгружено, **новые бизнес-POST не выполнять**. Позитивные UI-команды только fixture с явной пометкой; реальные root mutation cases подтверждены отдельными отчётами. Не менять grant/fixture metadata: root владеет retirement после UI проверки.

## Ownership / результат

Один ACK с точными файлами. Разрешены C0121 CASE JS/HTML/CSS/help, `admin-nav.js` и его ограниченный helper для native navigation, необходимые существующие loading JS/helpers/help. Backend/Oracle, architecture policy/baseline, tests root и финансовые источники не менять. Не публиковать GitHub/статьи через API, не запускать субагентов. Проверить синтаксис/encoding и изменённые UI сценарии, особенно: wrong receipt with matching current assignment остаётся unknown; valid immutable exact receipt resolves; unknown→400/403/404/409/422 остаётся pending; копирование/архив не создают возможность нового запроса;390px вся CASE-страница; scoped login→nav→CASE; read failure очищает старые строки.

Итог одним RESULT_C0122.md/RELEASE: исправления, реальные проверки против fixture, оставшиеся блокеры с file:line. Самопроверка своих фиксов не называется независимой бизнес-приёмкой. Если подтвердится серверный блокер — описать воспроизведение для root, закончить независимые UI части. После RELEASE новых запросов не ждать: root выполнит финальную интеграцию и общий gate.
