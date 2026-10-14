# Qwen: NI05.3/087 — оборудование и архив показания
Читать wiki/database/retailcase_ni053_scale_capture_20261010.md. Это синтетический gateway contract; отдельное физическое испытание требуется после получения модели/протокола весов.

Создать только собственный sender RUSERS/группу через действующую rights admin, право store_scale_ingest. GLOBAL_ADMIN не может быть device sender. Настроить device/address/version/active/calibration/limit/resolution. Submit5–25 samples, период2–10с, последние10KG, min-max≤resolution, KG/GROSS/no preset tare/recent zero. Проверить immutable original canonical JSON/hash/first server time/actor/policy, last sample вместо среднего.

Exact capture replay после изменения active не создаёт новый capture и не обновляет freshness; другой payload конфликтует. Неверный sender/address/недостаточное право/неактивный sender; stale/future/expired calibration/несуществующий departed load; zero false/null/zero вне±resolution; float quantities/нулевой вес/дискретность/неупорядоченные offsets/недостаточное окно/unstable/capacity/oversize>32000 bytes — отказы. Signed zero в пределах resolution допустим. Raw package bypass должен сохранять обязательные проверки.

Receiver list/read ограничен своим текущим магазином и store_receipt_confirm; gateway не получает receiver права автоматически. list50/старый key recovery; direct update/delete capture запрещены. Replay audit false, binary photo traffic cap4MiB не сломан новым JSON cap. P/H/receipt remain unchanged.

Разделить реальный HTTP/Oracle PASS, browser UI evidence и физический аппаратный протокол. Не выдавать DEV calibration за действующую поверку. Retire only own sender/device, сохранять immutable evidence, крупнейший SQL и решение записать в wiki.
