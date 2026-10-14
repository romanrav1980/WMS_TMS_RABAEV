from pathlib import Path
import json
files={}
p="wiki-raw/wms_admin_ui_reference/receiving-intent.js";t=Path(p).read_text(encoding="utf-8")
start=t.index('    const successful =');end=t.index('    const rejected =',start)
t=t[:start]+'''    function quantity(value){
      const text=String(value??'');
      if(!/^[0-9]+(?:[.][0-9]{1,9})?$/.test(text))return null;
      const [whole,fraction='']=text.split('.');
      return whole.replace(/^0+(?=[0-9])/,'')+(fraction.replace(/0+$/,'')?'.'+fraction.replace(/0+$/,''):'');
    }
    const identifier=intent.body.pallet_identifier||intent.body.sscc;
    const successful = status >= 200 && status < 300 && data?.status==='RECEIVED'
      && data.operation_id===intent.body.operation_id && data.pallet_identifier===identifier
      && data.line_number===intent.body.line_number
      && quantity(data.quantity)!==null && quantity(data.quantity)===quantity(intent.body.quantity)
      && Number.isSafeInteger(data.task_id) && data.task_id>0;
    const stored=localStorage.getItem(intent.storage_key);
    if(stored){
      const current=JSON.parse(stored);
      if(current.path!==intent.path||current.body?.operation_id!==intent.body.operation_id||material(current.body)!==material(intent.body))
        throw new Error('Сохранённая приёмка изменена в другой вкладке. Перечитайте исходный запрос.');
    }else return;
    if(status>=200&&status<300&&!successful)
      throw new Error('Ответ не соответствует исходной приёмке. Запрос сохранён; повторите его без изменения данных.');
'''+t[end:]
files[p]=t
p="wiki-raw/wms_admin_ui_reference/receiving.js";t=Path(p).read_text(encoding="utf-8")
t=t.replace("state.busy=true;el('receiptRetryPending').disabled=true;","state.busy=true;el('receiptRetryPending').disabled=true;el('receiptPalletFields').disabled=true;")
t=t.replace("resetPallet();await selectOrder(orderId);","resetPallet();await selectOrder(orderId,true);")
t=t.replace("finally{state.busy=false;renderPending();}","finally{state.busy=false;el('receiptPalletFields').disabled=false;renderPending();if(!state.order&&window.wmsAdminAuth.state.user)void loadOrders();}")
files[p]=t
p="wiki-raw/wms_admin_ui_reference/receiving.html";t=Path(p).read_text(encoding="utf-8").replace('src="receiving-intent.js"','src="receiving-intent.js?v=20261013-930"').replace('v=20261013-915','v=20261013-930');files[p]=t
print(json.dumps(files,ensure_ascii=True))
