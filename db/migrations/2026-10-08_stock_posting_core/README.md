<!-- Current status supersedes the historical runtime-016 description below. -->
Current 2026-10-08: wiki/database/nicora_stock_posting_handlers.md.
Components through 099 installed in existing RABAEV/orcl. Event bridge prevents a second explicit stock effect;
compatibility default OFF. MES calculation, supply, confirm/cancel use typed commands. Registry: 6 ADAPTED, 25 UNCONVERTED.
PREPARED, B0 NULL, stock/events/operations 0. Do not set ACTIVE manually.
current_runtime_manifest.json and 097_current_runtime.sql include 39 package pairs and native wrappers/guards.
scripts/stock_posting_install.py now preflights/refreshes that current installed foundation, never reset/bootstrap/cutover.
--apply creates a source-only checkpoint. The current bundle was not redundantly applied; its individual changed phases compiled live.
The description below is the original runtime-016 checkpoint, not the current feature/cutover status.

# Stock posting 2.0: подготовка и установка компонентов

8 октября 2026. Существующая RABAEV/orcl, без нового экземпляра и схемы.

Применены 014 foundation, 014b recompilation, 015 exact math и 016 command runtime (компоненты 016–027). Девять package и девять body VALID, три SYS grants выданы, policy catalog 72678 keys. PREPARED, новых stock operations 0, все 31 исходные legacy writer UNCONVERTED. Это подготовка единого переключения, не действующая новая проводка.

| Источник | Ответственность |
|---|---|
| 016_privileges_as_sys.sql | Прямые EXECUTE grants DBMS_LOCK/CRYPTO/FLASHBACK через существующее административное подключение |
| 016_locking.sql | Policy S/X до полного отсортированного набора anchors; проверка удержания и transaction identity |
| 017_context.sql | Закрытый доверенный контекст, только ACTIVE |
| 018_balances.sql | Точные совместные delta P/H, версии; append-only signed journal legs |
| 019_operations.sql | Полный canonical request, conflict/replay, сохранённый план и результат |
| 020_reservations.sql | Примитивы create/release/consume/relocate HARD; ещё не публичные handlers |
| 021_location.sql | Запрет обычной работы с недоступными ячейками |
| 022_command_plan.sql | Серверный compiler ресурсов MANUAL_MOVE; внешние списки locks не принимаются |
| 023_manual_move.sql | Целая немаркированная паллета без резерва, внутри одного склада |
| 024_posting.sql | prepare/execute/reset, обязательный существующий outbox; без TCL и внешних вызовов |
| 025_command_schema.sql | Дополнительный JSON-план в operation envelope |
| 027_policy_catalog.sql | Однократная публикация RELEASE/SKU/CELL policy keys в PREPARED |
| 026_complete_install.sql | Compilation gate и ledger ID 2026-10-08-016-stock-command-runtime |
| 026_verify.sql / 026_rollback.sql | Metadata verification и rollback только PREPARED без B0/operations |

Установка:

```powershell
api/wms_api_server/.venv/Scripts/python.exe scripts/stock_posting_install.py
# После административного применения 016_privileges_as_sys.sql:
api/wms_api_server/.venv/Scripts/python.exe scripts/stock_posting_install.py --apply
```

Installer проверяет schema/service, PREPARED и direct grants до первого DDL, сохраняет SHA-256 manifest. Он не запускает 016_privileges_as_sys.sql от RABAEV, не активирует release и не проводит товар. Apply идёт по dependency order: 025, 016–024, 027, 026. Следующая установка использует 028_install_runtime.sql, один OracleApply процесс/connection для этого набора. Wrapper изменён после успешной установки, повторно применять все DDL ради проверки wrapper не требуется. Повтор после частичной установки допустим только в PREPARED без операций; ledger записывается после VALID всех девяти package/body.

API `POST /api/inventory/stock-posting/manual-moves` использует право `stock_posting_manual_move`; actor берётся из авторизации, quantity — точная строка. В PREPARED запись отклоняется. Этот handler не заменяет task completion, приёмку, отбор или MES. Маркированный состав, агрегации, резерв, partial split и удержанный quality status требуют специализированного handler и сейчас отклоняются.

Все 31 исходные writer candidates остаются UNCONVERTED. B0/UOM normalization, полная closure маркированных units/HU, изменение policy writers через X-fences, перевод legacy receipt/task/pick/MES/C# и bridge/flag/cutover ещё не закончены. **Не устанавливать ACTIVE вручную.** Legacy event trigger остаётся текущим исполнителем; signed legs нового ядра рассчитаны на переключённый bridge, который исключит повторный stock effect.

026 rollback не запускался. Он удаляет только подготовленные runtime objects/plan column при PREPARED, пустом operation journal и отсутствии baseline. Policy catalog подготовительной установки сохраняется; identities не перенумеровываются. После активных committed фактов нужен регламент recovery.

Для обратимой установки пакетов/пустых metadata на этом выделенном dev достаточно source manifest и парного rollback. Новые VM/database snapshots не являются штатным gate: владелец отклонил их стоимость 08.10.2026. Дополнительный recovery определяется отдельно для разрушительного изменения или финального cutover.
