import json
from pathlib import Path
out={}
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json");m=json.loads(p.read_text(encoding="utf-8"))
m["firstChange"]="NI07.1: establish actual ordinary BOX assembly start on existing HU owners; then support separate CASE assembly dates inside one load while retaining once-only source charging. Preserve existing reuse and unresolved external acceptance."
out[str(p)]=json.dumps(m,ensure_ascii=False,indent=2)+"\n"
p=Path("wiki/runbooks/nicora_active_work.md");s=p.read_text(encoding="utf-8")
handoff="""## Следующая работа после checkpoint511
- Read wiki/database/nicora_ni071_revision_summary_20261012.md and finance/infrastructure/box_costs.py. Actual ordinary BOX assembly start must come from existing physical packing work; empty-container creation date is insufficient. Examine existing HU/link/task evidence before choosing a new record.
- Mixed CASE assembly dates inside one load currently explicitly fail COST_MULTIPLE_ASSEMBLY_PERIODS. Before changing financial line keys, inspect all FK/read/allocation/correction consumers. Preserve single source charge and immutable historical rates; no inferred average pretending to be an approved rate.
- Existing tested contexts:406 full grouped delivery;462 original BOX1/PALLET cancellation;464 receivedSAP3/6;483 refused1 supplier491/damaged1disposed490/buyer3/missing2;502 measuredCASE charge3/v2. Exact saved replay/read only, no source/initial factories.
- API509 current; schema RABAEV/orcl, native VALID; architecture648/0cycles/76debt/adminTS/encoding passed. No independent Qwen/hardware/externalACK or full18-sprint acceptance claimed.
- Last tasks Qwen: NI04.3/467, NI06.2/494, NI07.1/507. Keep at least80% implementation and only changed-path cases. Do not publish GitHub without fresh instruction.

"""
out[str(p)]=handoff+s
p=Path("wiki/index.md");out[str(p)]="- [Checkpoint511 и продолжение](runbooks/nicora_active_work.md):actual BOX start/mixed-date single-load finance next; exact existing fixture replay rules/current API509.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");out[str(p)]=p.read_text(encoding="utf-8")+"\n-12.10.2026 checkpoint511: JSON firstChange synchronized with currentNI07.1; next-source research and financial consumer constraints recorded. No extra broad runs/publication; final encoding passed510.\n"
print(json.dumps(out))
