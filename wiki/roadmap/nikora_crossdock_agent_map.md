# NIKORA: карта автора для раннего кроссдокинга

Дата: 16.09.2026. Это исполнимое назначение для 21 инкремента [[requirements/nikora_crossdock_increments]]. Очередь неизменна: `CD00 → CD19 → CDP`. Карта не меняет scope, календарь или смету профилей B/C/H/X/P из [[roadmap/nikora_agent_delivery_plan]]; она снимает неоднозначность, кому выдавать каждый ticket.

## Главное решение

**Основной автор критического контура — Codex с `gpt-5.6-sol`, `reasoning_effort=high`.** Ему выдаются Oracle/API-транзакции, учёт HU, custody и физические статусы. `gpt-5.6-terra` не пишет такой код первым: это более дешёвый независимый тестировщик/reviewer. `gpt-6-astra`, `high`, применяется только в CD02 и CD12: сначала фиксирует контракт и инварианты, затем Sol делает маленькую реализацию по этому контракту. Так дорогой контекст не расходуется на обычные адаптеры.

Для ограниченного UI, master data, отчётных XML и совместимого адаптера основным автором служит Claude Code с `claude-sonnet-5`, `effort=medium`; независимую проверку выполняет Codex Terra. `claude-opus-5`, `high`, не является обычным автором: он нужен для независимого review CD02/CD12 и для release-gate CD19. Локальный Qwen/Aider после CD00 допускается лишь к fixtures, тестовым XML, документации и изолированному UI; он не меняет Oracle-пакеты, идемпотентность, custody, freeze или реальные интеграционные endpoint'ы раннего контура.

