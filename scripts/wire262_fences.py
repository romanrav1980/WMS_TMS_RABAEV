from pathlib import Path
import json
p=Path("wiki-raw/wms_admin_ui_reference/receiving.js");s=p.read_text(encoding="utf-8").replace('order:null,line:null,policy:null,','order:null,line:null,policy:null,readEpoch:0,listEpoch:0,')
a=s.index("  async function loadOrders() {");b=s.index("  async function selectOrder(",a)
part=s[a:b].replace("    try {","    const token=++state.listEpoch;\n    try {",1).replace("      el('receiptOrders').replaceChildren", "      if(token!==state.listEpoch)return;\n      el('receiptOrders').replaceChildren",1)
part=part.replace("        sourceOpened=true;", "        if(token!==state.listEpoch)return;\n        sourceOpened=true;")
part=part.replace("}catch(error){message(error.message);}", "}catch(error){if(token===state.listEpoch)message(error.message);}")
s=s[:a]+part+s[b:]
a=s.index("  async function selectOrder(");b=s.index("  async function selectLine(",a)
part=s[a:b].replace("    state.line=null;", "    const token=++state.readEpoch;\n    state.order=null;state.line=null;",1)
part=part.replace("));state.order=order;", "));if(token!==state.readEpoch)return;state.order=order;")
part=part.replace("}catch(error){message(error.message);}", "}catch(error){if(token===state.readEpoch)message(error.message);}")
s=s[:a]+part+s[b:]
s=s.replace("()=>{state.order=null;state.line=null;state.policy=null;resetPallet();", "()=>{state.readEpoch++;state.listEpoch++;state.order=null;state.line=null;state.policy=null;resetPallet();")
s=s.replace("error.message+' Исходный запрос сохранён до подтверждения.'", "error.message+' Проверьте список неподтверждённых запросов.'")
print(json.dumps({str(p):s},ensure_ascii=True))
