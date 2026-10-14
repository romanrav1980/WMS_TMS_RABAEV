from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/domain/sscc_label.py");s=p.read_text(encoding="utf-8")
s=s.replace("def label_html(data: dict) -> str:","def label_html(data: dict, compact: bool = False) -> str:")
s=s.replace("    return '<!doctype html><html>", "    html = '<!doctype html><html>",1)
needle="\n\ndef label_zpl"
pos=s.index(needle)
s=s[:pos]+'\n    return html.replace("size:105mm 148mm","size:100mm 70mm").replace("width:95mm","width:90mm") if compact else html\n'+s[pos:]
s=s.replace("def label_zpl(data: dict, dpi: int = 203) -> str:","def label_zpl(data: dict, dpi: int = 203, compact: bool = False) -> str:")
s=s.replace("commands = [f'^XA^CI28^PW{px(105)}^LL{px(148)}']", "commands = [f'^XA^CI28^PW{px(100 if compact else 105)}^LL{px(70 if compact else 148)}']")
s=s.replace("{px(95)}^BY","{px(18 if compact else 95)}^BY")
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/case_labels.py");s=p.read_text(encoding="utf-8")
s=s.replace('data={"sscc":current["sscc"],"CASE":str(task),"source_identifier":current["original_carrier"]}','data={"sscc":current["sscc"],"Задание":str(task)}')
s=s.replace("return label_zpl(data,dpi)if format==\"zpl\"else label_html(data)","return label_zpl(data,dpi,compact=True)if format==\"zpl\"else label_html(data,compact=True)")
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/api/case_label_routes.py");s=p.read_text(encoding="utf-8").replace("dpi:int=Query(203,ge=203,le=600)","dpi:Literal[203,300,600]=203")
s=s.replace("from fastapi import APIRouter,Depends,Query","from fastapi import APIRouter,Depends")
out[str(p)]=s
p=Path("wiki/database/retailcase_ni042_final_qc_20261011.md");s=p.read_text(encoding="utf-8")
s+="\nДля малой коробки исходный GS1-128 генератор использует компактный100×70мм профиль: один номер задания и SSCC, без технического CP на поверхности и без планового количества. Паллетная входящая этикетка сохраняетA6. CASE принтеры203/300/600dpi явно допустимы, произвольный DPI не масштабирует модуль ниже нормы. [GS1 Logistic Label Guideline](https://ref.gs1.org/guidelines/logistic-label/): X от0.495мм, высота штрихов от31.75мм, quietzone10X; новый SVG90мм/176modules даётX≈0.511мм и высоту≈33.24мм, ZPL35мм/4,6,12dots. Физическое качество печати/считываемость проверяется на выбранном принтере в пилоте.\n"
out[str(p)]=s
for path in Path(".").glob("*/NI04.2/20[234]_*.md"):
 text=path.read_text(encoding="utf-8")
 text="Текущий составной прогон после205: scripts/ni042_final_qc_case.py. Ранний авторский сценарий202/203/204 сохраняется как исторический снимок до обязательных последующих ворот; он отдельно не является актуальным smoke полного NS40. Проверяйте соответствующую часть составного сценария и native/API/browser требования ниже.\n\n"+text
 out[str(path)]=text
p=Path("wiki/index.md");out[str(p)]=p.read_text(encoding="utf-8")+"\n- NI04.2/205: компактная100×70мм SSCC-этикетка CASE использует исходный генератор; сохранёнA6 приёмки, DPI203/300/600, физическая печать в пилоте.\n"
p=Path("wiki/log.md");out[str(p)]=p.read_text(encoding="utf-8")+"\n2026-10-11:205 CASE print profile100x70/one task+SSCC using original GS1 generator; receiptA6 preserved, CASE DPI203/300/600, native physical facts unchanged. Official GS1 size/quietzone reference recorded; Qwen202–204 current composed205 instead of historical pre-gate scripts. Offline gate encountered pytest temp setup Windows access issue; sole failing test passed immediately, retry with dedicated workspace basetemp/no cache.\n"
print(json.dumps(out,ensure_ascii=True))
