import json
from pathlib import Path
files={}
path=Path("api/wms_api_server/app/modules/transport/infrastructure/trip_selector.py")
text=path.read_text(encoding="utf-8")
text=text.replace("after_date: datetime|None,after_id: int,limit: int) -> dict:","after_date: datetime|None,after_id: int,limit: int,purpose: str=\"DEFER\") -> dict:",1)
old='        cur.callproc("RRL_ST_DEFER_API.context",[st,actor,out])\n        context=read_oracle_json(out.getvalue())'
new='        if purpose=="ASSIGN":\n            from .assignment_picker_source import assignment_picker_source\n            context=assignment_picker_source(cur,st,actor)\n        elif purpose=="DEFER":\n            cur.callproc("RRL_ST_DEFER_API.context",[st,actor,out]);context=read_oracle_json(out.getvalue())\n        else:raise TransportPlanError("ST_TRIP_PURPOSE_INVALID","Допустимы ASSIGN/DEFER",422)'
assert old in text;text=text.replace(old,new,1);files[str(path)]=text
path=Path("api/wms_api_server/app/modules/transport/infrastructure/st_deferral.py")
text=path.read_text(encoding="utf-8").replace("after_id: int,limit: int) -> dict:","after_id: int,limit: int,purpose: str=\"DEFER\") -> dict:",1).replace("district,store,after_date,after_id,limit)","district,store,after_date,after_id,limit,purpose)",1);files[str(path)]=text
path=Path("api/wms_api_server/app/modules/transport/contracts_st_deferral.py")
text=path.read_text(encoding="utf-8").replace("after_id: int,limit: int) -> dict:","after_id: int,limit: int,purpose: str=\"DEFER\") -> dict:",1);files[str(path)]=text
path=Path("api/wms_api_server/app/modules/transport/api/st_deferral_routes.py")
text=path.read_text(encoding="utf-8");text="from typing import Literal\n"+text
text=text.replace("limit: int=Query(default=50,ge=1,le=100),","limit: int=Query(default=50,ge=1,le=100),\n                    purpose: Literal[\"DEFER\",\"ASSIGN\"]=\"DEFER\",",1)
text=text.replace("after_date,after_trip_id,limit)","after_date,after_trip_id,limit,purpose)",1);files[str(path)]=text
path=Path("wiki-raw/wms_admin_ui_reference/st-trip-picker.js")
text=path.read_text(encoding="utf-8").replace("el('sdSt').value.trim()!==source.st_number","el(source.source_input_id||'sdSt')?.value.trim()!==source.st_number")
text=text.replace("st_number:current.st_number,limit:'50'","st_number:current.st_number,limit:'50',purpose:current.purpose||'DEFER'")
text=text.replace("if(result.source_hash!==current.source_hash)","if(current.source_hash&&result.source_hash!==current.source_hash)")
text=text.replace("if(initial){el('tpFrom')","if(!current.source_hash)current.source_hash=result.source_hash;\n   if(initial){el('tpFrom')")
text=text.replace("Подставить рейс в форму переноса; сохранение выполняется отдельно","Выбрать существующий рейс; назначение или перенос выполняются отдельно")
files[str(path)]=text
html=Path("wiki-raw/wms_admin_ui_reference/customer-orders.html")
text=html.read_text(encoding="utf-8").replace('<button id="sapTripReview"','<button id="sapTripChoose" type="button" title="Открыть существующий выбор рейса с фильтрами даты, района и магазина.">Выбрать рейс</button><input id="sapTripPickerSource" type="hidden"><button id="sapTripReview"',1)
source=Path("wiki-raw/wms_admin_ui_reference/day-reconciliation.html").read_text(encoding="utf-8")
dialog=source[source.index('<dialog id="tpDialog"'):source.index('</dialog>')+len('</dialog>')]
dialog=dialog.replace("ПЕРЕНОС СТ","НАЗНАЧЕНИЕ СТ").replace("Закрыть окно без переноса СТ","Закрыть окно без назначения СТ")
text=text.replace('    <script src="admin-nav.js',dialog+'\n    <script src="admin-nav.js',1)
text=text.replace('</head>','<link rel="stylesheet" href="trip-picker.css?v=20261014-1221"></head>',1)
text=text.replace('</body>','<script src="st-trip-picker.js?v=20261014-1221"></script><script src="sap-trip-picker.js?v=20261014-1221"></script></body>',1)
files[str(html)]=text
print(json.dumps(files,ensure_ascii=True))
