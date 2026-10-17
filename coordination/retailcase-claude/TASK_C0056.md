# C0056 — совместная реализация прав и встроенных знаний

Назначено владельцем 14.10.2026: выполнять до реализации согласованного объёма. Это продолжение C0049 с принятым новым контрактом, не возврат к старому freeze. Статус WAITING_FOR_ACK: запуск Claude и договорённость подтверждаются только его ACK.

## Источники

wiki/index.md; wiki/architecture/retailcase_scoped_access_and_knowledge.md; wiki/roadmap/retailcase_access_knowledge_plan.md; wiki/architecture/retailcase_modular_development_contract.md; config/architecture/retailcase-policy.json; wiki/concepts/ui_interaction_rules.md. C0055 замечания остаются действующими. KPI не утверждены и фиктивными значениями не заполняются.

## Разделение

Codex: весь Oracle/SQL, auth и scoped-допуск, backend platform/API знаний, миграции/seed, композиция backend и интеграция общих frontend main.tsx/App.tsx/api.ts, wiki/index/log, общая приёмка. Он не переписывает зарезервированные файлы Claude до RELEASE.

Claude: полный каталог C0049, организация и сценарии, frontend features/access-admin/, features/knowledge-editor/, features/workspaces/, существующий features/platform/help/ после ACK принятия этой области; пользовательские инструкции в docs/help/authoring/; отчёты в reports/retailcase/2026-10-14/claude/C0056/. Существующие большие UI-компоненты не расширять новым сценарием: выделять feature и передавать точечный integration patch владельцу. Auth/Oracle/main/api.ts и docs/help/published.json не менять. Для существующих transport/delivery/terminal файлов сначала точный file-lock contract.

## Непрерывная очередь Claude

1. ACK C0056, актуальный CLAUDE_STATUS, зарезервированные файлы. C0049 доработать по C0055: полный каталог/организация/permission mapping с областями и состоянием ready/planned. Нельзя выдавать справочник за реализованный UI.
2. Реальный AccessAdminPage: роли/права, группы объектов/состав/preview, назначения/сроки/отзыв, объяснение доступа, версии и неизменный operation_id при неизвестном исходе.
3. Реальный KnowledgeEditorPage: список/поиск, редактор черновика, preview безопасного текста, публикация/архив, история и связи, право редактора. Встроенная помощь: все новые действия tooltip/help_id/«Подробнее», mouse/focus/mobile/Escape, причины недоступности, не терять рабочий черновик.
4. WorkplaceHome и четыре рабочих места: директор РЦ, диспетчер, комплектовщик, водитель; reuse реальных API и компонентов. Без вымышленных KPI/кнопок. Перед изменением существующих файлов запросить конкретные locks.
5. Продолжить оставшиеся роли/помощь и адаптацию терминала по плану AK/KH. При зависимом backend-blocker — CONTRACT_REQUEST и независимый следующий блок, не простаивать.

## API и интеграция

Рабочий контракт: ACCESS_KNOWLEDGE_API_V1.md. Изменение схемы сначала CONTRACT_REQUEST → сообщение Codex CONTRACT. По мере появления backend Codex пишет READY. Пока API ещё не готов, можно писать типы, компоненты и локальный component preview, но в продукте не выдавать мок за настоящий результат. После каждого независимого блока RESULT + точные файлы + тесты/screenshots + GAP + RELEASE. Нельзя объявлять весь объём готовым после одного макета.

Общие файлы принадлежат Codex: передавай integration patch в proposals/C0056/integration/, Codex применит. Входящие сообщения читать перед блоком, после результата и при ожидании не реже60секунд. Не делать commit/push и не применять миграции. Общий gate выполняет Codex после интеграции; свой TypeScript и адресные UI-проверки выполняй на блоке. Существующие пользователи не переназначаются автоматически.

## Уточнение C0061

Новые UI расположены внутри зарегистрированного platform: features/platform/{access-admin,knowledge-editor,workspaces}/. Первоначальные отдельные features/* пути выше заменены этим уточнением; policy/baseline не расширяются. Перемещение своих файлов выполняет Claude.
