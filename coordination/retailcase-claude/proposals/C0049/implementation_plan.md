# Implementation contract C0049/C0056

Разделение по TASK_C0056: Codex — Oracle/backend/auth/API/main/App/api.ts и интеграция; Claude — features, каталог, пользовательские статьи. Состояние: «готово» только после RESULT и review Codex.

## Этапы и точные файлы

| Этап | Что | Файлы | Владелец | Зависит от | Состояние |
|---|---|---|---|---|---|
| 0 | Исправить авторизацию из permission_matrix §6 | `routers/production.py`, `routers/gps.py` (токен устройства), notifications, GET тары/возвратов | Codex | — | предложено |
| 1 | Каталог ролей, организация, матрица | `proposals/C0049/**` | Claude | — | этот RESULT |
| 2 | AccessAdminPage | `admin/wms_admin_frontend/src/features/access-admin/**` | Claude | `/api/access/*` READY | следующий |
| 3 | KnowledgeEditorPage и помощь | `features/knowledge-editor/**`, `features/platform/help/**`, `docs/help/authoring/**` | Claude | `/api/knowledge/*` READY | после 2 |
| 4 | WorkplaceHome + 4 места | `features/workspaces/**` | Claude | существующие API (см. ui_map); `/api/access/me` | после 3 |
| 4i | Подключение в App/меню | `App.tsx`, `main.tsx`, `features/platform/index.ts` | Codex по patch из `proposals/C0056/integration/` | 2–4 | — |
| 5 | Остальные роли, терминал | features + lock на transport/delivery/terminal | Claude/Codex | AK05–AK07 | план |
| 6 | Перевод legacy-групп | mapping §5 permission_matrix, SQL apply/verify/rollback | Codex | утверждение mapping | план |

## Контракты, которые использует UI

- **Access v1 и Knowledge v1** — по `ACCESS_KNOWLEDGE_API_V1.md`. Команды отправляются с `operation_id`, `expected_version` и квитанцией `GET …/commands/{id}`.
- **Неизвестный исход** (сеть/5xx) хранится локально по ключу `apiBase + actor + operation_id`. Повтор — тот же body. Новая команда по объекту блокируется до квитанции.
- **409** — показать сохранённую версию; изменить можно только новой командой.
- **До READY** экраны показывают «API ещё не подключено (ожидается READY от backend)» без мок-данных. Локальный component preview — только в отчёте, не в продукте.

## GAP, требующие backend

Объект «исключение/поручение» руководителя; сетевой агрегат по РЦ; утверждение расхождения пересчёта; узкие права (карантин, политика тары, стадия FINANCE без права ставок); профиль РЦ (часы/пороги); двор и ворота; перевозчики; область STORE/REGION; объектный SoD (автор ≠ проверяющий) в шести командах. Полный список — [generated/gaps.md](generated/gaps.md).

## Критерии готовности блока UI

- Реальный API без моков.
- У каждой новой кнопки tooltip и `help_id`, переход к статье; Escape/focus/mobile.
- Ошибки 401/403/404/409/422/сеть различаются; повтор без дубля; черновик не теряется.
- TypeScript PASS, адресные проверки Playwright, скриншоты desktop/mobile.
- Права пользователей не меняются.
