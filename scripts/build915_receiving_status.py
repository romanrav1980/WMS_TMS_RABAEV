from pathlib import Path
import json
files={}
p="api/wms_api_server/app/modules/integrations/infrastructure/supply_reads.py";t=Path(p).read_text(encoding="utf-8")
t=t.replace('cur.execute("select *from RRL_SAP_SUPPLY_ORDER where ORDER_ID=:order_id", order_id=order)','cur.execute("select s.*,h.CONDITION INCOMING_CONDITION from RRL_SAP_SUPPLY_ORDER s join RRL_PRIHOD_NAKLAD h on h.ID=s.NAKLAD_ID where s.ORDER_ID=:order_id", order_id=order)')
needle='header["lines"] = lines'
t=t.replace(needle,'''header["receipt_allowed"] = header["incoming_condition"] == 0 and header.get("closed_at") is None
        header["receipt_state"] = "REVERSED" if header["incoming_condition"] == 3 else "RECONCILED" if header.get("closed_at") is not None else "OPEN" if header["incoming_condition"] == 0 else "COMPLETE" if header["incoming_condition"] == 1 else "LEGACY_CLOSED"
        '''+needle)
files[p]=t
p="wiki-raw/wms_admin_ui_reference/receiving.js";t=Path(p).read_text(encoding="utf-8")
t=t.replace("message('Основание SAP открыто. Выберите товар для приёмки.');","message(order.receipt_allowed?'Основание SAP открыто. Выберите товар для приёмки.':'Приёмка этого основания закрыта. Доступен просмотр истории.');")
t=t.replace("if(state.busy||!state.order||!state.line||!state.policy)return;","if(state.busy||!state.order?.receipt_allowed||!state.line||!state.policy)return;")
t=t.replace("Number(line.remaining_qty)<=0||!window.wmsAdminAuth","!state.order.receipt_allowed||Number(line.remaining_qty)<=0||!window.wmsAdminAuth")
t=t.replace("!state.line||!state.policy||Number(state.line.remaining_qty)<=0","!state.order?.receipt_allowed||!state.line||!state.policy||Number(state.line.remaining_qty)<=0")
files[p]=t
p="wiki-raw/wms_admin_ui_reference/receiving-context.js";t=Path(p).read_text(encoding="utf-8")
t=t.replace("order?'Версия '+order.revision:'—'","order?'Редакция '+order.revision+' · формат '+(order.gateway_contract_version||1):'—'")
t=t.replace("'Основание приёмки не выбрано');","'Основание приёмки не выбрано');")
t=t.replace("text('[data-accepted]',line?'Принято '+line.accepted_qty","text('[data-accepted]',line?(order?.receipt_state==='REVERSED'?'Принято ранее ':'Принято ')+line.accepted_qty")
t=t.replace("root.dataset.ready=order&&line&&policy?'true':'false';","const statuses={OPEN:'Открыта приёмка',COMPLETE:'Количество принято полностью',REVERSED:'Поступление сторнировано',RECONCILED:'Приёмка закрыта со сверкой',LEGACY_CLOSED:'Закрыто старым процессом'};\n    text('[data-source-status]',order?(statuses[order.receipt_state]||'Статус требует проверки'):'Выберите основание');\n    root.dataset.ready=order&&line&&policy?'true':'false';")
files[p]=t
p="wiki-raw/wms_admin_ui_reference/receiving.html";t=Path(p).read_text(encoding="utf-8").replace('v=20261013-912','v=20261013-915')
needle='<strong data-order></strong>';assert needle in t;t=t.replace(needle,needle+'<span data-source-status></span>')
files[p]=t
print(json.dumps(files,ensure_ascii=True))
