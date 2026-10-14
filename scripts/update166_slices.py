import json
from pathlib import Path
p=Path(__file__).resolve().parents[1]/"wiki/requirements/nikora_delivery_v55/implementation_plan.json"
m=json.loads(p.read_text(encoding="utf-8-sig"))
items={"NI08.1":["161 workload person-hour/window advisory; separate existing approvals","162 preserved installed OR-Tools relative schedule/archive633/UI invalidation; no strict admission","163 read-only auto/manual preflight reuses existing native rules/currentsource/scope/UI"],
 "NI03.3":["164 current CASE queue/detail snapshot/warehouse; bounded history read","165 native CASE actor/WARE/right before replay/afterwait; actual native mutex test","166 current CASE marking-card/short-list scope; existing settings preserved"]}
for row in m["sprints"]:
 for text in items.get(row.get("id"),[]):
  if text not in row.setdefault("implementedSlices",[]):row["implementedSlices"].append(text)
p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
