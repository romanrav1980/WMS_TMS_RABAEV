# Sprint 68 — Usability Checklist: Ctrl+Enter — добавить СТ в рейс

## Сценарий: Keyboard shortcut

- [ ] Выделить 1+ СТ, выбрать рейс, нажать Ctrl+Enter → СТ добавлены в рейс
- [ ] Ctrl+Enter не срабатывает, если нет выделенных СТ
- [ ] Ctrl+Enter не срабатывает, если не выбран рейс
- [ ] Ctrl+Enter не срабатывает на вкладке «Маршруты» (activeTab !== "tasks")
- [ ] Ctrl+Enter не срабатывает при фокусе в поле ввода (INPUT, SELECT, TEXTAREA)
- [ ] Кнопка «Добавить в рейс» имеет tooltip «Ctrl+Enter»
- [ ] Кнопка «Добавить в #ID» в sel-bar имеет tooltip «Ctrl+Enter»
- [ ] Mac: Cmd+Enter работает аналогично (metaKey)

## Регрессия

- [ ] Escape handler (Sprint 44) работает как раньше
- [ ] Enter в поле ввода порядка (ORD) не добавляет СТ в рейс
- [ ] Создание нового маршрута через + Создать маршрут работает
