> Актуальное продолжение 121–130: [[nicora_stock_posting_continuation_20261008]]. 47 package pairs; 10 ADAPTED / 21 UNCONVERTED; PREPARED, полного cutover нет.

# NICORA: реализация проводки 2.0

Current status 08.10.2026 supersedes the historical checkpoints below: [[nicora_stock_posting_handlers]]. Components through 119 installed; 45 package pairs, 9 ADAPTED / 22 UNCONVERTED. See [[nicora_stock_posting_extension_20261008]]. PREPARED, no B0 or full cutover.

8 октября 2026 года. Владелец поручил реализацию [ТЗ 2.0](../requirements/stock_posting_core_tz.md), затем явно разрешил очистить некорректные остатки тестовой RABAEV/orcl.

## Очистка dev

Миграция [013](../../db/migrations/2026-10-08_stock_dev_cleanup/013_apply.sql) сохраняет затронутые строки в архивной RRL_STOCK_CLEANUP_BAK_20261008, удаляет некорректные ключи/NULL/отрицательное количество, в группе дубликатов оставляет последнюю корректную строку по TIME_OF_LAST_UPDATE/ROWID. Количества не суммируются и не пересчитываются. Документы, паллеты и RRL_EVENTS сохраняются. Добавляются NOT NULL, unique UID/CELL и CHECK REMAIN>=0.

Это разрешённая очистка тестовых данных, не восстановление доказанного физического склада по журналу. Архив — история maintenance, не текущий регистр запасов. Rollback отказывается восстанавливать дубли при изменившемся journal/сохранённых строках или установленном новом stock schema; не запускался.

Перед применением сохранены 3744 затронутые строки, 23 Oracle writer definitions и 8 local writer files: [checkpoint](../../runtime/stock_posting_20261008/checkpoint/writer-checkpoint.json). Regex inventory — исходная карта, не доказательство полного разрешения всех динамических/косвенных calls. Current INVALID baseline: RRL_SAP_RECEIPT_API body и RRL_SAP_STORE_ROW_GUARD trigger; они возникли до нового ядра.

## Реализация ядра

Установка служебных объектов/кода и единый cutover разделены. Новое ядро не получает права изменять текущий запас в режиме подготовки. Все handlers переводятся до глобальной активации; existing event trigger остаётся единственным текущим исполнителем до этого переключения.

Новую схему, instance, TMS, складской количественный регистр и третий независимый резерв не создавать. Карантин определяется ячейками хранения/отбора. Изменяемые stock objects и SQL фиксируются здесь после применения с результатом live metadata.

## Применено 08.10.2026

- **013 APPLIED:** архивированы 3744 строки, удалено 1880, оставлено 1864 выбранных корректных записи. INVALID_ROWS=0, DUPLICATE_KEYS=0. NOT NULL ключей/REMAIN, unique UID/CELL и CHECK REMAIN>=0 установлены; constraints ENABLED/VALIDATED. [Результат](../../runtime/stock_posting_20261008/cleanup-result.json).
- **014 APPLIED:** RRL_STOCK_OPERATION/GUARD/POLICY_GUARD/UOM_CONVERSION/WRITER_REGISTRY/BASELINE/B0_ROWS/RELEASE; добавлены HARD_RESERVED_BASE/STOCK_VERSION/BASE_UOM и journal operation/line/leg/base поля. P и H имеют CHECK; CELL остатка/событий расширены до 60, как справочник RRL_CELLS. Физическое количество при 014 не менялось.
- **015 APPLIED:** RRL_STOCK_MATH package/body VALID, положительная величина, разрешённая шкала, рациональный коэффициент и запрет округления. Read-only функция Oracle 2.5×24=60; непривязанные к новому B0 legacy quantities не объявлены нормализованными.
- **014b APPLIED:** после ALTER TABLE зависимые старые objects получили Oracle INVALID. Перекомпилированы без изменения source, новый compilation debt устранён; осталось исходное состояние из двух ранее INVALID объектов. Включён фактически enabled event trigger с BIN$-именем, который нельзя игнорировать как recycle-bin при проверке текущего writer.
- В WRITER_REGISTRY зарегистрирован **31 исходный candidate как UNCONVERTED**, конвертаций пока 0. Release **PREPARED**, BASELINE_ID NULL, новых товарных operations 0. Старый event trigger по-прежнему один enabled; flag/bridge пока не переключены.

## Runtime установлен 08.10.2026

SQL компоненты [016–027](../../db/migrations/2026-10-08_stock_posting_core/README.md) установлены: порядок locks, закрытый context/transaction identity, атомарные P/H delta, replay/conflict envelope, create/release/consume/relocate HARD, обычный cell gate. Добавлены public prepare/execute/reset, compiler ресурсов для MANUAL_MOVE, сохранение плана, два signed journal legs и обязательный существующий RRL_EVENT_OUTBOX. Девять package и девять body VALID; migration 2026-10-08-016-stock-command-runtime APPLIED. Каталог содержит 72678 policy keys. Current INVALID остался исходным: RRL_SAP_RECEIPT_API body и RRL_SAP_STORE_ROW_GUARD. Полные domain handlers и unit/HU bindings не завершены; это не принятая whole-system posting.

