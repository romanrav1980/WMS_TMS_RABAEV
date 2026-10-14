# NI03.3 — исполнение заказа при перемещении связанного CASE

Migration2026-10-13-005-ni033-case-bound-move, PREPARED before apply. Capture973 actual CASE1129/1130 inwaiting/currentCT2 and boundFF2. Current CASE_CARRIER_MOVE changes CTversion/currentcell, but its generic branch does not advance boundFF version. Waiting helper953 does; this change makes the existing physical mover the one owner of the version relationship.

Small metadata helper RRL_STOCK_CASE_BIND_MOVE, accessible only to existing CASE mover. Unbound CASE unchanged. Bound CASE requires original ST sameWARE/unloaded, exactly one original PICKED fulfillment/customer order/carrier/current version/original composition. Root declares ST/FF row locks; freezes material binding fields and composition hash, revalidates after locks before moving actual lots. After old TRANSFER_CORE and CT movement, FF picked content version is advanced in the same transaction. Original quantity/UOM/composition/pick stamps untouched. Waiting finisher changes from second FF updater to proof of that same new version.

Old QC facts remain historical; current admission uses current composition/version. No new stock writer, binding engine or shipment is created. Current role/WARE before replay remains existing CASE_TASK_ACCESS (+WHT access for waiting). Captured sources/SHA/paired rollback; no DB copy. Rollback not tested. Need live compile + actual forward movement of retained955/966, no source rebirth; no full sprint closure claimed.

## Checkpoint984

# NI03.3 / NI07.2 — связанный CASE и повторное ожидание

974 и981 APPLIED/VALID RABAEV/orcl. Малый RRL_STOCK_CASE_BIND_MOVE дополняет существующую CASE_CARRIER_MOVE: ST/FF ресурсы объявляются до блокировок, исходная привязка и hash оригинального состава проверяются после них. FF picked-content version обновляет этот единственный владелец в транзакции движения; waiting finisher только подтверждает полученную версию. Количество, единица, состав и старые подписи отбора сохраняются.

Actual975/976: retainedCASE1129/12EA/H12 из ожидания в контрольную system-cell, CT3=FF3. Native positive rollback сохранялCT2/FF2/currentcell; public command commit/replay прошёл. Последний975 harness ожидал изменения товарного hash и ошибся: whole-place relocation сохраняет состав, поэтому hash прежний, currentcaseversion3.976 исправляет интерпретацию. Автоматическое аннулирование каждого старого QC approval на любое перемещение не доказано и не обещается; текущее правило QC определяет допуск. Это уточняет прежнее непроверенное предположение на страницах953/974.

Повторное ожидание977 сначала упёрлось в старый unique INDEX RRL_WAREHOUSE_TASK_U2 (source/tasktype/sourceMovement/parent), источник CASE_ID в WHT не позволял второе движение.981 использует self SOURCE_TASK_ID=TASK_ID, как старое flat-waiting задание; настоящийCASE_ID хранится в immutable WAIT_PLAN. Первые1110/1111 сохраняют историческийSOURCE_TASK_ID и replay совместимость. Одна ограниченная dev-sequence catchup выше ранее существовавшегоmax1130 оставляет числовые gaps; запас/история не переписываются. PARENT_TASK_ID не используется как фиктивный residual.

Actual982: тот же CASE1129 изконтроля снова переназначен оригинальной TMS на будущийдень, зарегистрирован новый WHT1132 с self-source1132, DONE1CASE/SYNCED/journal12EA/P12H12/CT4=FF4. Исходные pick facts сохранены; exact replay тотже result. Второй retainedCASE1130 остаётсяP8H8/CT2FF2 вожидании. Фабрики, старые SAP и protectedWARE не пересоздавались. ПолныйNI03.3/NI07.2 не закрыт.

Source captures973/980/SHA/pairedrollback; no DBcopy. Rollback не испытан;981 rollback не откатывает sequence gaps и требует отдельно учитывать уже созданные self-source планы. Native current USER_ERRORS[]/INVALID[]. Latest broad gate968 PASS, subsequent nativecompile/current targeted cases PASS; поздниеUI/backendfamily изменения покрытыHTTP971, fullgate не повторялся.

SQL983 direct binding0.268–1.252ms/1.6–21.9buf; historicalglobalfulfillmentquery17.399ms145buf. Решение inventory owner: keyed current ST/FF lookups и bounded200lots остаются, без нового индекса; это не production load acceptance. Report17 сохраняет точные источники975/977. Далее — несколько самостоятельных CASE однойСТ, каждый с собственным immutable physical plan.
