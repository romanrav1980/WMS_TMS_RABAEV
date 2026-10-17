# help_id для экрана диспетчера и ТСД сборки (C0074, блок 1)

Экраны чужие: `components/TransportDispatchPage.tsx` принадлежит root/transport, `case-pick-tsd.html/js` — raw UI. Я их не редактирую. Владелец экрана добавляет атрибут `data-help-id`, а `title` оставляет как есть. «Подробнее» открывает статью через `openHelpArticle(article)` из `features/platform/help`. Статьи уже опубликованы: `dispatcher` v2 и `tsd-case-pick` v2.

## Диспетчер → статья `dispatcher`

| Элемент (текущий title/текст) | help_id |
|---|---|
| Предыдущий день / Следующий день / Перейти к сегодня | `dispatch.date.prev`, `dispatch.date.next`, `dispatch.date.today` |
| Склад (фильтр на сервере) | `dispatch.filter.warehouse` |
| Обновить рейсы / Автообновление | `dispatch.trips.refresh`, `dispatch.trips.autorefresh` |
| % сборки / Проверка % | `dispatch.trip.ready`, `dispatch.trip.verify` |
| Обновить список СТ / Показать только несобранные | `dispatch.st.refresh`, `dispatch.st.unpicked` |
| Итоги по загруженным СТ | `dispatch.st.totals` |
| Выделить все СТ рейса / Снять выделение / Копировать номера | `dispatch.st.select_trip`, `dispatch.st.clear`, `dispatch.st.copy` |
| Снять СТ с рейса | `dispatch.st.detach` |
| Создать новый рейс с теми же реквизитами | `dispatch.trip.clone` |
| Распечатать маршрутный лист / CSV / Excel | `dispatch.doc.route_sheet`, `dispatch.doc.csv`, `dispatch.doc.excel` |
| Пересчитать цену / Снять рейс со счёта | `dispatch.billing.recalc`, `dispatch.billing.detach` |
| Сбросить все фильтры / поиск | `dispatch.filter.reset`, `dispatch.search.reset` |

## ТСД сборки → статья `tsd-case-pick`

| Элемент (id) | help_id |
|---|---|
| cpTsdShiftLogin / cpTsdShiftLogout | `tsd.pick.shift.login`, `tsd.pick.shift.logout` |
| cpTsdClaim / cpTsdStart | `tsd.pick.claim`, `tsd.pick.start` |
| cpTsdPrev / cpTsdNext | `tsd.pick.prev`, `tsd.pick.next` |
| cpTsdConfirm / cpTsdShort / cpTsdClose | `tsd.pick.confirm`, `tsd.pick.short`, `tsd.pick.close` |
| cpTypeSave / cpTypeRetry / cpTypeRestart | `tsd.pick.type.save`, `tsd.pick.type.retry`, `tsd.pick.type.restart` |
| cpTsdMoveCarrier / cpTsdRetryCarrier | `tsd.pick.move`, `tsd.pick.move.retry` |
| cpTsdBindShipment | `tsd.pick.bind_st` |
| cpTsdPartialPreview / cpTsdPartialPrepare / cpTsdRetryPartialLayout | `tsd.pick.partial.preview`, `tsd.pick.partial.prepare`, `tsd.pick.partial.retry` |
| cpTsdReturnCarrier / cpTsdCancelEmpty / cpTsdRetryReturn | `tsd.pick.return`, `tsd.pick.cancel_empty`, `tsd.pick.return.retry` |
| cpTsdRetryPosting / cpTsdArchivePosting | `tsd.pick.retry`, `tsd.pick.archive` |

Для raw UI без React достаточно двух вещей: атрибута `data-help-id` и ссылки «Подробнее» на `/?help=<article>`. Нужна ли root-поддержка `?help=`, решает Codex.
