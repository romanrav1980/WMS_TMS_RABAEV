from pathlib import Path
import json
read=lambda p:Path(p).read_text(encoding="utf-8");files={}
p="wiki-raw/wms_admin_ui_reference/receiving.js";v=read(p)
v=v.replace("  const sourceOrder = new URLSearchParams(location.search).get('supply_order_id');\n  let sourceOpened = false;","""  const sourceQuery=new URLSearchParams(location.search);
  const sourceOrder=sourceQuery.get('supply_order_id')||sourceQuery.get('order_id');
  const sourceLine=sourceQuery.get('line_number');
  let sourceOpened=false,sourceLineOpened=false;""",1)
v=v.replace("if(sourceDocument||sourceOrder.length>100)","if(sourceDocument||sourceOrder.length>100||(sourceQuery.get('supply_order_id')&&sourceQuery.get('order_id')&&sourceQuery.get('supply_order_id')!==sourceQuery.get('order_id')))",1)
v=v.replace("      if(order.lines.length===1)await selectLine(order.lines[0]);","""      if(sourceLine&&!sourceLineOpened&&(!sourceOrder||order.order_id===sourceOrder)){
        const requested=sourceLine.length<=100?order.lines.find(line=>String(line.line_number)===sourceLine):null;
        if(!requested)throw new Error('Позиция из ссылки не найдена в текущем заказе. Выберите строку в таблице.');
        sourceLineOpened=true;await selectLine(requested,order.order_id);
      }else if(order.lines.length===1)await selectLine(order.lines[0]);""",1)
v=v.replace("item.line_number===line.line_number&&item.articul===line.articul","String(item.line_number)===String(line.line_number)&&item.articul===line.articul",1)
v=v.replace("      message(`Приёмка: ${line.articul}, ${line.name}`);","""      message(currentOrder.receipt_allowed
        ?`Выбрана строка ${line.line_number}: ${line.articul}, ${line.name}`
        :`Выбрана строка ${line.line_number}. Основание закрыто; доступен просмотр правил и истории.`);""",1)
v=v.replace("state.policy=null;sourceOpened=false;resetPallet()","state.policy=null;sourceOpened=false;sourceLineOpened=false;resetPallet()",1);files[p]=v
p="wiki-raw/wms_admin_ui_reference/receiving.html";files[p]=read(p).replace('receiving.js?v=20261013-969','receiving.js?v=20261013-1034').replace('receiving.css?v=20261013-969','receiving.css?v=20261013-1034')
p="wiki-raw/wms_admin_ui_reference/receiving.css";files[p]=read(p)+"\n#receiptLines{scroll-margin-top:140px}.receiving-page tr[data-selected='true']{background:#eaf3ff;box-shadow:inset 3px 0 #347de7}.receiving-page .receipt-select-button:focus-visible{outline:3px solid #98bffd;outline-offset:2px}\n"
print(json.dumps(files,ensure_ascii=True))
