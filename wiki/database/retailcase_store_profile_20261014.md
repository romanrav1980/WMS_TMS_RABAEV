# Профиль магазина и его применение

Установлено 14.10.2026 в RABAEV/orcl. MIGRATION_ID: 2026-10-14-1490-ni051-store-profile. [SQL](../../db/migrations/2026-10-14_ni051_store_profile/apply.sql), checkpoint000/rollback/verify рядом. OracleApply7statements Errors0.

RRL_STORE_PROFILE хранит текущую версию по существующему строковому STORE_ADDR; RRL_STORE_RECEIVING_WINDOW — недельные интервалы, RRL_STORE_PROFILE_CHANGE — неизменяемый журнал операции и результата. API master_data/store_profile сохраняет профиль, окна и историю в одной CONFIG-транзакции с expected_version и actor/request-bound replay. Legacy RRL_ADDR имеет уникальный индекс, но не PKconstraint: существование проверяет guard, новый FK к legacy не создаётся.

Расписание UNCONFIGURED либо WEEKLY; явный timezone из каталога Oracle; максимум8интервалов/день,56/неделю. При WEEKLY отсутствующий день закрыт. Read bound57 с отказом при>56 защищает от обрезания; запись executemany. UTC разрешён, существование timezone проверяется в Oracle. Подсобка/рампа/способ разгрузки — справочные параметры, сами по себе не отменяют приёмку, маркировку или другие допуски.

Недельные окна используются [[retailcase_ni081_store_weekly_windows_20261014]], внешние ограничения [[retailcase_store_access_dimensions_20261014]]. Не сравнивать их с внутренними размерами кузова: [[retailcase_vehicle_outer_dimensions_20261014]].

[Результат интеграции](../../reports/retailcase/2026-10-13/71-store-fleet-route-integration.md). Живой API случай C0029 завершён на собственном Own264: версия/повтор/конфликты, 56окон безобрезания, восстановление исходного новойверсией; K0037. Независимая приёмка отдельно.
