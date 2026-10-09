# NICORA: MCP и skills для полного проекта

Решение по составу инструментов: 2026-10-07. Основание — [[requirements/nikora_delivery_v55/README]], [[requirements/nikora_delivery_v55/testing_and_ai]], [[runbooks/evidence_driven_process_testing]] и [[database/oracle_change_protocol]]. Это выбор набора, не установка новых MCP или создание skills.

## Основной MCP-набор

| MCP | Назначение | Состояние |
|---|---|---|
| tms-wiki | Восстановление контекста, правила, решения и история | Smoke пройден |
| tms-repo | Ограниченное чтение и поиск кода для GAP и разработки | Smoke пройден |
| tms-oracle | Метаданные и ограниченные SELECT, SQL-инварианты и диагностика | Smoke пройден; только чтение |
| tms-playwright | Реальные ARM/ТСД UI, сетевые ошибки и снимки приёмки | Инструменты доступны; свежий запуск не проверен |
| tms-docker-routing | Compose и OSRM/Valhalla для транспортного контура | Инструменты доступны; свежий запуск не проверен |

PowerShell, Python, Node и .NET выполняют сборку, pytest, нагрузочные runners, миграции через существующий OracleApply и запуск служб. Отдельный универсальный MCP записи в Oracle не требуется. Наличие прав схемы не заменяет порядок применения миграций. ERP, весы, принтеры и камеры подключаются адаптерами приложения с отдельными контрактами и испытаниями, а не MCP разработчика.

Google Drive/Docs нужны при работе с исходными облачными документами; Sheets — при облачном реестре GAP. GitHub применяется только по отдельному прямому поручению публикации. Новые трекеры и Figma не обязательны для старта: очередь и требования уже хранятся в репозитории.

## Skills

Доступные skills по этапу: skill-creator для подготовки проектных skills; security-diff-scan/security-scan/threat-model и связанные fix/validation workflows по своему назначению; documents, spreadsheets, pdf, presentations для ТЗ, GAP, протоколов и обучения; Google Drive/Docs/Sheets при работе с облачными источниками. OpenAI Docs нужен для настройки Codex, а не для бизнес-логики NICORA.

Предлагаются шесть новых проектных skills (пока не созданы):

1. nicora-delivery — редакция 55, устойчивые ID правил, GAP, bounded tickets, зависимости, независимая проверка, wiki и закрытие карточек по evidence.
2. nicora-oracle — фактическая legacy-схема, PL/SQL, транзакции, остатки, резервы, конкурентный доступ, миграции apply/rollback/verify, планы и медленные SQL.
3. nicora-api-integrations — FastAPI, права, команды, идемпотентность, ERP XML, inbox/outbox, фоновые исполнители и адаптеры оборудования.
4. nicora-ui-terminal — React/TypeScript, ARM и PWA ТСД, сканирование, повтор после потери связи, реальные права/состояния, принятые UI/help-правила.
5. nicora-acceptance — pytest/Playwright, изолированные fixtures, товарные инварианты, ошибки, конкуренция, evidence reports и обязательный slow-SQL review.
6. nicora-operations — воспроизводимая сборка, Linux/Compose, бюджет Oracle-соединений, нагрузка, мониторинг, резервирование, восстановление, release/pilot gates.

Проектные skills должны ссылаться на maintained wiki и существующие runners, а не копировать требования или выдавать новые бизнес-правила. Общую ответственность за проект сохраняем, реализацию ведём ограниченными заданиями NS00–NS67. Никакие новые skills, внешние подключения, агенты или публикации этим решением не запускались.

## ??????????? ??????????

```powershell
python scripts/install_nicora_skills.py
python scripts/install_nicora_skills.py --install
python scripts/test_mcp_servers.py --report tmp/nicora_tooling/mcp-health.json
```

????? smoke ?????? ????????? ??? ???? MCP, ?????????? ?????? handshake ? ????-????. ??? ???????? ????????????? ??????? ????????????? ???????? --require-routing. ?????????? OSRM/Valhalla ?? ???????? ?? ???????? ???????????? ???????. SQL DDL ? ??????-???????? ???? ??????????? ?? ???????????.
