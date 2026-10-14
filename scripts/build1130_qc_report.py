from pathlib import Path
import json
f={}
report="""# 31 · Контроль по физической этикетке CASE

Физическая этикетка CP553000000001131 и внутренний CASE:1131 теперь открывают действующий источник CASE.QC.ST:4bb85f1f15:1131. Один read-only snapshot: свежий RUSERS/права, точные равенства по PALLET_UID/CASESSCC/CASEID, native assert_identifier для всех кандидатов. Несколько допустимых разных источников дают конфликт; неизвестный/чужой источник отклоняется. UNION ветви разделены для существующих индексных путей; выдача ограничена3.

GET возвращает canonical shipment_identifier и requested_identifier при преобразовании. Интерфейс сверяет предъявленный идентификатор, принимает canonical и сохраняет его до PLAN/SCAN/WEIGHT. Сохранённый запрос никогда не переназначается по изменившейся физической этикетке. Вызовы native QC/stock executor и POST контракты остаются прежними.

Actual1127 +HTTP1128: три формы идентификатора дают тот же CASE1131v20/readyfalse. Несуществующий actor/источник отклоняется. JS1129 доказывает canonical freeze/repeat и отсутствие автоматического PLAN; JS1097/1102 сохраняют текущие проверки ответа/восстановления. Browser42 открывает контроль по физической этикетке и показывает внутренний постоянный источник/текущийv20. QC POST/сканирование/вес/допуск в этом случае не выполнялись; missingweightpolicy не обходится.

P20/H20 на защищённом складе5062399 сохранены. Oracle DDL/данные не менялись. Architecture699/0cycles/76debt PASS.

SQL1127: alias query11.433ms/17buffers (другой cursor17.32ms/10). Решение владельца inventory: точные equality UNION paths и bounded3 сохранить, дополнительный индекс по этому случаю не требуется. Это единичное измерение, не нагрузочная мощность. ИсточникиHTTP/read-only текущие; real scanner и независимая приёмка отдельно.

[Скриншот42](screenshots/42-qc-physical-case-label.png).
"""
f["reports/retailcase/2026-10-13/31-qc-physical-label-report.md"]=report
f["reports/retailcase/2026-10-13/31-qc-physical-label-evidence.json"]=json.dumps({"native":json.loads(Path("tmp/read1127_qc_alias.json").read_text(encoding="utf-8")),"http":json.loads(Path("tmp/http1128_qc_alias.json").read_text(encoding="utf-8"))},ensure_ascii=False,indent=2)+"\n"
p=Path("reports/retailcase/2026-10-13/index.html");s=p.read_text(encoding="utf-8").replace("</main>","<article><h2>31 · Контроль по этикетке CASE</h2><p>Физический штрихкод открывает существующий QC; команды сохраняют постоянный источник.</p><a href=\"31-qc-physical-label-report.md\">Отчёт</a><img src=\"screenshots/42-qc-physical-case-label.png\" alt=\"Контроль текущегоCASE20 открыт по физической этикетке\"></article></main>");f[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/outgoing-quality.js");s=p.read_text(encoding="utf-8").replace("Идентификатор СТ <input data-id","Идентификатор паллеты / CASE / СТ <input data-id");f[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/warehouse-tasks.html");f[str(p)]=p.read_text(encoding="utf-8").replace("outgoing-quality.js?v=20261013-1129","outgoing-quality.js?v=20261013-1130")
f["задания на проведения тестов/NI02.1/2026-10-13-автоматическая-подготовка-СТ.md"]="""# Qwen · NI02.1 · Автоматическая подготовка СТ

Ограниченная независимая приёмка реализованного инкремента. Не запускать глобальные прогоны, не очищать историю/остатки, не пересоздавать context1118 или fixtures2044–2048/987. Read wiki/index.md и components/retailcase_ni021_auto_preparation_20261013.md. Отчёт сохранять в reports/retailcase/2026-10-13, факты отличать от допущений.

1. На сохранённом источнике2135/WARE9807 проверить существующую SAP_2135/ORDERS48470: два места; по18EA/3boxes/12kg SKUQAUTOc0c2a00c0bA/B. Получить repeat и resolve с исходным body из tmp/context1118.json; не генерировать новыйbody/ID. Повтор не создаёт новые ST/FF/запас.
2. Source2047 только прочитать/preview с положительными пределами: норма1 меньше коробки24 должна отказать409. Не исправлять историческую карточкуQPOOL ради зелёного теста.
3. Новый позитивный UI сценарий разрешён только на собственном изолированном источнике: нормы/целые коробки/группы/масса/размеры вmm. Через UI рассчитать18A+6B/12B при16kg/.096m³, сохранитьСТ и убедиться в source-demand exact сохранности и FFPLANNED0. Не трактовать план как физический запас.
4. Пределы/текущий исходник входят в signature. Изменить собственную текущую карточку между preview/run: отказ без части ORDERS/SBORKA/FF/receipt. Любые тестовые изменения собственногоSKU вернуть; не менять чужие настройки.
5. На собственном источнике проверить две конкурирующие команды: однаСТ, одинрезультат, второйконфликт; outerrollback и неизвестный исход со saved resolve. Не выполнять несколько begin_source внутри уже dirty callerTX.
6. UI: pending сохраняется доPOST; ошибочный ответ/другая вкладка/смена пользователя оставляютraw; retry неизменногоbody; malformedraw блокируетновыеwrites, GETдолженуспетьпередarchive/deletion. ОтказGET/сменаscope сохраняютraw. Ручнаяформа не обходит pendingавто.
7. Математика: разныегруппы не смешиваются, отсутствиеSEQ→group101 stableSKU; duplicateSEQ отказывается; oneboxoversize, ненулеваяwholebox норма, floorlimits, max100/1000SKU. Объём DIMKORmm/10^9. Смешение — нормативный план, не доказательство3D/температуры/грузоподъёмноститары.
8. МаркированныеSKU остаются планомбезфиктивныхQR/внешнихACK; действующие laterpick/QC должны требовать текущие WMSprofiles и фактический состав. Несколькопрофилей не увеличивают количество.
9. После собственного meaningfulcase снять slowSQL, явно выбрать bounds/index/rewrite/backlogowner; приложить реальныйскриншот. Результат independent PASS/FAIL/NOT_EXECUTED; не объявлять production или все18спринтов принятыми.
"""
p=Path("wiki/components/retailcase_ni051_control_label_20261012.md");f[str(p)]=p.read_text(encoding="utf-8")+"\n1130: read1127/HTTP1128 actualphysicalbarcode+CASE:1131+logical allcurrentCT20/readyfalse, unknownactor/source denied; UI1129 canonicalfreeze/retry/noautoPLAN PASS; screenshot42/report31. P20H20 unchanged/noDDL/noQCPOST. SQL11.433ms17buffers/17.32ms10 bounded3/UNIONexact retain/noindex ownerinventory. Full independent/weights/scanner acceptance not claimed.\n"
p=Path("wiki/index.md");f[str(p)]="- [QC physical label delivered1130](components/retailcase_ni051_control_label_20261012.md): actual CASE barcode/CASEID/current20/canonical freeze/report31/screen42/no stock effect.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");f[str(p)]=p.read_text(encoding="utf-8")+"\n- 2026-10-13 /1130: physicalCASE→existingQC delivered readonly1127/HTTP1128/UI1129 canonical source frozen, current1131v20/readyfalse/P20H20. Report31/screens42, newQwen NI02.1 task prepared (not executed). SQLbounded3 equalityUNION retained/noindex ownerinventory. APIserv1127 current, allfullsprints remain open/noGitHub.\n"
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");x=json.loads(p.read_text(encoding="utf-8"));x["planRevision"]=53
for i in x["increments"]:
 if i["id"]=="NI05.1":i["implementedSlices"].append("1126–1130 physicalCASE barcode/CASEID -> existing native QC current identifier in readonly snapshot; UI canonical request freeze/read/report31/screen42")
