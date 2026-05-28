# Sprint 67 — Usability Checklist: Amber rows for unready STs in trip detail

## Сценарий: Состав рейса с несобранными СТ

- [ ] СТ с VERIFY_PERC < 100 отображается с желтоватым фоном (amber #fffbeb)
- [ ] СТ с VERIFY_PERC = 100 не имеет amber-фона — стандартный белый
- [ ] СТ с VERIFY_PERC = null не имеет amber-фона
- [ ] При наведении на unready-строку фон темнее (#fef3c7)
- [ ] При выделении (checked) unready-строки — ещё темнее (#fde68a)
- [ ] Сочетание .selected + .dispatch-gr-unready корректно (нет flash белого)
- [ ] Таблица «Маршруты» RouteTaskStRow — без изменений (регрессия)

## Регрессия

- [ ] VERIFY_PERC полоска (VerifyBar) отображается корректно
- [ ] Сортировка строк не сбивает подсветку
- [ ] Снять СТ с рейса — строка исчезает нормально
