# RESULT C-0162 — права общего пула, включая повтор (Claude). Checkpoint `beca12db`, native NOT_APPLIED

Native-комплект **NOT_APPLIED**. Живые HTTP/Oracle-сценарии и приёмку выполняет root. Весь T08 не объявляется завершённым; `approval_available` не включался.

## Границы read / execute / replay
| Этап | Что проверяется | Где |
|---|---|---|
| **Preview (чтение)** | текущее право `stock_reservation_view` на **этот склад** (`RRL_ACCESS_API.allowed`: GLOBAL_ADMIN, legacy-группа своего склада, действующее назначение) — иначе 403 `POOL_WAREHOUSE_ACCESS_DENIED`. Для торговой площадки видны только строки, у которых пользователь видит собственника источника или получателя (как в расчёте вместимости), и классы видимых собственников; `complete=false`, `available_quantity=null`, если что-то скрыто | `PoolService.preview` (Python), одна READ ONLY транзакция |
| **План** | считается по **полному** снимку, одинаковому для всех читателей (C0160): пользователь видит разрешённое представление, а не урезанный план | `plan_pool` без изменений |
| **Replay** | runner вызывает `RRL_STOCK_POOL_CMD.assert_access` среди scope-hooks **до** ветки «операция уже выполнена»: право `stock_reservation_edit` на склад, а для записанного торгового плана — `operate` на собственника каждого класса из **его resolved plan** (без пересчёта по сегодняшним количествам). Потерявший право не получает старую квитанцию | +1 строка в `RRL_STOCK_POSTING_API`, `assert_access` в пуле |
| **Execute** | право на склад плана по текущему назначению (`RRL_ACCESS_API.allowed`) вместо глобального legacy `RRL_HAS_WRIGHT`; затем, как в C0160, operate на собственников использованных классов | `RRL_STOCK_POOL_CMD.execute_command` |

- Legacy-группа и GLOBAL_ADMIN сохраняются через `RRL_ACCESS_API.allowed`. Legacy-группа теперь действует для склада пользователя (RUSERS.WARE_ID), а не на любом складе.
- Глобальный `RRL_HAS_WRIGHT` не менялся.
- Обработчик ошибок пула root (общий `StockPostingError`) не трогался.

## Кандидат `db/migrations/2026-10-23_trade_pool_access/`
| Объект | Изменение |
|---|---|
| `RRL_STOCK_POOL_CMD` spec (+4) | `procedure assert_access(p_request, p_actor)` |
| `RRL_STOCK_POOL_CMD` body (+30) | `require_edit`, `require_plan_owners` (пустые `sources` или нет классов — выход, как execute-guard root), `assert_access`; execute: `require_edit(p_actor, ware плана)` вместо `RRL_HAS_WRIGHT` |
| `RRL_STOCK_POSTING_API` body (+1) | `if g_kind='RESERVATION_ALLOCATE_POOL'then RRL_STOCK_POOL_CMD.assert_access(p_request,p_actor);end if;` — среди scope-hooks перед `select ... RRL_STOCK_OPERATION where OPERATION_ID=g_operation`. Проводка, планирование и блокировки других команд не меняются |

- Before: pool spec E109…57D9, pool body **4ABD…796F** (после guard и empty-миграций root), posting body 6DAA…BC81. After — в manifest и verify.
- Apply: preflight → spec → body → posting → recompile (только INVALID) → verify. Откат — before-тексты.

## Python
- `infrastructure/pool_service.py`: `preview(warehouse, article, actor)` — READ ONLY, проверка склада до чтения снимка, `_visible_lines` (пачки по 500, одна проверка на собственника), фильтр строк, классов, долей и резервов, флаг `complete`.
- `api/pool_routes.py`: передаёт `user.username`, `PermissionError` → 403.

## Доказательства
| Что | Результат | Тип |
|---|---|---|
| Кандидат `assert_access` на 7 записанных пул-операциях root (6 торговых планов, 1 обычный) и новой операции | admin — ALLOWED; реальный активный пользователь без прав — `POOL_ALLOCATION_FORBIDDEN` до показа сохранённой операции | LIVE READ ONLY анонимный блок |
| Две ошибки, найденные этой проверкой до передачи | JSON-метод внутри SQL (ORA-40573) и `get_keys` пустого `sources` (ORA-06531) — обе исправлены, повтор прошёл | LIVE READ ONLY |
| pytest `test_trade_pool_access.py` 7/7 + прежние 16 (23) | склад до чтения; скрытый собственник убран и `complete=false`, план по полному снимку; неторговый целиком; маршрут 403; ровно один hook до replay; права и owners записанного плана; JSON не в SQL; хэши | offline |
| gate, encoding | PASS | — |

Живые сценарии root после apply и restart:
- scoped роль только на склад X — preview и allocate на X, отказ на Y;
- отзыв owner после сохранённой квитанции — повтор отказывает;
- отзыв назначения склада — повтор отказывает;
- legacy и GLOBAL_ADMIN проходят.

Пользователя без owner-права, но с правом склада, в БД нет; создавать такие данные мне запрещено.

## Ограничения
- Видимость строки в preview: достаточно видеть собственника источника **или** получателя (правило capacity). Если нужен строго собственник источника, это одна строка.
- Скрытые строки не раскрываются ни числом, ни остатком: `available_quantity=null` при `complete=false`.
- Новый allocate без записанного плана проверяет собственников в execute (C0160), до этого — только склад.
