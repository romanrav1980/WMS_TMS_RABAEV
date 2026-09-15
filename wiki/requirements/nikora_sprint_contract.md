# NIKORA: общий контракт реализации и приёмки спринта

Дата: 15.09.2026. Применяется ко всем карточкам [каталога](nikora_sprints/index.md). План/стоимость: [[roadmap/nikora_agent_delivery_plan]]. Запуск: [[runbooks/nikora_agent_launch]].

## 1. Что означает «готов спринт»

Спринт — законченный проверяемый вертикальный сценарий, а не объём написанного кода. Для архитектуры это исполняемый API/Oracle-сценарий; для функциональности — действие пользователя + серверный факт + внешнее сообщение, если оно входит в карточку. Для пилота — наблюдаемый операционный период.

Обязательный результат: код, тесты, миграции при необходимости, readback из изолированной БД, права, аудит, инструкция и воспроизводимый отчёт. Макет, устное «работает», один unit test или simulator внешнего контрагента не заменяют этот результат.

Статусы: DRAFT → READY → IMPLEMENTED → VERIFIED → ACCEPTED. Отдельно CONTRACT_READY / WAITING_EXTERNAL. Без действующего endpoint/весов/сканера соответствующий production gate остаётся WAITING_EXTERNAL. Автор кода не принимает собственный результат единолично.

## 2. Условия READY

- Утверждены зависимые карточки; выбран конкретный branch/SHA с явно включёнными пользовательскими незакоммиченными изменениями. Нельзя создать worktree от HEAD и забыть нужные текущие правки.
- Есть owner процесса, решения Q01–Q07 из GAP, нужные mapping/нормы/права/оборудование. Неизвестные параметры нельзя угадывать в коде.
- Для одного agent ticket указан точный allowlist файлов и тестовый oracle: вход, ожидаемый результат, негативный случай. Пути в карточках — точки расширения, не право переписать всю папку.
- Никаких production credentials в контексте агента. Отдельная test schema/tenant, обезличенные XML и журнал. Приватные данные разрешены облачному провайдеру только в согласованном контуре.
- Подтверждены тариф/доступность выбранной модели и budget ceiling. Названия agents/profiles не означают уже установленные CLI или оплаченный доступ.

## 3. Общие интерфейсные правила

URLs и имена новых сущностей в карточках — **проектируемые контракты**, не утверждение об их наличии. На старте ticket проверить существующий router/service/package; переиспользовать подходящий API. Изменение canonical контракта требует ADR и contract tests до UI.

Write-команда: commandId, subjectId, expectedVersion, payload, correlation/causation. Actor/site/права определяются серверной сессией, не доверенным полем пользователя. Время физического факта хранится с offset/UTC; UI показывает рабочую зону явно.

Ответ: effectId, newVersion, domain status, event IDs и outbox state. HTTP/transport receipt/APPLIED/физическое исполнение — разные состояния. Типовые ошибки: VALIDATION_ERROR, UNKNOWN_REFERENCE, VERSION_CONFLICT, INCOMPATIBLE_RESOURCE, QUALITY_HOLD, ALREADY_LOADED, SOURCE_NOT_AUTHORIZED. Mapping на 4xx/409 и legacy errors фиксируется в контракте, а не произвольно меняется между экранами.

Inbox: сохраняет исходный документ даже при ожидаемой отсутствующей зависимости. Idempotency по message/command и семантической версии; один и тот же GTIN не является ключом dedup физического скана.

## 4. Инварианты, которые не упрощаются ради дешёвого агента

1. GLN/GTIN/SSCC — строки с ведущими нулями. Обычный идентификатор паллеты WMS не обязан быть SSCC; строгая проверка включена только на требуемой границе NIKORA.
2. Master data не равны OrderManifest. Коммерческий заказ и фактическое исполнение не переписываются изменением справочника.
3. Missing source не ноль. PLAN и ACTUAL_ONLY не объединяются: второй не резервирует перевозку до разрешённого факта.
4. Количества связаны с owner/order-line/part/SKU/batch/UoM; PCE/KGM для catch-weight нельзя переводить постоянным коэффициентом.
5. Top-HU capacity исключает двойной счёт parent+child. Нет циклов/двух родителей. Repack сохраняет balance/provenance и инвалидирует старый quality admission.
6. Два контрольных прохода независимы; scanId отличен от GTIN. Вес/осмотр не заменяются сканом HU.
7. Сборка, качество, готовность к погрузке, LOADED, DEPARTED и store receipt — разные факты.
8. ERP получает ORDER_ASSEMBLED, INTERNAL_MOVEMENT_PLANNED, ORDER_IN_TRANSIT, ORDER_DELIVERED_TO_STORE. Причинность по part/leg/version; planned movement может предшествовать assembly. IN_TRANSIT только после DEPARTED, не внутреннего перемещения ричтраком.
9. RELEASED snapshot и исходное обещанное окно неизменяемы обычной правкой. Hard constraints одинаковы для manual/auto.
10. Груз на технике/loaded не переназначается как ожидающая задача; нужен подтверждённый физический unload/transfer.
11. Domain change + event + outbox в одном commit; network delivery at-least-once, бизнес-эффект идемпотентный. Не обещать exactly-once сеть.
12. Legacy billing/rights/stock/регуляторика сохраняются. Новые WMS, Kafka, графовая БД и generic workflow не входят в scope.

