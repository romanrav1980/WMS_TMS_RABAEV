# NI07.2 — повторное ожидание того же CASE

Migration2026-10-13-006-ni072-case-wait-identity PREPARED. Actual977 повторно переназначил retained CASE1129 на следующий плановый день; новое WHT insert00001 refused before stock move.

Live979: RRL_WAREHOUSE_TASK_U2 — unique INDEX, не constraint. Keys: TASK_SOURCE, NVL(SOURCE_TASK_ID,-1), NVL(SOURCE_MOVEMENT_ID,-1), TASK_TYPE, special SAP UID / otherwise parent ID. FirstCASE implementation used CASE id as SOURCE_TASK_ID, поэтому второй MANUAL/PUTAWAY для того же CASE конфликтовал с прошлым завершённым заданием.

New CASE waiting uses SOURCE_TASK_ID=TASK_ID, как прежняя flat waiting branch. Original CASE remains explicit CASE_TASK_ID in immutable WAIT_PLAN; source read/command validates that exact CASE and current WHT. Two earlier dev records retain their original source ID and remain replay-compatible. No PARENT_TASK_ID is invented for sequential full movement: it is not partial residual quantity. One-time bounded dev sequence catchup past observed MANUAL PUTAWAY maxsource1130 prevents collisions with those earlier CASE ids; no rewind/copy/history rewrite or stock change. Subsequent tasks use the monotonic self ID. Open CASE task detection uses authoritative plan CASE_TASK_ID plus carrier identifier.

Capture980/SHA/paired code rollback; unused numeric gaps are normal retained allocation, not reversed. Need compile and retained977 planning/physical finish through current one FF-version writer974. FullNI07.2 still open. Previous QC signature expectation in975 harness was wrong: whole movement preserves goods composition hash; actual976 currentCASE3/FF3 with same signature is correct. Prior claims about automatic invalidation of every old QC approval on any relocation were unproven and are superseded by current-policy evidence; no oldapproval fixture was tested.

## Checkpoint984

# NI03.3 / NI07.2 — связанный CASE и повторное ожидание

974 и981 APPLIED/VALID RABAEV/orcl. Малый RRL_STOCK_CASE_BIND_MOVE дополняет существующую CASE_CARRIER_MOVE: ST/FF ресурсы объявляются до блокировок, исходная привязка и hash оригинального состава проверяются после них. FF picked-content version обновляет этот единственный владелец в транзакции движения; waiting finisher только подтверждает полученную версию. Количество, единица, состав и старые подписи отбора сохраняются.

Actual975/976: retainedCASE1129/12EA/H12 из ожидания в контрольную system-cell, CT3=FF3. Native positive rollback сохранялCT2/FF2/currentcell; public command commit/replay прошёл. Последний975 harness ожидал изменения товарного hash и ошибся: whole-place relocation сохраняет состав, поэтому hash прежний, currentcaseversion3.976 исправляет интерпретацию. Автоматическое аннулирование каждого старого QC approval на любое перемещение не доказано и не обещается; текущее правило QC определяет допуск. Это уточняет прежнее непроверенное предположение на страницах953/974.

Повторное ожидание977 сначала упёрлось в старый unique INDEX RRL_WAREHOUSE_TASK_U2 (source/tasktype/sourceMovement/parent), источник CASE_ID в WHT не позволял второе движение.981 использует self SOURCE_TASK_ID=TASK_ID, как старое flat-waiting задание; настоящийCASE_ID хранится в immutable WAIT_PLAN. Первые1110/1111 сохраняют историческийSOURCE_TASK_ID и replay совместимость. Одна ограниченная dev-sequence catchup выше ранее существовавшегоmax1130 оставляет числовые gaps; запас/история не переписываются. PARENT_TASK_ID не используется как фиктивный residual.

Actual982: тот же CASE1129 изконтроля снова переназначен оригинальной TMS на будущийдень, зарегистрирован новый WHT1132 с self-source1132, DONE1CASE/SYNCED/journal12EA/P12H12/CT4=FF4. Исходные pick facts сохранены; exact replay тотже result. Второй retainedCASE1130 остаётсяP8H8/CT2FF2 вожидании. Фабрики, старые SAP и protectedWARE не пересоздавались. ПолныйNI03.3/NI07.2 не закрыт.

Source captures973/980/SHA/pairedrollback; no DBcopy. Rollback не испытан;981 rollback не откатывает sequence gaps и требует отдельно учитывать уже созданные self-source планы. Native current USER_ERRORS[]/INVALID[]. Latest broad gate968 PASS, subsequent nativecompile/current targeted cases PASS; поздниеUI/backendfamily изменения покрытыHTTP971, fullgate не повторялся.

SQL983 direct binding0.268–1.252ms/1.6–21.9buf; historicalglobalfulfillmentquery17.399ms145buf. Решение inventory owner: keyed current ST/FF lookups и bounded200lots остаются, без нового индекса; это не production load acceptance. Report17 сохраняет точные источники975/977. Далее — несколько самостоятельных CASE однойСТ, каждый с собственным immutable physical plan.
