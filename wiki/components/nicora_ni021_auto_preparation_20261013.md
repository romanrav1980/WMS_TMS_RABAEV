# NI02.1 — автоматическая подготовка существующей СТ

Разрешена владельцем13.10.2026: свежего SQLнет, реализовать самостоятельно. Владелец fulfillment; создание ORDERS/SBORKA/fulfillment остаётся LegacyPreparation, одна source transaction. Остатки, резерв, задания отбора и назначение рейса здесь не проводятся.

## Фактический исходник
Read1110: RRL_COMPL_SEQ существует (ARTICUL/WARE_ID/SEQ/SEQ_GROUP), исторической RRL_COMPL_SEQ_GR нет. Архив2011 задаёт группы/порядок, массу и объём коробок, но содержит DELETE/COMMIT/ROUND вместимости. Эти операции не восстанавливаются. Паллетный каталог DEFAULT_WEIGHT_KG нельзя без доказательства считать максимальной грузоподъёмностью.

## Контракт нового расчёта
Автопредложение строится из текущего принятого SAP-заказа, действующего календаря/deadline/адреса, карточек SKU, wholepack/norm/dimensions/mass и RRL_COMPL_SEQ. Группы и порядок существующей карты сохраняются; отсутствующая карта использует исторический group101 и стабильный артикул в конце группы. Противоречащие карты не чистятся автоматически.

Из-за отсутствия текущей таблицы ограничений обязательные пределы задаются явным входом расчёта: максимальная масса товара (кг), объём товара (м³), число плановых мест ≤100. Нули/default950kg/1.728m3 и выдуманная масса тары не подставляются. Один и тот же набор пределов становится частью сохранённого запроса. Это ограничение плана товара, не подтверждение фактической грузоподъёмности тары/машины. Справочник действующих профилей можно добавить отдельным инкрементом, без скрытого seed.

Расчёт точный Fraction/Decimal: коробки целые, capacity всегда floor; коробка, не помещающаяся по заданным пределам или норме, отвергается. Внутри одной группы можно смешать хвосты разных SKU, пока выполняются масса/объём/сумма долей норм ≤1. Между группами смешивания нет. Последовательность стабильна по исходной карте. Перебор ограничен1000SKU/100мест; исходная потребность по каждому SKU сохраняется точно, строка legacy одного SKU на месте единственная. Объём считается из действующего DIMKOR в миллиметрах (article_logistics/тест271:40cm→400mm), произведение переводится вм³ делением на10^9. Архив2011 не доказывает единицы действующей карточки; первоначальное предположение оcm исправлено до runtime записи. Трёхмерная геометрическая укладка/температурная совместимость без соответствующих данных не объявляются доказанными.

Preview только читает текущий snapshot и возвращает source_signature, состав, нормативные показатели и ограничения. Запуск требует сохранённый operation_id, исходную подпись предложения и те же пределы. Под текущими source/config locks он проверяет роль/склад, сначала ищет существующий результат этого auto-request, затем перечитывает источник/карты и сравнивает подпись. Повтор после изменения справочника возвращает старый подтверждённый результат; другое содержимое стемжеID или уже подготовленный источник другой командой отклоняется. Никаких вложенных Root/commit и удаления прежней СТ.

## Актуальные случаи
2047/WARE9807 ACCEPTED, PREPARATION_HASH NULL, deadline02Nov2026 — потенциальный существующий позитивный источник. 2044 ACCEPTED, но отсутствуют нужные logistics;2045REJECTED.2046/2048 уже подготовлены и не перераздаются. Readiness2047/sequencecard/replay/rollback/bodyconflict и UI ещё ожидают. Изменение источника или конфигурации после preview должно отказать без части заказа/СТ/FF. Native quantity engine не меняется.

1117: расчёт/API/shared writer/UI реализованы; live позитив/повтор/конкуренция ещё ожидают. Command блокирует source/config, затем RRL_COMPL_SEQ SHARE WAIT3 (включая отсутствующие строки), затем карточки SKU в стабильном порядке, затем legacy ORDERS. Manual использует тот же порядок; cached result возвращается до блокировок справочника. Короткое глобальное ограждение sequence требуется из-за отсутствия уникальной карты/version; владелец fulfillment, замена на версионированный scope при росте contention.

1125: actual isolated2135 SAP_2135/2places18A+6B/12B, exact18EA/3boxes/12kg perSKU, outerrollback/stale/race/replay/conflict/currentHTTP+UI PASS. ProtectedP20H20. Report30/screen41; source2047 remains unprepared/badnorm, oldfixturesunchanged. Preview signature now includes limits too; saved original1118 receipt is returned unchanged. Current read-only UI displays original receipt stats; new receipts additionally save explicit planned_pallets. NoDDL; older archive remains evidence. SQL8.286ms/75.57 and2.603ms/14.5 retainboundedreads/noindex, ownerfulfillment; globalmetadata fences versioning backlog.

1131: prepared UI bridge savedauto→selected order/sapAssignment/current preparation receipt→existing assignendpoint. Explicit readonly preflight uses existing native capacity/type/source service; not operational/departure admission. Runtime pending; no second order/tripmapping.

1136: bridge1131–1134 currentreceipt→existingassignment/read-onlypreflight delivered. Already-prepared originaleditor hidden (notoriginaldemand-as-layout); oldprepare blockedbyauto/manual pending. Actual33571 prospective2places/24kg CHECKED, noassignmentwrite. Report32/screenshot43intermediate,final44 unavailableChrome. Projectmap subprojects/nicora.md introduced.

1147: prepared warehouseSKU temperature ranges added to same readiness/source_signature. Auto places preserve common known range, reject invalidrange, separate incompatible knownSKU and known-vs-unknown, while existingunknowns mayformnormativeplanwithoutphysicalthermalclaim. Temperature sourcedexistingRRL_RECEIPT_SKU_RULE; numericvehicle/tempfacts stillseparate. Runtimepending/newpurecases1147 pending.

14.10.2026/1148: layoutstrategyV2 distinguishes temperature-compatible packing; source existingSKU ranges/native readonly2047 fields observed, pure1147 casesPASS/architecture7000cycles76debt. UI shows range/unknown perplace. V1savedresults immutable, oldunprepared previews require reread. APIlatestV2 load/replay pending, noDDL/newphysicalfixture.

1158: API V2 loaded; original1118 savedV1 repeat/resolveHTTP1121 PASS, no recalc/new source; pure1147 andJS1122 PASS. Report34 records thermal compatibility.
