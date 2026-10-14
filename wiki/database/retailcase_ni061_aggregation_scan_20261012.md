# Межскладская приёмка по агрегационным кодам
Migration2026-10-12-310-interware-aggregation-scan APPLIED, dev RABAEV/orcl. Новое приватное RRL_IW_AGG_SCAN вызывается существующим RRL_INTERWARE_MARK_SCAN. Единственный quantitywriter остаётся Root + прежние receiving/balance/unit kernels.

## Разрешение состава
API /receive и /recovery-receipts принимает aggregation_scans(system_code,profile_code,level,code). Нормализация сохраняет точные байты кода и передаёт SHA256. Native допускает только ранее зарегистрированную агрегацию с доказанным применённым non-SAP sender manifest/use, текущей версией профиля и разрешённым BOX/PALLET либо UNIT_OR_AGGREGATION. SAP-источник агрегации пока явно не поддержан этим межскладским обработчиком; обычная SAP-приёмка использует прежний resolver.

Состав раскрывается в прежние hashes кодов физических единиц, сверяется с immutable sender members: unit ID, точное количество, исходный raw code соответствующего профиля. Только ISSUED без резерва. После раскрытия общий валидатор проверяет точную матрицу выбранного груза; foreign/missing/duplicate/overlap отказаны. Несовместимый уровень/версия и известная аннулированная CRPT-агрегация отказаны. Реальный государственный ACK не создаётся и не утверждается; это WMS-подтверждение состава.

Пределы:1000 агрегатов,10000 физических единиц,20000 раскрытых сканов/профилей. Уровни nested sender graph уже развёрнуты существующим импортом124; отдельный HU warehouse tree не создаётся автоматически.

## Фактический сценарий310
Собственный исходный товар3,6 codes/2 profiles; inventory birth по исходному sender graph4nodes: CRPT PALLET→BOX1+BOX2; EGAIS BOX3units. Прежние PICK/TASK/ST/QC/LOAD/DEPART применены без нового shipping owner. Целевой interwarehouse RECEIVE принимает3 по двум агрегационным сканам. Ранее зарегистрированные3units/6codes сохранены; P3/H0 в приёмочном карантине. Неизвестный/повторный/пропущенный агрегат отказан. Native outer rollback удалил receipt/P3, затем actual HTTP+exact replay успешны, protected20/20. tmp/context310.json — текущее состояние; sourcefactory/initialcase не повторять. Sourceсоздан один раз, после ошибки сохранения контекста восстановлен из применённых фактов; inventory stock не рождался повторно.

Raw UI позволяет выбрать QR единицы/коробку/паллету согласно карточке, сохраняет тип сканов и полную pending-команду по пользователю/API. Количество не выводится из числа сканов. JS syntax PASS; физический ТСД/браузер independent acceptance ещё не выполнены.

## SQL
Applied manifest proof12exec/13.693ms/98buf, members lookup12exec/9.652ms/67buf. Решение: сохранить PK/index lookup и ограничения; не добавлять кэш или индекс без необходимости. Раскрытие по агрегатам выполняет отдельный bounded query; для больших реальных партий inventory owner должен измерить full1000 aggregation/20000matrix и при росте заменить N-запросов одним пакетным join. Производственная нагрузка не заявлена проверенной.

Далее: SAP birth-source resolution, invalidation/repacking lifecycle, warehouse nested HU receiving/packing, independent hardware/external acceptance.
Источники: [native](../../db/migrations/2026-10-12_ni061_aggregation_scan/apply.sql), [actual case](../../scripts/case310_aggregate_receive.py), [[retailcase_ni043_sender_manifest_20261010]], [[retailcase_ni061_flexible_unit_mode_20261012]].
