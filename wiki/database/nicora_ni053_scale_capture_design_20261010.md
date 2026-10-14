# NI05.3 — устойчивое показание магазина
Ticket087. Перед реализацией: процесс10_store_receipt, исходная gap analysis и061 weight policy. Подключённого физического драйвера в источниках не найдено; модель/протокол запрошены. Это контракт существующего шлюза, не заявление о подключении весов.

Настроенные весы магазина имеют точный адрес, отдельного действующего RUSERS sender с правом store_scale_ingest, calibration reference/срок, capacity и resolution в KG, optimistic version/active. Настройки только warehouse_settings_edit/CONFIG. Данные присылает связанный sender; права получателя и шлюза разделены.

Packet: ID/устройство/actual departed load/address, KG/GROSS, отсутствие preset tare, свидетельство zero check, устройство measured_at, 5–25 положительных отсчётов с integer offset. Интервал не менее2с/не более10с; max-min не превышает resolution; значение — последний отсчёт (без усреднения/округления). Неисправность/устаревшая калибровка/unstable/future/stale/чужой адрес запрещены. Никакого BARCODE fallback.

Оригинальный принятный JSON/SHA, sender/device version/server received_at и результат сохраняются append-only отдельно от короткой stock транзакции. Exact ID/body replay возвращает прежний capture, иной payload конфликтует. Source actual load/address сверяется в Oracle. Промышленный hardware gateway обязан передавать реальный zero/calibration/sample evidence; synthetic packet не является аппаратной приёмкой.

087 только архивирует измерение; не разрешает WEIGHT_PHOTO до frozen physical box masses, нескольких archived photos и отдельного Root admission. Захват не изменяет P/H/outbox stock и не создаёт government ACK. История не удаляется при замене настроек/повторе.
