# NI07.1 — физический класс машины и источник на выезде

Миграция 2026-10-12-559-vehicle-source-at-departure: применена559/561/564; author профиль563/564 выполнен.

Существующий RRL_TR_VEHICLE остаётся справочником автомобилей. Установлено по live metadata: NUM/TR_TYPE/PALLETS/MAX_WEIGHT_KG есть; физические размеры грузового отсека и финансовый класс отсутствуют. Не выводить размер машины из вместимости или названия.

Дополнение: редактируемая только разрешённой командой версия класса и габаритов отсека в миллиметрах, основание и автор, сохранённые исходные поля автомобиля. История неизменяема. Повтор использует ту же операцию; изменённое сообщение с тем же ID отклоняется, новая версия требует текущей версии.

Существующий TRIP_DEPART будет фиксировать исходник машины, класса, перевозчика и районного ключа в той же транзакции с исходными фактами выезда. Старые рейсы не получают выдуманные габариты. Отсутствующий или изменившийся профиль фиксируется явно и запрещает нормативное начисление, не подменяется значением по умолчанию.

Прежнее ядро stock posting сохраняет единоличное изменение товара. Профиль и источник выезда — данные для последующего расчёта, без повторного списания товара, изменения рейсов/назначений или второго Oracle.

Native API/guards/DEPART hook и существующий fleet UI подключены. Открыто: адресный реальный выезд и единственное транспортное начисление по архивным фактам. Ни миграция, ни этот объём пока не завершены.

Применено55913/0,5613/0,5643/0; native errors/invalid empty after561. Existing fleet profile API/guards and original DEPART hook installed, no historical sources inferred. Profile configuration requires current fleet_edit, expected version and exact base hash. Active config whitelist now includes only this additional existing fleet permission; warehouse-settings privilege is not substituted.
563 first attempt refused configuration before any profile effect; original private vehicle retained.564 continuation: same-op two senders yield one v1; own base PALLETS20->21 invalidates current profile, exact v1 replay returns original, stale base hash rejected; v2 confirms current base. Native v3 outer rollback restores head2/removes new history; history delete refused. Only private vehicle changed, no trips/loads/goods created in this case. ctx563 retained; do not recreate case563/resume564.
FleetManagementPage uses new profile form through public finance facade and small VehicleFleetActions; new editor state at page composition, old VehiclesTab extracted rather than enlarged. Local TS562 PASS; architecture after final boundary fix needs pass. UI intent persisted before send per exact API/actor/vehicle, unknown response exact retry, confirmed409 correction refreshes base, no password persisted. Native state READY/BASE_CHANGED/NOT_CONFIGURED is explicit.
SQL563 current history1.075ms/4.2buffers, head lookup2.638ms/7buffers, same-op13.487ms/13buffers cold: retain PK(vehicle,version), OP unique and single-row base/head locking under short config fence. Owner transport/finance: publication rare; current source captures one read per departure, inspect same-source contention only on measured growth. No throughput/legal/hardware claim.
Next actual departure snapshot/one clock proof, immutable carrier/region source consumption and monetary recognition. Full NI07.1 remains open.

565/566: выполнен новый оригинальный LOAD/DEPART с READY profile1, source1 и одним точным clock; товарный эффект DEPART0.575: ранее созданный источник принят получателем BOX3 с завершённой MANUAL выгрузкой. Старый519 остаётся без выдуманного профиля. Manifest579 включает559/561/564; целиком на ACTIVE не применялся.
