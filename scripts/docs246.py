from pathlib import Path
import json
out={}
page="""# NI08.1: предварительный контроль сохраняет собственную погруженную СТ
246 — приложение, без Oracle DDL. После241 штатное additive assign_sts допускает сохранение собственной погруженной СТ; предварительный контроль163 всё ещё отвергал любую CONDITION=2. Исправлен существующий current_sources/route_result, без нового назначения или проводки.
В том же READ ONLY snapshot возвращается число действующих физических подтверждений: ACTIVE membership, LOADED load fact, APPLIED stock operation, unreleased custody, текущий planned/unbilled/nondeleted TT, совпавшие ID/номер машины и членство СТ. Только ровно одно такое подтверждение и тот же запрошенный manual trip снимают source blocker. Новый план, чужой рейс, отгруженный рейс, отсутствующее или неоднозначное доказательство остаются запрещены. Native capacity/application checks сохранены; operational_admission=false, общий aware calendar/driver/loading gate не заявлен.
scripts/case246_preflight.py: существующий собственный33541, уже LOADED исходная СТ224 не получает ложного source blocker. Новый план с теми же строками отвергается; completed33558 не получает retained proof и остаётся BLOCKED. Ни TT/ST, ни количество не изменены, protected20/20. Архитектура567/0циклов/76debt PASS. Независимый Qwen запуск не заявлен.
SQL текущего bounded чтения25.839ms/2: retain существующие ST_NUMBER batch200/row5000 и ключи membership/load/operation/TT/vehicle. Коррелированный lookup только для выбранных строк, без полного просмотра load history; новый индекс или cache не оправданы этим случаем. Owner transport проверяет большой фактический набор перед промышленным допуском.
"""
out["wiki/database/nicora_ni081_retained_preflight_20261011.md"]=page
for path,line in [
("wiki/index.md","- [Предварительный контроль сохраняет свою погруженную СТ](database/nicora_ni081_retained_preflight_20261011.md):246 same read snapshot/exact active physical proof/current trip; foreign-new-departed blocked/no stock."),
("wiki/log.md","2026-10-11:246 reconciled original manual preflight163 with native additive assignment241: own LOADED ST retained only exact one current ACTIVE/APPLIED/unreleased load proof with same trip/vehicle, current planned unbilled TT. New/foreign/departed remain blocked. Actual33541 positive/33558 negative/no writes/protected20-20/architecture5670cycles76debt. Bounded SQL25.839ms2 retain existing keys/batches; no new index/cache. Common calendar admission remains."),
("wiki/requirements/nikora_delivery_v55/execution/active/ni08_1.md","11.10.2026:246 own physically LOADED ST retained in manual preflight under exact current membership/stock/custody/vehicle/TT proof; same snapshot/no quantity. New/foreign/departed refuse. Shared aware calendar remains.")
]:
 out[path]=Path(path).read_text(encoding="utf-8")+"\n"+line+"\n"
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json")
j=json.loads(p.read_text(encoding="utf-8"))
next(x for x in j["increments"]if x["id"]=="NI08.1").setdefault("implementedSlices",[]).append("246 manual preflight retains own physically loaded ST under exact active current proof/same snapshot/new foreign departed denied/no stock")
out[str(p)]=json.dumps(j,ensure_ascii=True,indent=2)+"\n"
root=next(p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md"))
out[str(root/"NI08.1"/"246_retained_preflight.md")]="# Qwen:246 — сохранение погруженной СТ в preflight\nПроверить совпадение native241 conditions/current manual trip/ровно один ACTIVE LOADED APPLIED unreleased custody proof/current vehicle/planned unbilled TT. New plan, foreign/departed, zero/duplicate proof refuse. Same READ ONLY snapshot, current actor/Ware before response; native capacity and operational_admission=false preserved. Existing33541 positive/completed33558 negative; no writes/protected20-20. Bounded SQL/batch decision documented.\n"
print(json.dumps(out,ensure_ascii=True))
