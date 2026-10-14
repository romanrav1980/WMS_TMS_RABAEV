from pathlib import Path
import json
out={}
for filename in ["ni06_1.md","ni05_3.md"]:
 p=Path("wiki/requirements/nikora_delivery_v55/execution/active")/filename
 s=p.read_text(encoding="utf-8")+"\n11.10.2026:301–303 [найденный остаток и повторная доставка](../../../../database/nicora_ni061_recovery_redelivery_20261011.md): actualordinary+marked2 existingTASK_COMPLETE→originalST/assignment→QC/load/depart→STORE. Buyer1+2=3, sourceFF3once, historicalloss2/found2/net0. Native rollback/replay/sixcodes/protected20-20; independent/hardware/external notclaimed. Partial/recurrent loss and nestedconsolidation remain.\n"
 if filename=="ni06_1.md":
  s=s.replace("Связать обязательства плеч, ворота, консолидацию, фактическую выгрузку/приём целевого склада; legacy SYNC не считать полным процессом.","Для отдельных обычных и маркированных целых/частичных паллет обе фактические приёмки, ворота, задания, ответственность, исходный заказ и целое восстановление недостачи с повторной доставкой реализованы. Остаток: вложенные и агрегированные места, консолидация/переупаковка, частичные и повторные циклы найденного груза, независимая и аппаратная приёмка/реальные внешние ответы.")
 out[p.as_posix()]=s
p=Path("wiki/log.md");out[p.as_posix()]=p.read_text(encoding="utf-8")+"\n- 11.10.2026 303 qualitycheckpoint: NICORA quality gate PASS (24 architecture/tooling cases +both frontend TypeScript), rawJS bothsyntaxPASS; architecture632/0cycles76. First quality attempt hit Windows Temp permissions; CLI now creates uniquely named pytest basetemp inside workspace, no external temp cleanup. Cards NI06.1/NI05.3 reflect real301–303 reuse and remaining scope.\n"
p=Path("wiki/index.md");out[p.as_posix()]=p.read_text(encoding="utf-8").replace("302–303 originalST/QC/LOAD/DEPART/STORE reused; buyer1+2=3/originalFF3once/history2-found2-net0.","302–303 originalST/QC/LOAD/DEPART/STORE reused; buyer1+2=3/originalFF3once/history2-found2-net0; qualitygatePASS.",1)
print(json.dumps(out))
