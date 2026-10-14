# Точный момент начала сборки CASE
Миграция2026-10-12-361-case-actual-aware-start APPLIED dev RABAEV/orcl. Existing CaseActions.start_task записывает STARTED_AT_INSTANT TIMESTAMP WITH TIME ZONE вместе с прежним началом, назначением и STARTED event в той же metadata transaction/ordered CONFIG6. Повтор сохраняет первый момент и один event. Guard запрещает импорт выдуманного начала, изменение первого момента, backfill старого naive STARTED_AT и запись пояса без достоверного источника.

RRL_RESOURCE_SHIFT.START_AT/FINISH_AT — TIMESTAMP(6) без пояса. Поэтому STARTED_SHIFT_TIME_ZONE пока NULL, включая назначенные смены. Physical ZONE_CODE не является часовым поясом. Старые времена не интерпретируются как UTC или местные. Для выбора рабочего дня необходима явная политика пояса склада.

Actual361: собственное пустое CASE с отдельным типом тары, штатный COUNT1/BOOK, existing start/currentserver with Oracle offset, repeated start/one event, immutable guard, transaction rollback. Python Oracle thin fetch datetime не сохраняет tzinfo; доказательство offset получено Oracle TO_CHAR(TZH:TZM), а не предположением Python. После проверки BOOK_CANCEL/COUNT0, пустая fixture metadata отмечена CANCELLED. Обычный empty-return отказал CASE_EMPTY_CANCEL_LINE_BOUND_1_200 из-за отсутствия строк; это не объявляется успешной бизнес-отменой. Товар не создавался, protected P20/H20 неизменны. Context tmp/context361.json; initial factory не повторять.

Период существующего BOX cost пока loaded UTC. Новое поле подготавливает достоверный источник начала; NS56 этим не закрыт.
