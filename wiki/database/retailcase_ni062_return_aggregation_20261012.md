# NI06.2: агрегатные сканы при передаче и приёмке возврата

Migration2026-10-12-619-return-aggregation-custody подготовлена после чтения живых RRL_STORE_RETURN_UNIT_CORE, RRL_STORE_MARK_CORE и общего RRL_IW_AGG_SCAN. Новый реестр маркировки, товарное ядро и складское дерево не создаются.

В прежнем custody_proof зарегистрированная агрегация раскрывается общим resolver в прежние hashes индивидуальных кодов. Затем прежний валидатор сверяет ровно утверждённые физические ключи/профили/количества/партии/версии. BOX/PALLET-only профили не принимают прямые единичные сканы; UNIT_OR_AGGREGATION допускает предусмотренные способы. Неполный/чужой/дублирующий состав отклоняется. Непромаркированный товар не получает чужие агрегатные сканы.

Сохраняются ограничения общих1000 агрегатов/10000 единиц/20000 профилей-сканов, current profile/level/version, registered/applied origin и regulatory invalidation. Старый агрегационный код не разрешается автоматически после изменения current UID: это прежний инвариант вскрытия/перепаковки. Новый жизненный цикл после возвратного UID остаётся отдельным сценарием, не имитируется.

620: lifecycle invalidate держит существующий CONFIG.WAREHOUSE X6, warehouse stock commands используют общий policy fence; повторная проверка native custody_proof после canonical wait сохраняется. Нет второго исполнения quantity и обхода существующей конфигурационной сериализации.

Парные исходники захвачены до изменения; rollback отказывает после подтверждённых return aggregation facts. Root ledger JSON называется CANONICAL_REQUEST (проверен live), не PAYLOAD_JSON. Применение/контракты UI/конкретный original aggregate возврат ещё предстоят.

Дополнительная сверка: REUSE уже проверяет исправность полной коробки warehouse.complete_good_boxes, коробочный EAN/количество, исходные SKU/партия/срок и массы/кодовую матрицу. Не строить второй общий механизм инспекции для этих уже выполненных проверок. Операторское подтверждение не является реальным лабораторным или аппаратным доказательством.

## Checkpoint629: реализован путь коробки, ограничение паллеты сохранено

619/626 применены в dev RABAEV/orcl; USER_ERRORS/INVALID пусты (627). Shared resolver подключён к handover, driver pickup и warehouse receive. API621 принимает aggregation_scans через публичный inventory-контракт, пустой новый список удаляется для старого canonical request.

622/623/624: собственная SAP-поставка3EA, прежняя ST/LOAD/DEPART/магазин, текущие профили CRPT UNIT + EGAIS BOX-only. Возврат прошёл согласование/SAP/план/передачу/независимую подпись водителя/полную исправную коробку/приёмку/PUT. Прямой unit fallback для BOX отвергнут. Неверное количество коробок отвергнуто. Точные receive/PUT повторы сохранены. 627 read-only подтверждает P3/H0, 3 прежних физических ключа, 6 прежних кодов, одну передачу и удалённого тестового пользователя. Не запускать исходные factories622/623/624 заново.

Важное уточнение исходного предложения: RRL_STOCK_STORE_RETURN_REC_CMD требует fresh PALLET_IDENTIFIER. Поэтому PALLET aggregation старого контейнера не должна подтверждать новый контейнер. 626 явно отклоняет её RETURN_PALLET_AGGREGATION_REQUIRES_PRESERVED_CONTAINER_IDENTITY. Полный PALLET-only возврат ещё не реализован; нужен явный сценарий сохранённой идентичности или зарегистрированная новая агрегация. Прежний PALLET-код не разрешается автоматически после перепаковки/изменения UID. BOX-путь не объявляется доказательством PALLET-пути.

629 UI: ReturnMarkPanel в прежней ReturnCustodyPanel и return-mark-draft.js на прежней складской странице. Режимы UNIT/BOX/UNIT_OR_AGGREGATION, никаких прямых unit fallback для BOX. Черновик связан с API/пользователем/исходником/составом; сохранённая команда использует прежний механизм точного повтора. PALLET-only блокируется с понятной причиной. Сервер остаётся валидатором полного состава.

SQL627: lookup aggregation0.510ms/5.43buffers; count2.249ms/27.57buffers; insert2.656ms/29buffers. Решение: сохранить текущие indexed registered-origin queries и ограничения1000/10000/20000; отдельный индекс не оправдан этим dev случаем. Это не нагрузочное подтверждение миллионов операций. Native VALID и architecture676/0cycles/76debt; changed frontend typecheck PASS. Нет настоящего государственного ACK или независимой приёмки.

Checkpoint648 supersedes blanket PALLET rejection629 for exact unchanged whole original UID only. Native639/helper/current receipt and actual643 PALLET+BOX complete P3H0; other identity/repacking stays blocked. [[retailcase_ni062_preserved_pallet_20261012]].
