# NI02.2: нормативные варианты загрузки машины
14.10.2026 /1179–1180. Установлены профиль1179 и общий норматив1185; текущие packages/errors проверены, исправления1188/1189 включены в SQL.

Источник: процесс06 ТЗ57 — норматив вместимости конкретной машины по каждому типу тары и допустимым сочетаниям, без вывода из площади пола.

Владелец конфигурации — существующий RRL_VEHICLE_PROFILE_API/HEAD/HIST, право transport_fleet_edit, CFG fence, версия, source hash, неизменная история и точный повтор. Новых таблиц и stock writer нет. floor_variants:1–20 именованных вариантов, в каждом1–8 различных активных RRL_PALLET_TYPE и целое max_places1–1000. В одном варианте перечислены совместно допустимые количества типов; разные варианты альтернативны. Отсутствующий тип не разрешён этим вариантом. Геометрия грузового отсека и температура сохраняются отдельно.

API и карточка используют прежний save/intent/retry. Каталог читает существующий справочник с текущим правом просмотра, граница500. Настройка сама не является допуском погрузки: проверка фактических верхних HU и проводка остаются у существующих native owners; подключение следует отдельным блоком.

Миграция2026-10-14-1179-vehicle-tare-variants: [apply](../../db/migrations/2026-10-14_ni022_vehicle_tare/apply.sql), captured live before-body/checkpoint, paired rollback на прежний защищённый температурный профиль. Старые сохранённые request/results не переписываются.

## Подключение1185–1186
Подготовлен общий native check_floor_capacity: целые количества по типам, альтернатива вариантов, несовместимость и явная неизвестность. Его вызывает прежний RRL_TRANSPORT_PLAN_RULES.check_vehicle, следовательно прежний окончательный assign/apply получает то же правило. Для машины без матрицы сохраняется старое ограничение PALLETS; при заданной матрице вместимость берётся из норматива, масса/тип/гидроборт/адрес/временные окна сохраняются.

Источник типов на этой стадии ограничен одним действующим CASE на подготовленное место с активным типом. Несколько CASE, отсутствие типа и физические уже загруженные TOP без отдельной типизации дают unconfirmed; complete=1 отказывает, preview возвращает предупреждение. Вложенные HU не считаются автоматически несколькими CASE; поддержка доказанного типа физического TOP — следующий блок. Это консервативное ограничение, не полный физический допуск. Запрос с200 bind ST /5000мест; без JSON_TABLE на большом join. Snapshot/read vs locked final recheck сохранены. SQL миграции и captured sources в2026-10-14_ni022_vehicle_floor_rule.

## Результат1190

Actual retained vehicle10100/profile2: saved variants MIXED8EU+4TROL/TROLLEYS20, same temperature numeric bounds; rollback/replay/conflict passed. Native6 rule cases pass; SAP_2135/2unknown rejects final checker, no actual assignment claimed. SQL5.472ms31.33buffers →retain boundedIN/keys/noindex (ownertransport). P20/H20 unchanged. [Report36](../../reports/retailcase/2026-10-13/36-vehicle-tare-variants-report.md)/screens49–50. TS/architecture703/0cycles/76 pass; independent/full acceptance pending. Nextphysical TOP type.
