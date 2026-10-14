from pathlib import Path
import json
out={}
out["wiki/database/nicora_ni042_marked_direct_20261011.md"]="""# NI04.2: маркированный pick-by-line
201 reuses installed199 native DIRECT/source HARD/CASE roots, no duplicate allocator or schema writer. Own scripts/ni042_marked_direct_receiving_case.py QPB2015561DE80/wave448 real ARTMAS10 EA12/SAP file XML supplier→current receiving. WMS SKU card requires two UNIT profiles CRPT TOBACCO and EGAIS ALCOHOL; synthetic testcodes12physical/24codes, no government signature or external legal ACK claimed.
Before physical receipt both original customer orders5/7 have no stock/HARD. After current receipt pending putaway IN_PROGRESS blocks admission; native launch current source HARD12 and atomic old placement cancellation/rollback restores PLANNED+H0. No replenishment/rack target. Existing native CASE barcode+physical unit scans (bothprofiles) allocate exact current selected source units5/7; EAN-only refuses409. Unit counts and BASEqty5+7=12, no unit assignedtwice, originalsource0. Exact original operation replay has no second movement. Native return/release/countcleanup/original13520/20.
Existing categoryB fill-to-volume confirmed from current native RRL_STOCK_REPL_ADMISSION.mode_for and previous029 proof/scripts/ni032_partial_replenishment_case.py: B+occupied+allowed partial→min freecapacity/source, different category/fullmode/minimax/SHORT retain explicit rules. Do not create a second category engine. NS40 small-box independent final weight/control next.
"""
for path,line in[("wiki/index.md","- [Маркированный pick-by-line](database/nicora_ni042_marked_direct_20261011.md):201 realSAP physical12/codes24/5+7/exact QR/EAN409/no replenishment/no govACK; categoryB existing029 reused."),
("wiki/log.md","2026-10-11:201 markedDIRECT actual5561de8012physical/24codes/two WMS profiles/orders5+7/currentHard/QRmandatory/replay/rollback/native cleanup passed. No govACK. Current native B mode and029 evidence found; no duplicate implementation. NS40 finalsmallboxweight next."),
("wiki/requirements/nikora_delivery_v55/execution/active/ni04_2.md","11.10.2026:201 NS37 marked software12 physical/24 codes→stores5+7/current exact unitHARD/EAN-only409/replay/return passed; categoryB existing029 mode/proof reused. NS40 final smallbox independent weight is confirmed remaining gap.")]:
 p=Path(path);out[path]=p.read_text(encoding="utf-8")+"\n"+line+"\n"
roots=[p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md")]
if roots:out[str(roots[0]/"NI04.2"/"201_marked_pick_by_line.md")]="""# Qwen:201
Run ni042_marked_direct_receiving_case.py dev. SAP recipient/current accepted physical12 and24codes2profiles; originalorders5/7 from receiving no rack/replenishment. Exact selected unitHARD, EAN-only refuses, wrong-owner/profile/unit/source refused, replay unchanged. Original physical total12 not24, five andseven unique keys only once. Native launch/placement rollback andreturncleanup. SyntheticCRPT/EGAIS probes are not legalgovACK; real card profile byapplicability. Native categoryB fill already029; preserve explicit mode/minimax/SHORT/mixflag. NS40 finalsmallbox remains separate.
"""
print(json.dumps(out,ensure_ascii=True))