Официальная причина такого разделения: Sol позиционируется как флагман для сложной профессиональной работы; Terra — баланс качества и стоимости, Luna — для массовых дешёвых задач, а Astra — для наиболее трудной сквозной работы. [OpenAI Models](https://developers.openai.com/api/docs/models). Claude Sonnet 5 и Opus 5 активны; оба поддерживают effort/adaptive thinking, поэтому ограничение ticket важнее увеличения длины одной сессии. [Anthropic model status](https://platform.claude.com/docs/en/about-claude/model-deprecations), [Claude prompting](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices).

## Правила выдачи одного шага

1. Владелец создаёт отдельный worktree от зафиксированной согласованной ревизии. Автор не работает в общем незавершённом дереве и не включает чужие staged-изменения.
2. На шаг выдаются три последовательных bounded tickets: контракт/отрицательный тест, реализация, независимое review + evidence. Автор не принимает собственную работу.
3. До CD00 локальная модель не является исполнителем. После её benchmark она может готовить fixtures и UI только с allowlist файлов; результат всё равно запускается в CI/Oracle runner независимым агентом.
4. Review блокирует merge при нарушении XML-idempotency/outbox, версии состава HU, custody, freeze, ролевой проверки, баланса или одного из четырёх ERP-событий. Исправляет блокер первоначальный автор; reviewer не делает скрытую доработку.
5. Статус `ACCEPTED_CD` ставит человек по фактическому evidence. Это не закрывает родительскую карточку полного объёма.

## Назначение по шагам

| Шаг | Профиль | Автор реализации | Независимый reviewer / тест | Практическая граница ticket |
|---|---|---|---|---|
| CD00 | B | Техлид-владелец + Codex `gpt-5.6-sol`, high — паспорт стенда | Claude Code `claude-sonnet-5`, high | Доступы, test Oracle, два источника и rollback; без продуктовой доработки. Qwen/Luna только benchmark. |
| CD01 | H | Codex `gpt-5.6-sol`, high | Claude Sonnet 5, high | Один XML ingress, schema/unknown-field/negative tests, без бизнес-оркестрации. |
| CD02 | X | Codex `gpt-6-astra`, high — ADR инвариантов; Codex Sol, high — реализация | Claude Code `claude-opus-5`, high | Один путь exactly-once/idempotency + outbox/retry; без новых типов сообщений. |
| CD03 | C | Claude Code `claude-sonnet-5`, medium | Codex `gpt-5.6-terra`, medium | Только адреса, магазины, артикулы и их revision. |
| CD04 | H | Codex Sol, high | Claude Sonnet 5, high | Один `OrderManifest` с revision/cancel и ожидаемыми частями. |
| CD05 | H | Codex Sol, high | Claude Sonnet 5, high | Стабильный ID исходной части/HU, link к заказу; без parent SSCC и repack. |
| CD06 | H | Codex Sol, high | Claude Sonnet 5, high | PLAN и ACTUAL_ONLY для WMS №1, включая повтор/невалидный SSCC. |
| CD07 | C | Claude Sonnet 5, medium | Codex Terra, medium | Четыре outbound ERP статуса и их мониторинг, без «успешно» до физического факта. |
| CD08 | C | Claude Sonnet 5, medium | Codex Terra, high | Совместимый тонкий адаптер WMS №2 по уже принятому контракту; без нового канонического формата. |
| CD09 | H | Codex Sol, high | Claude Sonnet 5, high | `Leg`/custody: один источник → хаб, с запретом двойного владения. |
| CD10 | H | Codex Sol, high | Claude Sonnet 5, high | Время, ворота, ёмкость для раннего ручного подвоза; без оптимизатора/VRP. |
| CD11 | H | Codex Sol, high | Claude Sonnet 5, high + человек по складу | Evidence повторного контроля существующей WMS: scan/weight/contentVersion; без нового QA-приложения. |
| CD12 | X | Codex Astra, high — модель freeze/release; Codex Sol, high — реализация | Claude Opus 5, high | Атомарный validator/freeze/release и негативные гонки; никаких упрощений правила состава. |
| CD13 | H | Codex Sol, high | Claude Sonnet 5, high | Ручная волна магазина и обратный расчёт времени; без автоматического планирования. |
| CD14 | H | Codex Sol, high | Claude Sonnet 5, high | Ручной маршрут и порядок загрузки/выгрузки в пределах одной волны. |
| CD15 | C | Claude Sonnet 5, medium | Codex Terra, high | Приёмка исходного HU в целевой WMS и линия магазина; без merge/repack HU. |
| CD16 | H | Codex Sol, high | Claude Sonnet 5, high | Подтверждение load/departed и только затем ERP `ORDER_IN_TRANSIT`. |
| CD17 | H | Codex Sol, high | Claude Sonnet 5, high | Минимальные исключения HOLD/missing/mismatch, без полного диспетчерского центра. |
| CD18 | C | Claude Sonnet 5, medium | Codex Terra, high | Приёмка магазина и ERP `ORDER_DELIVERED_TO_STORE`, включая частичный/повторный факт. |
| CD19 | H | Codex Sol, high — исправление найденных блокеров | Claude Opus 5, high + человек-владелец | Двухисточниковый release gate; reviewer только проверяет доказательства, не расширяет scope. |
| CDP | P | Человек-оператор; локальный Qwen/Aider — сводка журналов | Claude Sonnet 5, high — разбор инцидентов | 10 дней наблюдаемого пилота, без самостоятельного продуктового рефакторинга. |

## Что запускать фактически

- Для CD01, CD04–CD06, CD09–CD14, CD16–CD17, CD19: Codex Sol `high`, один CD-ID и allowlist в `TASK.md`; после завершения — новая независимая сессия Claude Sonnet 5 `high`.
- Для CD02 и CD12: первая сессия Astra создаёт только `ADR + invariant tests + acceptance matrix`; вторая сессия Sol реализует только этот матричный набор. Opus 5 получает diff, tests и Oracle evidence, но не право менять код.
- Для CD03, CD07–CD08, CD15, CD18: Claude Sonnet 5 `medium`, максимум один адаптер/экран/контрактный кусок. Codex Terra `medium` (для CD15/CD18 `high`) запускает tests и ищет нарушение контракта.
- Для CD00/CDP кодирование не является целью. В CD00 сначала зафиксировать baseline и воспроизводимость; в CDP — фактические показатели, инциденты и решение человека о расширении.

Luna — не автор архитектурного или складского ticket: её можно использовать для генерации тестовых XML, классификации логов и чек-листов с обязательной машинной валидацией. Это соответствует её назначению для cost-sensitive high-volume задач, но сохраняет ответственность сильной модели за изменения состояния. [GPT-5.6 Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna).

## Промпт-шаблон автора

```text
Ты автор только CDxx из wiki/requirements/nikora_crossdock_increments.md.
Прочитай AGENTS.md, CD-карточку и её родителей. Работай в отдельном worktree от указанного SHA.
Сначала создай/обнови TASK.md: scope, allowlist, инварианты, negative tests, команды проверки и out-of-scope.
Сделай только один bounded ticket. Не меняй соседние CD, не расширяй XML и не заменяй WMS-ядро.
Перед завершением выполни указанные тесты, зафиксируй API/Oracle evidence и slow-SQL decision.
Не ставь ACCEPTED_CD: это делает человек после независимого review.
```

Для reviewer заменить первую строку на «Ты независимый reviewer CDxx. Код не редактируй; воспроизведи проверки, проверь diff против инвариантов и верни только PASS/BLOCKED с evidence». Полные команды и stop rules — [[runbooks/nikora_agent_launch]].
