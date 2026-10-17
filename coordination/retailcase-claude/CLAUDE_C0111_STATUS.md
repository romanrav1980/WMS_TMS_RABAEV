# Claude — статус C0111 (AK06-D, терминал сборки накидыванием)

Обновляет только Claude (сессия C0111, инструменты Read/Edit/Write/Glob/Grep; Bash/сеть/Oracle/git недоступны).

**Статус:** RESULT / RELEASE первого кодового блока (полный UI/hooks поверх замороженного контракта, backend ещё не wired)
**Задача:** AK06-D — цифровой пост сборки накидыванием: товар→человек→сборочная тара на весах, скан товара/количества, подтверждение приростом (AUTO после стабилизации или BUTTON «Положил»), отдельный финальный замер. Контракт: `coordination/retailcase-claude/ASSEMBLY_SCALE_API_V1.md` + `api/wms_api_server/app/modules/inventory/contracts_assembly_scale.py` (backend ещё не смонтирован — `assembly_scale_service()` кидает RuntimeError, роутера `/api/inventory/assembly-scale/*` в коде пока нет; это ожидаемо, native пишет Codex параллельно).

**Что сделано (новые файлы, все в эксклюзивной области):**
- `features/inventory/index.tsx` — публичная граница, экспортирует `AssemblyScaleApp` (root будет `import './features/inventory'`).
- `assembly/contracts.ts` — TS-типы 1:1 с ASSEMBLY_SCALE_API_V1.md (state не status, все числа массы — строки сервера).
- `assembly/api.ts` — Basic-auth fetch к `/api/inventory/assembly-scale/*` (same-origin, без browser-override базы); `rawApiGet` для стороннего пути `warehouse-scales/final-captures` (другой роутер, тот же Basic auth); `outcome_confirmed` засчитывается только при совпадении operation_id/step_id/session_id с ИСХОДНЫМ запросом.
- `assembly/journal.ts` — переиспользуемый helper (≤100 строк) для 3 сохраняемых command-типов (open_session/open_step/finish): точный payload до отправки, scope по server+actor+task_id, повреждённая/чужая запись бросает `JournalDamagedError` и блокирует новую мутацию, а не молча отбрасывается.
- `assembly/commands.ts` — `openSession/openStep/finish` (каждая через journal: отличающееся тело при незавершённом intent отклоняется, а не перезаписывается; очистка intent только после реального успеха), `markPlaced` (без массы/количества/actor в теле, как в контракте), `readSession/readStep`.
- `assembly/usePolling.ts` — ограниченный опрос раз в2с, свой AbortController/disposed-флаг на каждый запуск эффекта (безопасно для StrictMode и позднего ответа).
- `assembly/useAssemblyAuth.ts` — вход через существующий `/api/terminal/auth/me` (Basic), credentials только в памяти.
- `assembly/useAssemblyContext.ts` — `GET /context?task_id=`, валидирует форму и совпадение task_id.
- `assembly/useAssemblySession.ts` — держит сессию/текущий шаг, опрашивает `GET /sessions/{id}` пока OPEN, различает «Восстановление связи» (status0/503 без confirmed) от подтверждённого отказа, `retrySame`/`readBeforeRetry` (сначала читаем, потом разрешаем повтор ТОГО ЖЕ тела).
- `assembly/components/`: `LoginGate`, `TaskPicker` (только номер/прямая ссылка, НЕ сканируется), `PendingSessionRecovery` (нашёл и закрыл реальный дыр-кейс: краш между генерацией session_id и ответом — без этого компонента operator застревал бы без способа прочитать результат, потому что `readBeforeRetry` в основном хуке работает только когда `session` уже существует), `StationSetup` (пост+фактическая тара+скан тары), `NewStepForm` (позиция/количество/сканы/явный чекбокс AUTO без галочки по умолчанию, текст — конкретный артикул+количество), `StepStage` (WAITING_BEFORE/ARMED/READY/APPLIED/DISCREPANCY, «Положил» только BUTTON+ARMED, звук/визуальный успех только на реальном APPLIED и один раз на step_id), `FinishPanel` (читает `GET /api/inventory/warehouse-scales/final-captures?task=` — уточнил актуальный путь по `warehouse_scale_routes.py`, этого route `/tasks/{task}/final-readings` не существует; фильтрует кандидатов по совпадению task_id/scan_container, не придумывает capture_key при пустом списке), `Diagnostics` (device_id/калибровка/версии/сырые времена — свёрнуто), `CommandError` (uncertain/confirmed, кнопки «Прочитать результат»/«Повторить то же самое»/«Скрыть»).
- `assembly/help.ts` — короткие title/data-help-id константы; `NativeHelp` (существующий, platform) подключён с `articleId="assembly-scale"` в шапке рабочего экрана.
- `assembly/styles.css` — только новые классы `asm-*`, 360/390 и desktop; переиспользует `.store-app-*`/`.wms-help-*` из существующего `platform/shared.css` (отдельно не копировал).

**Проверено статически (grep/чтение, Bash недоступен):** все `<button>` имеют `title`+`data-help-id`; `ScanField`/`NativeHelp` подключены только через публичный `features/platform` (без глубокого импорта delivery — проверил grep, совпадений нет); единственный публичный экспорт `features/inventory/index.tsx`; файлы ≤170 строк, функции ≤~55 строк — лимиты 600/100 с запасом.

**Сознательно НЕ реализовано/осталось честно открытым:**
1. Backend не wired — все экраны будут давать честную ошибку чтения до READY Codex; это не демо-обход.
2. `FinalCaptureCandidate` парсится defensively (точная форма `final_readings()` не зафиксирована в контракте) — беру только записи с валидным 64-hex `capture_key`, остальное не угадываю.
3. Нет related-статей переходов внутри `NativeHelp` специфичных для этого экрана — используется общий компонент как есть.
4. Не проверял реальный HTTP/браузер/tsc — нет инструментов в этой сессии.

**Занятые файлы:** весь `terminal/wms_terminal_web/src/features/inventory/**` (новый), `coordination/retailcase-claude/CLAUDE_C0111_STATUS.md`, `CLAUDE_C0111_TO_CODEX.md`. Не трогал `assembly-main.tsx`, `vite.config.ts`, `assembly/index.html`, serverstatic/manifest, `features/platform/**` (только читал/импортировал публичное), `resources/`/`shift/` (кроме уже отданного точечного fix C0110, до перехода на это задание).
**Последний прочитанный ID Codex:** C0110 (CODEX_TO_CLAUDE.md) + прямое поручение владельца о AK06-D.
**Открытые вопросы:** см. CLAUDE_C0111_TO_CODEX.md — точный response-shape `final_readings()`, подтверждение auth-механизма `/api/inventory/assembly-scale/*` (предположил Basic как у соседних роутеров), готовность backend для живой проверки.