## 5. Правило ограниченного agent ticket

Одна карточка разбивается на 3 указанных шага; каждый шаг при необходимости — на 2–3 короткие сессии, **не один автономный запуск на весь спринт**.

- Local: 1–3 редактируемых файла, одна чистая функция/состояние экрана/fixture, до 250 строк смыслового diff. Контекст вместе с инструкциями 8–10k, output до 2–4k, не более двух попыток.
- Средний облачный: 3–6 файлов, один endpoint + его UI или один обработчик, до ~600 строк смыслового diff; 16–32k контекста, 20–30 tool turns.
- Сильный: один инвариант/транзакционный сценарий; обычно 4–8 файлов и до ~1000 строк; 32–64k контекста. Размер не разрешает массовую архитектурную переделку.
- Лимиты diff ориентировочные, не стимул дробить транзакцию на несогласованные commits. Если цель не помещается — новый ticket с явным контрактом, не молчаливое расширение.
- Stop: две неудачные попытки с тем же дефектом, выход за allowlist/контракт, нарушение баланса/прав, ≥80% бюджета без приёмки. Сохранить patch, failing test и handoff; эскалировать уровень, не зацикливаться.
- Сначала контракт/красный тест, затем минимальная реализация, потом независимые негативные тесты. Тестировщик получает ТЗ и patch, но не верит summary разработчика.
- Не менять assertions/fixtures, чтобы скрыть ошибку. Изменение бизнес-ожидания утверждает владелец требования.

## 6. Полномочия и Git

Один worktree/ветка на ticket. Shared paths (transport_service.py, terminal App.tsx, Oracle migration sequence) имеют одного владельца записи; независимые агенты не пишут туда одновременно. Локальный кодовый помощник не получает прямого доступа к Oracle writes, deploy, секретам, commit/push/merge.

Reviewer имеет read-only доступ к production-коду; создание независимых тестов — в отдельном test worktree/allowlist. Тесты исполняет утверждённый runner на test schema. Ни модель, ни её флаг «без вопросов» не заменяют OS sandbox, права БД и сетевые ограничения.

Merge/deploy и применение миграций в live выполняет назначенный человек/утверждённый pipeline после evidence. Пользовательские правки сохраняются. SAP/SAP_INTEGRATION не публикуется.

## 7. Приёмочная матрица каждой карточки

- Happy path, конкретный отрицательный случай из карточки, повтор команды, отказ связи/процесса, concurrent version/claim.
- UI: empty/loading/error/stale/403/409, keyboard/touch, mobile 360 px; реальные scanner/scales там, где предусмотрены.
- API: contract fields, authentication/authorization/site scope, structured errors, correlation.
- Oracle: before/after balances/status/keys, миграция apply/verify/rollback; зеркало wiki/database после настоящих schema changes.
- External: packet log/send/ACK/business effect и контроль количества на обеих сторонах. Simulator проверяет только контракт.
- Legacy regression по затронутым сервисам, не обязательно полный прогон всего репозитория после каждой маленькой правки.
- SQL: RRL_SQL_SLOW_LOG, /api/admin/slow-sql, Oracle top SQL, API audit; каждое превышение согласованного порога получает rewrite/window/batch/cache/index/stats/backlog с владельцем.
- UTF-8 check и git diff --check; wiki/index/log обновлены.
- Feature-flag rollback прекращает новые команды, не удаляет физические факты.

## 8. Команды и evidence

Карточки задают будущие тестовые файлы под tests/nikora/. Сейчас это задания на их создание, не существующие проходящие тесты. Сначала проверить штатный runner/venv/Oracle fixture setup репозитория; не запускать мутационные тесты с production DSN.

Базовые цели после реализации: pytest узкого модуля, соответствующий Playwright сценарий, Oracle verify SQL и encoder check. Test report должен содержать SHA, model ID/version/effort, реальные input/cache/output tokens, стоимость, команды/exit codes, test IDs, passed/failed/skipped, скриншоты и DB readback. Не записывать ключи/пароли и необезличенный XML в общий отчёт.

Технические доказательства хранить в reports/nikora/<sprint>/<run>/; создание каталога/артефактов разрешено в рабочем дереве. Пока реализации нет, каталог не требуется. Реальный расход сравнивать с [[roadmap/nikora_agent_delivery_plan]], пересчитывать оставшийся backlog после S0 и первых двух доставленных сценариев.

