# wiki/codex — Аналитические файлы ассистента

Эта папка содержит файлы, которые создаёт и редактирует **только AI-ассистент**.

Назначение: синтез, анализ состояния проекта, стратегические планы и ТЗ, сформированные на основе изучения базы знаний и кода.

**Не редактируй вручную** — обновления будут перезаписаны при следующем анализе.

## Содержимое

| Файл | Назначение |
|------|-----------|
| [project_state_analysis.md](project_state_analysis.md) | Анализ текущего состояния проекта (обновляется при изучении) |
| [strategic_development_plan.md](strategic_development_plan.md) | Стратегический план развития системы |
| [transport_management_tz.md](transport_management_tz.md) | ТЗ: модуль управления транспортом (общий, все контуры) |
| [transport_dispatch_assignment_tz.md](transport_dispatch_assignment_tz.md) | ТЗ детальный: назначение СТ + авто-план + VRP (разделы 1–12) |
| [transport_final_tz.md](transport_final_tz.md) | **Финальное ТЗ** (компакт): 3 уровня, API, Oracle, оценка |
| [transport_ui_prompts.md](transport_ui_prompts.md) | 12 промптов для генерации UI рабочего места диспетчера |
| [transport_tms_summary.md](transport_tms_summary.md) | **Суммарное ТЗ** (креативная версия): ASCII-диаграммы, UI-мокапы, все уровни на одной странице |
| [transport_implementation_tz.md](transport_implementation_tz.md) | **Детальное ТЗ реализации**: Oracle DDL, PL/SQL пакет, FastAPI код, React компоненты, VRP-алгоритмы, тесты — всё для непосредственной разработки |
| [topology_grid_editor_tz.md](topology_grid_editor_tz.md) | **ТЗ: Excel-подобный редактор топологии** — создание склада с нуля, drag-выделение, назначение L/R/Проход, Z/U/SNAKE маршруты, from-grid API |
