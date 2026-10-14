from pathlib import Path
import json
read=lambda p:Path(p).read_text(encoding="utf-8");files={}
p="wiki-raw/wms_admin_ui_reference/receiving-context.js";v=read(p).replace("line?'К приёмке '+line.remaining_qty+' '+line.base_uom:'—'","line?(order?.receipt_allowed?'К приёмке ':'Остаток по заказу: ')+line.remaining_qty+' '+line.base_uom:'—'",1);files[p]=v
p="wiki-raw/wms_admin_ui_reference/receiving.js";v=read(p)
v=v.replace("row.firstElementChild?.textContent===line.line_number","row.firstElementChild?.textContent===String(line.line_number)",1)
v=v.replace("  const message = text => {el('receiptMessage').textContent=text;};","""  const message = text => {el('receiptMessage').textContent=text;};
  function updateLabelAvailability(){
    el('receiptIssueLabel').disabled=!(state.order?.receipt_allowed&&state.line&&state.policy&&!state.busy&&Number(state.line.remaining_qty)>0);
  }
  updateLabelAvailability();""",1)
v=v.replace("state.policy=null;el('receiptConfirm').disabled=true;","state.policy=null;el('receiptConfirm').disabled=true;updateLabelAvailability();")
v=v.replace("updateScanMode();el('receiptConfirm').disabled=!canConfirm();","updateScanMode();el('receiptConfirm').disabled=!canConfirm();updateLabelAvailability();",1)
v=v.replace("    if(!state.order||!state.line){message('Выберите заказ и товар.');return;}","    if(!state.order?.receipt_allowed||!state.line||!state.policy||Number(state.line.remaining_qty)<=0){message('Для выпуска этикетки выберите открытое основание и позицию с остатком приёмки.');return;}",1)
v=v.replace("finally{el('receiptIssueLabel').disabled=false;}","finally{updateLabelAvailability();}",1);files[p]=v
p="wiki-raw/wms_admin_ui_reference/receiving.html";files[p]=read(p).replace('receiving-context.js?v=20261013-969','receiving-context.js?v=20261013-1035').replace('receiving.js?v=20261013-1034','receiving.js?v=20261013-1035')
test=read("scripts/check947_receiving_delegation.cjs")
test=test[:test.index("(async()=>{")]
test=test.replace("location:{search:'?supply_order_id=SOURCE'}","location:{search:'?order_id=SOURCE&line_number=2'}",1)
test=test.replace("vm.createContext(context);","source.receipt_allowed=false;source.lines[0].line_number=1;source.lines[1].line_number=2;\nvm.createContext(context);",1)
test+="""(async()=>{
 await flush();await flush();await flush();
 assert.equal(dispatched.filter(e=>e.type==='wms-receipt-line-selected').at(-1).detail.line_number,2);
 assert.equal(node('receiptLines').children[1].dataset.selected,'true');
 assert.equal(node('receiptConfirm').disabled,true);
 assert.equal(node('receiptIssueLabel').disabled,true);
 assert.match(node('receiptMessage').textContent,/Основание закрыто/);
 assert.equal(requests.filter(r=>r.includes('/pallets')||r.includes('/labels')).length,0);
 console.log('PASS1036 alias/explicitnumericline/stringdataset/currentpolicy/closedreceipt+labeldisabled/no writes');
})().catch(e=>{console.error(e);process.exitCode=1;});
"""
files["scripts/check1036_receipt_line_link.cjs"]=test
print(json.dumps(files,ensure_ascii=True))
