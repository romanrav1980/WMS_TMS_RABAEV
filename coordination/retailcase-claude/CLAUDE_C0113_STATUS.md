# Claude — статус C0113 (независимый review CASE work UI)

Обновляет только Claude (сессия C0113, инструменты Read/Edit/Write/Glob/Grep; Bash/сеть/Oracle/git недоступны).

**Статус:** RESULT / RELEASE — независимый review завершён, один реальный конкретный дефект найден и исправлен в рамках эксклюзивной области.
**Роль:** независимый ревьюер/исправляющий УЖЕ НАПИСАННОГО Codex-коллаборатором UI (`case-work/`), не автор. Не переписывал feature целиком, не трогал assembly (ни Oracle/API).

## Метод

Прочитал AGENTS.md, wiki/index.md (ранее в сессии), `wiki/runbooks/retailcase_case_work_terminal.md`, `CASE_RESOURCE_API_V1.md`, `contracts_case_resource.py`, `CASE_WORK_INTERNAL_STATUS.md`. Прочитал весь актуальный исходный код `case-work/` (12 файлов: CaseWorkApp/TaskCard/WorkPanel/JournalPanel/contracts/journal/api/useCaseWork/useCaseActions/reasonText/ReasonNotice/case-work.css) и сверил его построчно с каждым пунктом чек-листа из PROMPT_CLAUDE_C0113_REVIEW.txt, а не только с уже пройденными root-моками.

## Проверено и подтверждено верным (без изменений)

- Basic `/api/terminal/auth/me`, пароль только в памяти (переиспользует `assembly/useAssemblyAuth` и `assembly/components/LoginGate` — общий для терминалов логин, не дублирование).
- Выбор только собственных ACTIVE-сессий по `resource_code` (`<select>` в WorkPanel), без ручного ввода ID.
- `canonical()` — компактный sorted-key JSON ровно по 7 полям контракта (включая `resource_id:null`/`equipment_id:null`); `validCommand` жёстко проверяет именно этот набор ключей. `sha256()` — SHA-256 через `crypto.subtle`, верхний регистр.
- Персист `Intent` (url/body/server/actor/task/hash) ДО POST (`submit()` вызывает `writeJournal` раньше `resolve(...,true)`); ошибка записи журнала блокирует отправку (`catch { publish({blocked:true}); throw }`).
- Единый журнал (`JOURNAL_KEY`) + `navigator.locks` вокруг каждой мутации журнала; при отсутствии Web Locks — явный отказ, не тихий обход. На монтировании — только GET-попытка прочитать квитанцию сохранённого pending (`resolve(...,false)`), POST не отправляется автоматически.
- GET404 трактуется как «неизвестно»: `retry()` сначала делает `resolve(...,false)`, и ТОЛЬКО при статусе 404 делает `resolve(...,true)` тем же самым `Intent` (тот же operation_id/тело) — не создаёт новый.
- `api.ts`: top-level `409 + outcome:"REJECTED"` принимается как квитанция только если тело СТРОГО содержит `outcome==="REJECTED"` на верхнем уровне; «сырой» `409 {detail:...}` без этой формы уходит в общий «контракту не соответствует» путь и НЕ считается отказом. 200 засчитывается только при `outcome==="APPLIED"`.
- `validateAck()` — полная сверка identity+hash (operation_id/action/task_id/actor/request_sha256/outcome_confirmed/stock_posted/changed), для APPLIED дополнительно статус/assigned_to/resource_session_id/resource_id/equipment_id/assignment_version=ожидаемая+changed/aware started_at для START; для REJECTED — changed=false/may_create_corrected_operation=true/непустой error_code. Несовпадение — исходный intent НЕ трогается (`writeJournal` вызывается только после успешной validateAck).
- Идентичность: `resolve()` отказывает, если сохранённый intent принадлежит другому `actor`/`server` — поздний ответ чужого логина/вкладки не применяется.
- Нет поля количества нигде в Command; actor не передаётся из браузера.
- Правильная ссылка legacy-владельца `/wms-admin/case-pick-tsd.html?case_task_id=` (НЕ `/case-pick.html`); честные подписи про отдельный допуск к legacy и к `/assembly/`.
- Каждый `<button>/<a>/<select>/<textarea>` имеет `title`+`data-help-id` (проверено grep по всем файлам `case-work/`); `NativeHelp articleId="case-work"`; импорт `ScanField/NativeHelp` только через публичный `features/platform`.
- Файлы ≤53 строк (кроме `case-work.css`), функции ≤29 строк — лимиты 600/100 с большим запасом.
- Unicode-счётчик причины (`Array.from(reason).length`) соответствует Python `len()` по code points; HTML `maxLength=500` — заведомо более строгий UTF-16-предел поверх этого (как и заявлено в CASE_WORK_INTERNAL_STATUS).
- Путь кросс-навигации `/case-work/?task_id=` сверил с `vite.config.ts` (`caseWork: "./case-work/index.html"`) и фактическим паттерном монтирования `/assembly` в `assembly_scale_composition.py` — ожидаемый путь совпадает со сложившимся соглашением именования (`/case-work`), это не дефект.

