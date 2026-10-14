import json
from pathlib import Path
r=Path(__file__).resolve().parents[1];out={}
p=r/"wiki-raw/wms_admin_ui_reference/case-pick-tsd.html";s=p.read_text(encoding="utf-8")
needle='<button id="cpTsdRetryReturn" type="button" hidden>'
assert s.count(needle)==1
s=s.replace(needle,'<label>Причина отмены пустого места<input id="cpTsdEmptyCancelReason" maxlength="1000"></label><button id="cpTsdCancelEmpty" type="button">Отменить пустое место</button>'+needle)
out[str(p.relative_to(r))]=s
p=r/"wiki-raw/wms_admin_ui_reference/case-carrier-return.js";s=p.read_text(encoding="utf-8")
s=s.replace('cpTsdEl("cpTsdRetryReturn").hidden=!localStorage.getItem(key());',
 '''cpTsdEl("cpTsdRetryReturn").hidden=!localStorage.getItem(key());
  cpTsdEl("cpTsdCancelEmpty").disabled=!cpTsd.task||!!(cpTsd.task.physical_lots||[]).length||
    !/^0(?:\\.0+)?$/.test(String(cpTsd.task.picked_qty??"0"))||["CANCELLED","SHIPPED","FAILED"].includes(cpTsd.task.status);''',1)
s=s.replace('async function submit(retry){','async function submit(retry,empty=false){')
s=s.replace('if(!scan||!Object.keys(destinations).length)throw new Error("Отсканируйте идентификатор паллеты.");',
 '''if(!scan||(!empty&&!Object.keys(destinations).length))throw new Error("Отсканируйте идентификатор паллеты.");
    const reason=cpTsdEl("cpTsdEmptyCancelReason").value.trim();
    if(empty&&(Object.keys(destinations).length||!reason))throw new Error("Требуются пустое место и причина отмены.");''')
s=s.replace('scan_container:scan,expected_content_version:cpTsd.task.content_version,destinations}};',
 'scan_container:scan,expected_content_version:cpTsd.task.content_version,destinations,...(empty?{allow_empty:true,reason}:{})}};')
s=s.replace('await cpTsdFetch("/api/case-pick/tasks/"+intent.task+"/return-carrier",','const result=await cpTsdFetch("/api/case-pick/tasks/"+intent.task+"/return-carrier",')
s=s.replace('cpTsdSetState("Товар возвращён в исходные ячейки. Резерв снят, паллета отбора отменена.");',
 '''cpTsdSetState(result.status==="CANCELLED_EMPTY"?
    "Пустое место отменено, резерв снят. Если закреплена тара, освободите её бронь; затем примите решение по волне. Потребность заказа сохраняется.":
    "Товар возвращён в исходные ячейки. Резерв снят, паллета отбора отменена.");''')
s=s.replace('cpTsdEl("cpTsdRetryReturn").addEventListener("click",()=>submit(true));',
 'cpTsdEl("cpTsdRetryReturn").addEventListener("click",()=>submit(true));\n  cpTsdEl("cpTsdCancelEmpty").addEventListener("click",()=>submit(false,true));')
out[str(p.relative_to(r))]=s
print(json.dumps(out))
