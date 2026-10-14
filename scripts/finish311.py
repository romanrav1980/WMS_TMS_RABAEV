from pathlib import Path
import json
out={};p=Path("scripts/source311_marked_case.py");t=p.read_text(encoding="utf-8-sig")
r=Path("scripts/resume311_source.py").read_text(encoding="utf-8")
a=r.index(' idoc=ET.Element(');b=r.index('\n continuation=',a);block=r[a:b]
t=t.replace(' try:\n  import xml.etree.ElementTree as ET',' import xml.etree.ElementTree as ET\n'+block+'\n try:\n  import xml.etree.ElementTree as ET',1)
out[p.as_posix()]=t
page="wiki/database/retailcase_ni061_sap_aggregation_scan_20261012.md"
out[page]="""# Межскладская приёмка: агрегации исходной SAP-поставки
Migration2026-10-12-311-sap-interware-aggregation APPLIED. Приватный RRL_IW_AGG_SCAN теперь разрешает composition из RRL_SAP_TRACE_AGG только через конкретную строку заказа фактической RRL_SAP_PALLET_RECEIPT, APPLIED SAP_RECEIPT stock operation, прежний UID рождения и положительное проведённое количество. NonSAP sender proof310 сохранён.

Каждый код раскрывается в старые physicalunit ID/quantity/raw code. Версия профиля в PROFILES_JSON прежнего code registry должна совпадать с текущей карточкой; это также усилено для nonSAP. BOX/PALLET/UNIT_OR_AGGREGATION проверяются прежним owner, точная матрица/duplicate/foreign/partialset и known regulatory invalidation сохраняются. Нового реестра кодов, родителя товара или quantitywriter нет.

Функциональный дефект прежнего импорта исправлен в integrations/infrastructure/supply_orders.py: setinputsizes задавал xml_raw, отсутствующий в INSERT aggregation. Теперь CLOB code_raw соответствует реальному placeholder. Ранее эта ветка возвращала DPY4008/HTTP500; после исправления реальный XML с двумя составами принят202.

Сценарий311: ARTMAS материал, XML SAPwarehouse supply3/2aggregations, native physicalbirth3/6codes, original autoPUT task completed, existingpick/ST/QC/LOAD/DEPART, interwarehouse2scans→3samephysicalunits. Native late rollback и actualHTTP replay, foreign/missing/duplicate aggregate отказаны. P3H0 в целевом приёмочном карантине, protected20H20. Source311 сначала отклонён до импорта ARTMAS, затем 500bind и SSCC evidence conflict исправлены; исправленный SAPfixture revision2 применён до physicalreceipt. Товар создан ровно один раз, контекст tmp/context311.json сохранён. Ранее ошибочный PALLET source code не зарегистрирован как physicalaggregation.

На freshfixture source311_marked_case содержит ARTMAS beforeSUPPLY и PALLET code=actualSSCC. Никогда не повторять source/resume/caseinitial для имеющегося context311; savedAPI exactreceipt replay допустим. Это не hardware acceptance/realSAPtest/legalACK.

SQL/source policies: exact receipt UID unique index and aggregate order-line PK retained; bounded20000 profile matrix. large1000 aggregation fanout measurement/rewrite backlog inventory from310 остаётся. После case311 требуется измерение актуального SAPproof SQL; не утверждать performance без него.

Источники: [native](../../db/migrations/2026-10-12_ni061_sap_aggregation_scan/apply.sql), [case](../../scripts/case311_aggregate_receive.py), [[retailcase_ni061_aggregation_scan_20261012]].
"""
p=Path("wiki/index.md");out[p.as_posix()]="- [SAP-агрегации межскладской приёмки](database/retailcase_ni061_sap_aggregation_scan_20261012.md):311 exact applied original order-line/versions; actual2scans/3units/6codes; SAP CLOB import fixed.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");out[p.as_posix()]=p.read_text(encoding="utf-8")+"\n- 12.10.2026 311 APPLIED SAP-origin aggregate proof + code profile version check. ActualARTMAS/SUPPLY/native SAPbirth/autoPUT/originalpick-ST-QC-LOAD-DEPART/interware receive3 by2aggscans/rollback/replay/P3H0/protected20/20. Fixed prior DPY4008 wrongxml_raw bind in SAPaggregationINSERT. Existing identities retained; no realgovACK.\n"
p=Path("wiki/runbooks/retailcase_active_work.md");t=p.read_text(encoding="utf-8").replace("Current native310/app310/serv310.","Current native311/app311/serv311.")
t+="\nLatest311 tmp/context311 SAP exact ownsource3 receivedonce, originalPUTfinished/pick-ST-QC-LOAD-DEPART followedinterware3/2aggscans/same6codes. Sourcecontexts310and311 bothcurrentP3H0 receiving quarantine. Neverrerun factories/resumes/initialcases. SAPaggregateINSERT code_raw CLOB fixed. NativeVALID beforeactualcase, currentRoot unchanged. Next ordinary physicalHU consolidation ofactualaccepted/recoveredpieces using existingowners, notduplicateHUregistry.\n";out[p.as_posix()]=t
p=Path("wiki/requirements/retailcase_delivery_v55/execution/active/ni06_1.md");t=p.read_text(encoding="utf-8")
a=t.index("Для отдельных обычных");b=t.index("\n",a)
t=t[:a]+"Целые/частичные обычные и маркированные паллеты, повторная доставка найденного остатка по частям, отмена до приёмки и агрегационные сканы nonSAP/SAP реализованы. Остаток: warehouse вложенные HU между складами, консолидация/переупаковка, повторный физический цикл недостачи одной единицы, независимая/аппаратная приёмка и реальные внешние ответы."+t[b:]
t+="\n311: exact applied SAPreceipt/order-line aggregate origin/currentsavedcode versions, actual2scans→3units/6oldcodes. Исправлена прежняя SQLCLOB binding ошибка imports aggregation.\n";out[p.as_posix()]=t
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");j=json.loads(p.read_text(encoding="utf-8"));inc=next(x for x in j["increments"]if x["id"]=="NI06.1");inc.setdefault("implementedSlices",[]).append("311 actual SAP aggregation origin/order-line/stock proof -> original unit codes/current profile versions; actual supply XML binding fixed")
inc["remainingScope"]=["aggregation invalidation/repacking lifecycle","warehouse nested HU receiving and physical consolidation into upper place","true recurrent physical-loss cycle","independent acceptance/hardware/current real ERP and government ACK"];out[p.as_posix()]=json.dumps(j,indent=2)+"\n"
root=next(Path(".").glob("*/NI08.1/178_container_cell_index.md")).parent.parent
out[(root/"NI06.1/311_sap_aggregation.md").as_posix()]="# Qwen311\nExact original SAPreceipt STOCK_OPERATION_ID APPLIED/SAP_RECEIPT, own order-line, physicalbirthUID and quantities; foreignorder, no appliedbirth, missing/duplicate/overlap and changedprofileversion fail. Actualcontext311 alreadyP3 inquarantine: onlysavedHTTP replay, do not rerun factory/resume/nativeinitialrollback. Fresh source mustARTMASfirst/PALLET aggregate code=same physical SSCC. RealgovACK remainsfalse. Confirm supplyXML withaggregateUNITS_JSON/code_rawCLOB doesnotDPY4008; duplicate senderMessage+exactXML returns cached source without stock. Independentbrowser/hardware separate.\n"
print(json.dumps(out))