## Найденный и исправленный реальный дефект

**JournalPanel.tsx: карточка «подтверждён результат» не проверяла task_id.** Журнал один на устройство (`JOURNAL_KEY` не содержит task_id). После подтверждённого CLAIM/START по заданию №1136 оператор открывает другое задание (№1200, та же учётка) — `result` вычислялся только по совпадению `actor`+`server`, без сравнения `last.intent.task_id` с открытым `task`. Карточка «Действие подтверждено · Задание №1136» показывалась бы поверх актуального №1200, вводя в заблуждение (раздел `pending` уже правильно учитывал это через ссылку «К исходному заданию» — только `last` был не защищён).
Исправление: `result` теперь требует `last.intent.task_id === task`; при несовпадении (но тот же актёр/сервер) — отдельная строка «Есть подтверждённый результат по другому заданию №N» со ссылкой `/case-work/?task_id=N`, тем же паттерном, что уже используется для `pending`. Без non-null assertion — сузил тип через `last && lastOwn && ...` как в остальном файле.

## Не являются дефектами (намеренно задокументировано, не трогал)

- `features/inventory/case-work` импортирует `LoginGate`/`useAssemblyAuth` напрямую из `../assembly/...` (не через публичную границу `features/inventory/index.tsx`). Это переиспользование ВНУТРИ одного зарегистрированного домена `inventory` (assembly и case-work — не отдельные домены в `config/architecture/retailcase-policy.json`), не нарушение policy про междоменные импорты; architecture-gate проверяет именно домены верхнего уровня. Решение разумное (не плодит второй логин-экран), но единая авторизационная зависимость названа в честь другой фичи — чисто номенклатурная шероховатость, не исправлял риска ради косметики так близко к дедлайну и без права трогать assembly.
- Один глобальный `pending` блокирует действия по ЛЮБОМУ заданию, пока не разрешится — подтверждено как осознанный дизайн (один физический оператор = одно незавершённое действие одновременно), а не бага.
- `openTask()` одновременно меняет `task` и вызывает `work.refresh()` — из-за батчинга React 18 эффект выполняется один раз, не двойной запрос; не исправлял отсутствие проблемы.

## Не делал / ограничения

Не запускал `tsc`/gate/браузер (нет Bash в этой сессии) — весь review статический (чтение+grep+сверка с контрактом). Не трогал assembly/Oracle/API/policy/baseline/git/wiki/entry/vite. Не называю этот review независимой приёмкой хода «железо»/реального native — это обзор исходников против контракта.

**Занятые файлы:** `terminal/wms_terminal_web/src/features/inventory/case-work/JournalPanel.tsx` (единственная правка), `coordination/retailcase-claude/CLAUDE_C0113_STATUS.md`, `CLAUDE_C0113_TO_CODEX.md`.
**Последний прочитанный контекст:** PROMPT_CLAUDE_C0113_REVIEW.txt, CASE_WORK_INTERNAL_STATUS.md (все записи до текущей), CASE_RESOURCE_API_V1.md.