x["currentSprint"]="NI02.2";x["currentSprintMeaning"]="Continue remaining current source/transport constraints via existing assignment after automatic preparation delivered"
f[str(p)]=json.dumps(x,ensure_ascii=False,indent=2)+"\n"
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.md");f[str(p)]=p.read_text(encoding="utf-8").replace("**Revision 52,","**Revision 53,")+"\nRevision53/1130: physicalCASE label→existingQC currentsource delivered/report31/screen42; noQCPOST/nativehandler unchanged. NextNI02.2 remaining transport-source constraints. Full independent/external acceptance not claimed.\n"
p=Path("wiki/runbooks/retailcase_active_work.md");f[str(p)]="""# CHECKPOINT1130 — continue all / NI02.2 next

NI02.1 now implemented_targeted_verified: report30/screen41/Qwen task prepared notrun. Actualown1118 contextDONE/order2135 SAP_2135/2plannedplaces exact36EA/6boxes/24kg/FF2PLANNED0, race/rollback/stale/replay; source2047badnorm unchanged. No factories rerun. Auto signature includes limits after1125; cached1118receipt immutable. New receipts planned_pallets; actual1118oldreceipt onlystats, UI correctly says composition in card. APIserv1127 restarted latestPython1127 (includes auto limits/volume36/planned metadata/currentQC resolver). Encoding1125PASS before1126–1130; final latestencodingpending.

1126–1130 QCphysicalalias delivered: quality_identifier.py freshRUSERS/currentQCrights/exactUNION3/nativeassertallcandidates/ambiguity409. GETstatus physicalCP553000000001131/CASE:1131→canonicalCASE.QC.ST:4bb85f1f15:1131/current20/readyfalse; unknownactor/source denied. UIadoptIdentifier validatesrequested/canonical in readonly/recovery/deeplink, freezescanonical beforecommands/retries. No aliasreresolution ofsavedPOST/currentNativeQC/stockcommandsunchanged; noDDL/noQCPOST. Read1127+HTTP1128/JS1129 PASS, old1097/1102PASS beforelinkedhelper minor (rerunonlyifnewconcern). Architecture699/0cycles/76debtPASS. Report31/evidence/screens42 actualopenedphysicalcode; browser821857750 Chrome2 order1043Tab now8088/wms-admin/warehouse-tasks.html?qc_shipment=CP553000000001131&v1129#outgoingQuality. QCv20/BOTH/independent/fullscan/SIweightpolicy stillmissing, notbypassed. SQLalias11.433ms17buffers/17.32ms10 exactUNION/bound3 retain noindex ownerinventory.

Plan53 currentNI02.2. Activecard ni02_2 says calendar/ERP late decision delivered264–278; remaining tare/temperature/deadline/dock constraints. Need inspect existingtransportapproval/currentvehicle/temp policy native beforeadding anything. Reuse assignment/coordinator nosecondengine. All18 fullacceptance notcomplete, continueowneruntilall/no cutoff/noagents/goals/noGithubuntilactualall/noDBcopies/min80%functionality. Reports31 andQwen auto task saved originalRussian folder. Protected987 currentP20H20/HU1069v10/CASE1131CT20qty12;HU994v18/CASE1132CT13qty8 bothTOPQW/1157+1159DONE unchanged; no NEWfixtures. Do not guesspaths/globs/ports, avoidbroad tmp rg (millions ofoutput); eachlookup thenobservedread. Python-cbootstrap broken __file__, write tiny script instead. Newauto DDL none.

""" +p.read_text(encoding="utf-8")
print(json.dumps(f,ensure_ascii=True))
