from pathlib import Path
import json
out={}
out["wiki/components/nicora_ni011_artmas_sparse_units_20261011.md"]="""# Частичное изменение MARM не меняет вложенность на1
272 domainarticle_units отделён от mapper. MARMRTX явно отмечает изменяемые коэффициенты и EAN; отсутствие flags коэффициента означает сохранить известное отношение, не default1. Изменение коэффициента требует NUMERATOR иDENOMINATR; новый альтернативный UoM без доказанного отношения отвергается. Base identity проверяется native UOM configuration. Повторные UoM/flags, unsupported explicitEANclearing, invalid/oversized rationalcomponents отвергаются. Fraction exact numerator/denominator<=1e9, optional finite decimal representation<=9 без округления.

ArticleMasterApply читает previousUNITS_JSON под прежним native CONFIGX и merge поuom сохраняет неупомянутые единицы/прежние EAN. Полный нормализованный merged список публикуется в существующий RRL_STOCK_UOM_CONFIG, новые коэффициенты не вычисляются второй проводкой. Пустой unit patch оставляет metadata unchanged. Маркировка, остатки и исходный SAP заказ не меняются.

Actualsame271 QPOOL SKU sparse MARMBOX LENGTH40CM/LENGTHX безNUM/DEN: BOX24 и отсутствующий в deltaEA сохранены, старые mm/kg/count все совпадают. Новый CS/LENGTHX без зарегистрированного коэффициента отвергнут, wholecard/source metadata rolledback, originalraw inboxERROR сохранён. Source2046 qty48/P20H20 unchanged/no Root event. Purepatch проверил неполную паруNUM/DEN и unknownaltUoM. tmp/context272.json хранит own successful/failedinbox; не повторять создание новыхIDocs ради тех же assertions.

Архитектура602/0cycles76. SQL actual271/272: originalSBORKA_ROWS_ADD4 average51.532ms3 (другой cached signature7.095ms4), innerINSERT20.295ms7/ORDER_ROWS11.667ms2; metadata writes не в longest. DiagnosticCOUNTbyDOCID92.53ms2 — только авторская сверка: в будущих runtime read paths использоватьPALLET_UID/явныеIds, не глобальныйDOCIDscan. OwnerNI02: при реальных100паллетах профилировать существующий legacy row writer/триггеры, при росте применять boundedbatch вместо повторных N+1; сейчас сохранить existingwriter и exactQty, не вводить новыйwriterили спекулятивный индекс. Размер/массаконтракт271 остаётся предполагаемымSAPprofile, realXMLnotcertified.

Следующий факт: supply/store import всё ещё использовали Decimal(u.ratio); для не конечного рационального отношения это None и неверный fallback/ошибка. Требуется переиспользовать опубликованные native рациональные политики и RRL_STOCK_MATH.convert_exact, а не новое математическое ядро. Это ещё не закрыто272.
"""
for path,line in [
("wiki/index.md","- [Частичные изменения единиц ARTMAS](components/nicora_ni011_artmas_sparse_units_20261011.md):272 preserve ratio/omittedUoMs/EAN, unknown unproven unit atomic rejection."),
("wiki/log.md","2026-10-11:272 MARMRTX noNUM/DEN no longer default1; domainexactrationalpatch/metadata merge/native existingUOMpublish. Actualsame271 BOXlengthX kept24+EA/mmkg unchanged/newCSwithoutconversion rejected/cardmetadata rollback/inboxERROR/source48/P20H20. Architecture602cycles0debt76. Originallegacyrowwriter51.532ms3/inner20.295/ORDER11.667 retainboundedexistingwriter ownerNI02; diagnosticDOCIDscan92.53ms useUIDids inruntime, don'tnewindex forauthorcheck. Next sourceimportnativeexactrational math."),
("wiki/requirements/nikora_delivery_v55/execution/active/ni01_1.md","11.10.2026:272 sparse MARMRTX coefficient/EAN preservation/mergedomittedunits, exactrational metadata andexistingnativepolicy; actualBOX24+EA kept/newCSunproven refused atomic/no qty. Source nonterminatingrational conversion remains separate nextgap."),
("wiki/runbooks/nicora_active_work.md","Latest272 appnotyetserverrestart/native270; domainarticle_units +merge metadata. tmp/context272.json hasownsuccessfulsparseBOXlengthX/noRatio ->BOX24+EA retained andfailednewCSunproven ERROR. Source2046/48 untouched. Next273 source imports native exactrational conversion/sharedCFG/current supply actorWare; don'tdupIDocs. Nativebundle270 needsgenerate afternextscope patch.")
]:
 out[path]=Path(path).read_text(encoding="utf-8")+"\n"+line+"\n"
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json");j=json.loads(p.read_text(encoding="utf-8"))
next(x for x in j["increments"]if x["id"]=="NI01.1").setdefault("implementedSlices",[]).append("272 sparse MARMRTX ratio/EAN preservation/old unit metadata merged/exact existingnativeUOMpublish/unknownnewunit refused atomic")
out[str(p)]=json.dumps(j,ensure_ascii=True,indent=2)+"\n"
root=next(p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md"))
out[str(root/"NI01.1"/"272_sparse_units.md")]="# Qwen:272 — частичные единицы\nMARMBOXdimensionX безNUM/DEN сохраняет зарегистрированныйBOX24 и omittedEA/EAN. Не применять default1, не удалять отсутствующиеunits изmetadata. RatioX требует обаNUM/DEN, duplicateUoM/flags и явноеEANclearing безконтракта отвергать. UnknownnewCSwithoutcoefficient ->whole apply rollback/rawinboxERROR, прежние card/unitpolicy/sourceqty intact. Fraction num/den<=1e9 exact, nonterminatingdecimalratioNone сохраняетrational. SourceStore/Supply conversionNativeMath still273nextgap, не выдавать272заегоисправление. Existingcontext272 не создаватьзаново. Legacyrowwriter longest51ms/profile boundedbatch if100pallets; diagnosticDOCIDscannotruntime proof.\n"
print(json.dumps(out,ensure_ascii=True))
