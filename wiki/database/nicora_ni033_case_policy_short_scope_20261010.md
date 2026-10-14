# NI03.3: склад правил маркировки и списка недостач (166)

Владелец resources для доступа, inventory для карточки маркировки. GET CASE line marking-policy теперь передаёт текущего actor и вызывает RRL_CASE_TASK_ACCESS с case_pick_execute в одном READ ONLY snapshot с прежней карточкой SKU. Состав профилей/признаки маркировки не пересчитаны и не продублированы.

GET /api/case-pick/shorts читает только недостачи CASE-заданий текущего склада; действующий case_pick_view/WARE/GLOBAL_ADMIN читается в том же snapshot. Прежний query вынесен из CasePickService, внутренний delegate сохранён. Лимит1–500, неизвестная строка404, чужой CASE403, смена текущего склада учитывается немедленно.

Композиция передаёт конкретный callback публичного ресурcного допуска в marking reader. Первоначальный прямой inventory→resources import образовал цикл через прежний tare reader; он удалён, callback обязателен и HTTP выбирает нативный scope helper. Business rule остаётся Oracle, baseline не расширен.

Авторский scripts/ni033_case_policy_short_scope_case.py: текущие CASE1031/unmarked карточка совпадает с admin; чужая строка403/несуществующая404/текущаяWARE9104отказ403. В базе17недостач чужих CASE; личный список возвращает только свой склад;501лимит422. Временное собственное view право/WARE полностью восстановлены, P20H20 неизменны. Положительный marked CASE card не заявлен этим случаем.

Architecture530/0cycles/76debt PASS/encodingPASS. SQL shorts14.287ms, markingcard7.520ms. Решение: сохранить существующиеPK/ограничение500/51profiles и один snapshot; новый индекс не нужен. Ownerresources проверяет промышленную кардинальность истории отдельно. Investigation/camera и metadata close/reject остаются отдельным остатком, полный спринт не закрыт.
