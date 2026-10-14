from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py");s=p.read_text(encoding="utf-8")
needle="    partial_receipt: bool | None = Field(strict=True,default=None)"
assert needle in s;s=s.replace(needle,needle+"\n    unit_keys: list[str] | None = Field(default=None,max_length=10000)",1)
out[p.as_posix()]=s
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse.js");s=p.read_text(encoding="utf-8")
needle=' const scanKey=()=>key()+":unit-draft";'
assert needle in s
s=s.replace(needle,''' const selectedUnitPanel=document.createElement("section");selectedUnitPanel.id="iwSelectedUnits";marks.append(selectedUnitPanel);
 const scanKey=()=>key()+":unit-draft";
''',1)
needle='el("iwUnitInfo").textContent='
position=s.index(needle)
line_end=s.index(';',position)
# Insert after the current source read already has a result; discover its variable.
source_function=s[s.index(" async function unitSource()"):s.index(" async function",s.index(" async function unitSource()")+10)]
print(source_function[:1600],file=__import__("sys").stderr)
out[p.as_posix()]=s
print(json.dumps(out,ensure_ascii=True))
