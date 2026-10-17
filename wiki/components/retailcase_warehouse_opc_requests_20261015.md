# Складской request/claim OPC producer — 15.10.2026

[[retailcase_opc40200_client]] и [[retailcase_warehouse_scale_gateway_20261015]] дополнены реальным warehouse producer: операторский intent без массы → durable claim identity → native claim → read-only OPC40200 GROSS → atomic local capture/raw bundle → два существующих HTTPS архива. [Инструкция и ограничения](../../docs/integrations/warehouse-opc40200-requests-runtime.md), [CLI](../../tools/warehouse_scale_opc_gateway.py).

Поддерживаются текущие CASE EMPTY_TARE/FINAL_GROSS и явно commissioned sealed weighted PICK. Loose NET не имитируется. Реальный пустой ноль требуется после claim ACK; для заполненного контейнера нужна физическая последовательность снять/проверить ноль/вернуть. Исходная ASM тара не превращается в новый ноль. Старые canonical DTO/raw1.0 сохранены; stock writer не добавлен.

Local claim identity сохраняется до HTTP, потерянный ACK повторяет её неизменно; истечение не создаёт новый ID автоматически. Shared physical lease и native claim ограждают экземпляры. До подключения OPC восстанавливаются capture+raw и выполняется drain; permanent terminal history диагностируется отдельно, без вечной блокировки unrelated requests. Границы auto-reclaim и ручного разбора зафиксированы в инструкции.

22 focused unit/fault/HTTP + shared regression81 PASS;3 encrypted localhost OPC→HTTP цикла PASS, без аппаратных/Oracle утверждений. Native kit и native fixture приёмка находятся у root/inventory. Production API не требует asyncua: зависимость остаётся в tool venv.


Отдельная разрешённая native приёмка EMPTY_TARE CASE1136 завершена: actual production HTTP/native request/claim, encrypted localhost OPC zero→0.5, captureARCHIVED/raw1.0MATCHED; sourceP24/H1/version10 неизменен. [Native отчёт](../../reports/retailcase/2026-10-15/warehouse-weigh-request/opc-empty-native-http.json). Это TEST протокол, физических весов нет; native FINAL/PICK и ASM quantity flow не объявляются принятыми этим проходом.

Отдельное прямое разрешение root выполнено для одного ASM1EA: encrypted TEST OPC BEFORE0.5 → ARMED, AFTER1.5 → canonical CASE_PICK_CONFIRM `WHREQ15.ASM.PICK1136` APPLIED. Исходный UID23/H0, CASE child1/H1; STEP_USE/stock operation/UTC clock/event outbox по одной записи. Exact AFTER HTTP replay сохранил все количества и счётчики. [AFTER](../../reports/retailcase/2026-10-15/assembly-scale/opc1136-after.json), [replay/child proof](../../reports/retailcase/2026-10-15/assembly-scale/opc1136-after-replay.json). Это разрешённая DEV TEST quantity-приёмка программного протокола; физических весов/подбора нет. Лог slow SQL в этом проходе пуст: сохраняются bounded ID-чтения/короткие транзакции, нагрузочная пригодность не заявлена. FINAL и последующая canonical компенсация требуют отдельных разрешений и доказательств.