Препятствие grants устранено: из существующей OS-сессии oracle подключились локально SYSDBA после unset TWO_TASK/LOCAL, выбрали PDB ORCL и применили [prerequisite](../../db/migrations/2026-10-08_stock_posting_core/016_privileges_as_sys.sql). Все три прямых EXECUTE подтверждены. Пароль не запрашивался и не сохранялся. [Runbook](../runbooks/nicora_oracle_local_admin.md).

Python inventory содержит точные contracts/resources, bounded UoW (полный rollback, тот же ID, неизвестный commit, изоляция сломанного соединения). Одна lease на все попытки исключает повторный полный срок ожидания pool; после неизвестного commit автоматического retry нет. UoW заранее отклоняет запись в PREPARED. Existing pool сохранён размером 12, ожидание соединения ограничено 30 с вместо бесконечного WAIT.

Добавлен `POST /api/inventory/stock-posting/manual-moves` с отдельным правом stock_posting_manual_move, authenticated actor и quantity-string вместо float. Handler рассчитан только на целую немаркированную паллету без HARD, внутри склада. У существующей паллеты сохраняются UID/SKU/партия/срок; настройки маркировки читаются из RRL_SKU_RECEIPT_POLICY/PROFILE, состав — из существующих RRL_WMS_RECEIPT_UNIT/RRL_CRPT_AGGREGATION. Маркировка/агрегация/резерв/частичный split требуют других handlers и отклоняются, не обходятся количественной проводкой. Ячейки карантина исключает обычный cell gate. Этот endpoint не подключён вместо действующего task/receipt/pick/MES, запись остаётся закрытой PREPARED.

Installer [stock_posting_install.py](../../scripts/stock_posting_install.py) проверяет service/schema/state/direct grants до DDL, сохраняет source hashes, устанавливает компоненты по зависимостям и записывает ledger только после VALID девяти package/body. Он не выдаёт SYS grants и не активирует release. [Manifest](../../runtime/stock_posting_20261008/runtime-install-preflight.json) подтверждает applied=true/18 VALID. Для следующих установок добавлен 028 bundle: один OracleApply процесс/connection вместо 12 запусков, без повторного live apply ради проверки wrapper. Опциональный --wait-ready ждёт загрузки существующего сервиса до DDL.

Снимок VM на этом шаге оказался избыточным и задержал работу. После pause в live snapshot VirtualBox завис в SUSPENDED_EXT_LS; та же VM перезапущена, CDB OPEN/ACTIVE и ORCL READ WRITE, подключение RABAEV восстановлено, grants сохранились. [Инцидент](../incidents/oracle_live_snapshot_20261008.md). Новой схемы/второго Oracle/копии базы для разработки не создано. Владелец отклонил такие затраты для обычного шага: дальнейшие обратимые package/additive metadata changes идут с source checkpoint и rollback, без новых VM snapshots. SQL 027 для последующих запусков сначала выделяет distinct ARTICUL, сокращая повторные PL/SQL key computations по историческим паллетам; текущую инициализацию не повторяли.

Пять адресных проверок [transaction runner](../../tests/nicora/test_stock_posting_uow.py) прошли: whole rollback после deadlock, один connection/неизменный request при retry, отсутствие retry после неизвестного commit, отклонение float/actor override и истёкшего deadline. Это Python/fake-driver проверки, не доказательство конкурентной Oracle-проводки. Сбой возврата соединения в pool не скрывает известный committed результат. Количественные поля RRL_REMAINS/RRL_EVENTS/RRL_STOCK_RESERVATION в live Oracle имеют unconstrained NUMBER, без скрытого округления объявленной шкалой. Import зарегистрировал три маршрута. Физические команды не запускались.

Добавлены read-only endpoints `/api/inventory/stock-posting/status` и `/operations/{operation_id}`, с существующим stock_reservation_view. Результат чужой операции доступен только GLOBAL_ADMIN, собственной — её actor; отсутствие committed видимой операции не утверждает rollback. Проверены import/регистрация двух маршрутов, exact quantity/key helpers и реальный PREPARED read. [Свидетельство](../../runtime/stock_posting_20261008/foundation-check.json). Физические business commands и нагрузка не запускались.

SQL решение этого подготовительного шага: новые reads ограничены PK release/operation, дополнительных scan/index не требуется. ROW_NUMBER/sort cleanup — однократный maintenance под закрытой таблицей, не алгоритм физической проводки. Stock hot path/batching/locks и RRL_SQL_SLOW_LOG/top SQL анализируются после первого согласованного реального posting case; его пока не было. Общий encoding check имеет прежнюю единственную ошибку raw TRANSPORT_TASK_PACKAGE_BODY.sql (U+0420 U+00A0), новые файлы не указаны. Raw source не правился.

## Следующий шаг

Расширить handlers и подключить действующие receipt/task/pick/MES/admin/C# writers с source/actor/units/reserve/closure checks. Заполнить полную dependency map, публикацию новых policy keys и перевод policy writers на X-fences, нормализацию B0, legacy bridge и cutover. Активация остаётся единой после готовности полного набора. PREPARED, operation count 0, 31 исходный writer UNCONVERTED. Это не закрытый NI03 и не завершённая реализация ТЗ 2.0.
