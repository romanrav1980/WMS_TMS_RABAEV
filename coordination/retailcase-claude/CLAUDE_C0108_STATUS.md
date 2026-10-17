# Claude — статус C0108 (AK06-E)

Обновляет только Claude (отдельная сессия C0108, инструменты Read/Edit/Write/Glob/Grep; Bash/сеть/Oracle/git недоступны).

**Статус:** RESULT / RELEASE третьего блока (C-0110: структурный фильтр wave_id вместо текстового поиска по wave_code)
**Задача:** AK06-E — UX старшего смены и общего ресурсного Ганта (ричтраки/комплектовщики/ворота/машины) по текущим реальным API, без фейковой готовности/demo-данных. Источник: GET /api/resources/timeline (useResourceTimeline), /api/picking/waves, /api/picking/shift-overview, /api/case-pick/* (useShiftData).

**Аудит перед правками (конкретные находки):**
1. Существующий код (resources/, shift/) уже дисциплинирован: нет выдуманной готовности, у каждой кнопки title+data-help-id (проверено grep по `<button` — все совпадения уже содержат title/data-help-id; HelpButton сам добавляет их). Второй timeline engine отсутствует — ResourceGantt/ResourcePlanner переиспользуются и в shift/, и в receiving/storage/Twin.
2. Конкретный пробел навигации (сама задача "волна↔её ресурсы↔текущие задания↔детали"):
   - WaveCard не показывал текущие задания сборки ЭТОЙ волны (только агрегированные риски) — нет перехода "волна → её сборка".
   - Не было перехода "волна → её ресурсы в общем Ганте ниже" — пользователь не знал, что строку поиска Ганта можно заполнить кодом волны вручную.
   - В карточке работы общего Ганта (ResourceCard, событие) поле "Волна" было нажимаемым текстом без перехода назад к карточке волны (в отличие от "Задание"/"Рейс", у которых есть реальный экран-владелец через event.link).
   - Переход "задание сборки → Гант" (кнопка «В Ганте») не скроллил к секции Ганта — на мобильном (360/390px) секция далеко внизу, нет визуальной обратной связи.
3. Отдельно замечен пробел ВНЕ зоны правок: ResourceList (`workspaces/OpsParts.tsx`, общий файл, не resources/ и не shift/) не даёт перейти от сессии человека/техники к Ганту. Не правил — файл вне эксклюзивной области; сообщаю root в CLAUDE_C0108_TO_CODEX.md.

**Сделанные правки (в пределах resources/ и shift/, обратимо-совместимые опциональные props, без второго Ганта):**
- `resources/ganttHelp.ts` — новая запись `openWave` (help для возврата к волне из карточки работы).
- `resources/ResourceCard.tsx` — опциональный проп `onOpenWave?: (id:number)=>void`; при наличии поле "Волна" в карточке работы становится кнопкой (возврат к контексту).
- `resources/ResourceGantt.tsx` — опциональный проп `focusQuery?: {value:string; token:number}`; внешний запуск подставляет текст в существующий поиск (не меняет фильтр типов/данные, не считает это новым расчётом).
- `resources/ResourcePlanner.tsx` (включая экспорт `PlannerBody`) — проброс `onOpenWave`/`focusQuery` без изменения обязательных параметров (другие вызывающие — receiving/storage/Twin/mock-preview — не затронуты, проверено grep всех использований).
- `shift/help.ts` — новая запись `waveGantt`.
- `shift/WaveCard.tsx` — новые проп `tasks: CaseTask[]`, `onShowInGantt`, `onOpenTask`; показывает текущие задания сборки этой волны и кнопку «Ресурсы волны в Ганте».
- `shift/ShiftSupervisorDesk.tsx` — состояние `waveFocus`, `ganttRef`+`scrollIntoView`, обработчики `jumpToGantt`/`showWaveInGantt`; волна фильтрует свои CASE-задания из уже прочитанных `data.caseTasks` (без нового запроса); кнопка «В Ганте» из любого списка теперь прокручивает к секции Ганта.

**Второй блок (после C-0109):**
- `resources/timelineTypes.ts` + `timelineAdapter.ts` — `last_signal.session_id` сохраняется как есть из ответа API (числовой session_id из resource_session_view), не только в составе готовой строки для показа; это и есть настоящий, не придуманный ключ.
- `resources/ResourcePlanner.tsx` — новый опциональный `onTimeline` отдаёт вызывающему месту уже прочитанный (не второй запрос) ResourceTimeline.
- `workspaces/help.ts` — новая запись `openResourceGantt`.
- `workspaces/OpsParts.tsx` (точечно, только `ResourceList` — владение разрешено root в C-0109) — опциональные `resourceKeyBySession`/`onOpenResource`; кнопка «В Ганте» у сессии появляется только когда для её `session_id` есть реальное совпадение в карте, иначе ничего не показываем (без fake readiness).
- `shift/ShiftSupervisorDesk.tsx` — хранит прочитанный timeline, строит `session_id → resource_key` только по факту совпадения, передаёт в ResourceList через PanelList.
- Самопроверка первого блока (статически, без браузера): переход «работа в Ганте → назад к волне» (`onOpenWave`) не прокручивал к карточке волны, в отличие от прямого перехода «волна → Гант» — несогласованность в собственном UX. Добавил `waveCardRef`/`scrollToWaveCard` и `backToWave`, теперь оба перехода симметрично прокручивают к своей цели.

**Третий блок (C-0110, реальная ошибка найденная root):** `showWaveInGantt` подставлял `wave.wave_code` в текстовый `filters.query`, а `matches()`/hay в timelineModel.ts никогда не содержал wave_code (только wave_id/event_id/title/код ресурса) — для CASE-событий, у которых title не включает код волны, подстановка не находила ни одного ресурса/бара, при этом молча выглядела как «пустая выборка», а не как ошибка. Заменил на структурный числовой фильтр:
- `timelineModel.ts`: `Filters` получил `waveId: number | null; waveLabel: string | null`; `groupRows` отдельно (независимо от текстового `query`) требует `hasWave(r.bars, f.waveId)` — точное совпадение `event.wave_id`, не substring.
- `ResourceGantt.tsx`: проп переименован `focusQuery` → `waveFocus: {waveId, label, token}`; применяется в `filters.waveId/waveLabel`, не трогая `query`. Видимый активный фильтр — чип «Волна <label>» в тулбаре с отдельной кнопкой очистки (`ganttHelp.waveFilter`/`waveFilterClear`), независимой от текстового поиска. Бары внутри строки ресурса фильтруются тем же точным `wave_id` (ряд остаётся, если хотя бы один бар совпал); состояние «сейчас» слева считается по ПОЛНОМУ списку баров ресурса, а не по отфильтрованным — иначе занятый другой волной ресурс мог бы ложно показаться свободным. Очередь «без времени/ресурса» также фильтруется тем же `wave_id`, когда фильтр активен. Пустая группа при активном фильтре показывает именно «у этой волны нет видимых ресурсов/работ», не общий «по фильтру ресурсов нет».
- `ResourcePlanner.tsx`/`PlannerBody` и `ShiftSupervisorDesk.tsx`: переименованы соответственно (`waveFocus` с `{waveId, label, token}`), `showWaveInGantt` теперь передаёт `w.pick_wave_id` (число) + `w.wave_code` только как отображаемую метку чипа, не как ключ фильтра.
- Проверил grep — ни одного оставшегося `focusQuery` в репозитории, ни одного другого места, создающего `Filters` литерал (кроме обновлённого).

**Не делал:** не трогал backend/Oracle/API, не трогал IsoStageScene.tsx/ops.css целиком (только функцию ResourceList в OpsParts.tsx, по разрешению C-0109), не вводил второй UI/второй расчёт занятости/второй timeline engine, не называл свои статические проверки независимой приёмкой.

**Проверка:** только читал код и статически сверял сигнатуры/импорты/единственность вызывающих компонентов (grep по WaveCard/ResourcePlanner/ResourceGantt/ResourceCard/PlannerBody) — Bash/TypeScript/браузер недоступны в этой сессии, поэтому typecheck и live-проверка НЕ выполнены мной. Прошу root прогнать `tsc`/`retailcase_quality_gate.py` и реальный `/?page=workspace` на desktop+390px после этого RELEASE.

**Занятые файлы:**
admin/wms_admin_frontend/src/features/platform/workspaces/resources/ganttHelp.ts,
admin/wms_admin_frontend/src/features/platform/workspaces/resources/ResourceCard.tsx,
admin/wms_admin_frontend/src/features/platform/workspaces/resources/ResourceGantt.tsx,
admin/wms_admin_frontend/src/features/platform/workspaces/resources/ResourcePlanner.tsx,
admin/wms_admin_frontend/src/features/platform/workspaces/resources/timelineTypes.ts,
admin/wms_admin_frontend/src/features/platform/workspaces/resources/timelineAdapter.ts,
admin/wms_admin_frontend/src/features/platform/workspaces/resources/timelineModel.ts,
admin/wms_admin_frontend/src/features/platform/workspaces/shift/help.ts,
admin/wms_admin_frontend/src/features/platform/workspaces/shift/WaveCard.tsx,
admin/wms_admin_frontend/src/features/platform/workspaces/shift/ShiftSupervisorDesk.tsx,
admin/wms_admin_frontend/src/features/platform/workspaces/help.ts (точечно: новая запись help),
admin/wms_admin_frontend/src/features/platform/workspaces/OpsParts.tsx (точечно: только функция ResourceList, по разрешению C-0109),
coordination/retailcase-claude/CLAUDE_C0108_STATUS.md,
coordination/retailcase-claude/CLAUDE_C0108_TO_CODEX.md.

**Последний прочитанный ID Codex:** C-0110 (CODEX_TO_CLAUDE.md).
**Открытые вопросы Codex:** см. CLAUDE_C0108_TO_CODEX.md — прошу typecheck/gate/live проверку конкретно нового структурного фильтра (выбор волны → непустой набор ресурсов/баров при реальных bindings, очистка фильтра восстанавливает полный список); жду отдельного сообщения root перед тем как браться за AK07 controls UI или за терминал сборки накидыванием.
