# NI08.1 / 638: непрерывное вождение нескольких рейсов

Подготовлено для локальной Qwen, независимый прогон не выполнен. Source wiki/components/retailcase_ni081_cross_trip_continuity_20261012.md.

На одном действительном source-approved driver day проверить существующие time-preview/Gantt/common coordination. Два разных рейса90 и40 минут с разгрузкой10 между ними дают непрерывное130, конкретный blocker DRIVER_CONTINUOUS_DRIVE_LIMIT с operation/day. REST15 между ними снимает это нарушение; REST14 не снимает. Ни новый рейс, ни работа, ни полночь не считаются отдыхом.

Проверить локальную полночь120+30=150, отсечение будущей части22:00–00:30 до120 в предыдущем дне, mixed approved zones, дубли operation IDs, missing times, overlapping intervals, stale source/foreign WARE/actor. Общий дневной540 и непрерывный120 — разные проверки, суммы не смешивать. Начальная смена/внешняя занятость/правовые нормы остаются unverified: тест не должен объявлять реальный допуск.

Нельзя пересоздавать259/33564 или254/33570 и переписывать прежние OPS. Сначала собственная isolated fixture; outer rollback для metadata changes, без quantity writes. Scoped real GET result/current hashes и конкретный slowSQL decision; полный регресс/нагрузка сейчас не назначены.
