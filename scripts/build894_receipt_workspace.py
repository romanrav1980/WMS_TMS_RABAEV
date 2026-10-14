from pathlib import Path
import json
files={}
p="wiki-raw/wms_admin_ui_reference/receiving.html";s=Path(p).read_text(encoding="utf-8")
s=s.replace('<link rel="stylesheet" href="styles.css">','<link rel="stylesheet" href="styles.css"><link rel="stylesheet" href="receiving.css?v=20261013-894">',1)
s=s.replace('<section class="admin-page"><article class="panel">','''<section class="admin-page receiving-page"><article id="receiptContext" class="panel receipt-context"><header><h2>Приёмка на основании SAP</h2><span data-version></span></header><div class="receipt-context-grid"><div><small>Основание поставки</small><strong data-order></strong><small data-warehouse></small></div><div><small>Текущий товар</small><strong data-article></strong><small data-remaining></small><small data-accepted></small></div><div><small>Правила сканирования</small><strong data-scanning></strong><small data-profiles></small></div></div></article><article class="panel receipt-list-panel">''',1)
s=s.replace('<article class="panel"><header class="panel-header"><h2 id="receiptOrderTitle">','<article class="panel receipt-lines-panel"><header class="panel-header"><h2 id="receiptOrderTitle">',1)
s=s.replace('<article class="panel"><header class="panel-header"><h2>Принимаемая паллета','<article id="receiptPallet" class="panel"><fieldset id="receiptPalletFields"><legend class="sr-only">Принимаемая паллета</legend><header class="panel-header"><h2>Принимаемая паллета',1)
s=s.replace('<a href="warehouse-tasks.html">Задания на размещение</a></article>','<a href="warehouse-tasks.html" title="Открыть фактические задания на перемещение принятого товара">Задания на размещение →</a></fieldset></article>',1)
s=s.replace('<h2>Настройки приёмки склада</h2>','<details><summary title="Открыть действующие настройки склада, температурные правила и время пополнения">Настройки приёмки склада</summary>',1)
s=s.replace('<p id="receiptSettingsMessage"></p></article>','<p id="receiptSettingsMessage"></p></details></article>',1)
s=s.replace('id="receiptReplanPallet" maxlength="25"','id="receiptReplanPallet" maxlength="50"')
s=s.replace('<script src="receiving-intent.js">','<script src="receiving-context.js?v=20261013-894"></script><script src="receiving-intent.js">',1)
s=s.replace('<script src="receiving.js">','<script src="receiving.js?v=20261013-894">',1)
files[p]=s
p="wiki-raw/wms_admin_ui_reference/receiving.js";s=Path(p).read_text(encoding="utf-8")
s=s.replace("    if(onClick)tr.addEventListener('click',onClick);","""    if(onClick){
      tr.tabIndex=0;tr.title='Выбрать строку для приёмки';tr.addEventListener('click',onClick);
      tr.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();onClick();}});
    }""",1)
s=s.replace("  async function loadOrders() {","  async function loadOrders() {\n    if(state.busy){message('Дождитесь подтверждения текущей паллеты.');return;}",1)
s=s.replace("  async function selectOrder(id) {","  async function selectOrder(id,confirmedRefresh=false) {\n    if(state.busy&&!confirmedRefresh){message('Дождитесь подтверждения текущей паллеты.');return;}",1)
s=s.replace("    state.order=null;state.line=null;state.policy=null;el('receiptConfirm').disabled=true;","    state.order=null;state.line=null;state.policy=null;el('receiptConfirm').disabled=true;\n    el('receiptLines').replaceChildren();el('receiptOrderTitle').textContent='Загрузка заказа…';",1)
s=s.replace("  async function selectLine(line) {","  async function selectLine(line) {\n    if(state.busy||!state.order||!state.order.lines.includes(line))return;\n    const token=++state.readEpoch,currentOrder=state.order;",1)
s=s.replace("      if(state.line!==line)return;","      if(token!==state.readEpoch||state.order!==currentOrder||state.line!==line)return;",1)
s=s.replace("      state.policy=policy;el('receiptMarking')","      state.policy=policy;window.dispatchEvent(new CustomEvent('wms-receipt-policy-selected',{detail:{articul:line.articul,policy}}));el('receiptMarking')",1)
s=s.replace("    }catch(error){message(error.message);}\n  }\n  function resetPallet", "    }catch(error){if(token===state.readEpoch&&state.order===currentOrder)message(error.message);}\n  }\n  function resetPallet",1)
s=s.replace("    state.busy=true;el('receiptConfirm').disabled=true;","    state.busy=true;el('receiptConfirm').disabled=true;el('receiptPalletFields').disabled=true;",1)
s=s.replace("await selectOrder(id);message(text);","await selectOrder(id,true);message(text);",1)
s=s.replace("finally {state.busy=false;el('receiptConfirm')","finally {state.busy=false;el('receiptPalletFields').disabled=false;if(!state.order&&window.wmsAdminAuth.state.user)void loadOrders();el('receiptConfirm')",1)
files[p]=s
print(json.dumps(files,ensure_ascii=True))
