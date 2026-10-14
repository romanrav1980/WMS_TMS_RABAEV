from pathlib import Path
import json
p="wiki-raw/wms_admin_ui_reference/receiving.js";v=Path(p).read_text(encoding="utf-8")
v=v.replace("sourceLineOpened=true;await selectLine(requested,order.order_id);","sourceLineOpened=true;await selectLine(requested,order.order_id,confirmedRefresh);",1).replace("await selectLine(order.lines[0]);","await selectLine(order.lines[0],order.order_id,confirmedRefresh);",1)
v=v.replace("async function selectLine(line,expectedOrderId=state.order?.order_id) {\n    if(state.busy)","async function selectLine(line,expectedOrderId=state.order?.order_id,confirmedRefresh=false) {\n    if(state.busy&&!confirmedRefresh)",1)
v=v.replace("el('receiptConfirm').disabled=!canConfirm();}","el('receiptConfirm').disabled=!canConfirm();updateLabelAvailability();}")
v=v.replace("if(!state.order&&window.wmsAdminAuth.state.user)void loadOrders();}","if(!state.order&&window.wmsAdminAuth.state.user)void loadOrders();updateLabelAvailability();}")
v=v.replace("renderCodes();}\n  function updateScanMode()","renderCodes();updateLabelAvailability();}\n  function updateScanMode()",1)
h="wiki-raw/wms_admin_ui_reference/receiving.html";s=Path(h).read_text(encoding="utf-8").replace("receiving.js?v=20261013-1035","receiving.js?v=20261013-1037")
print(json.dumps({p:v,h:s},ensure_ascii=True))
