from pathlib import Path
import json,re
files={}
p="api/wms_api_server/app/modules/fulfillment/infrastructure/customer_order_read.py";t=Path(p).read_text(encoding="utf-8")
t=t.replace("legacy_order_id: int | None = None, limit: int = 200) ->", "legacy_order_id: int | None = None, limit: int = 200,\n             before_id: int | None = None) ->",1)
t=t.replace('        with self.gateway.transaction("Customer order list scoped READ ONLY")', '        if before_id is not None and before_id < 1:\n            raise ValueError("Positive order cursor required")\n        with self.gateway.transaction("Customer order list scoped READ ONLY")',1)
t=t.replace("limit, None if global_admin else warehouse)", "limit, None if global_admin else warehouse, before_id)",1)
t=t.replace("        warehouse: int | None = None,\n", "        warehouse: int | None = None,\n        before_id: int | None = None,\n",1)
t=t.replace("        if warehouse is not None:", '        if before_id is not None:\n            conditions.append("co.CUSTOMER_ORDER_ID < :before_id")\n            params["before_id"] = before_id\n        if warehouse is not None:',1)
t=t.replace('        conditions: list[str] = []', '        conditions: list[str] = ["exists(select 1 from RRL_CUSTOMER cx where cx.CUSTOMER_ID=co.CUSTOMER_ID)"]',1)
t=t.replace("            select *\n              from (\n                select co.CUSTOMER_ORDER_ID,", "                select co.CUSTOMER_ORDER_ID,",1)
t=t.replace("                  from RRL_CUSTOMER_ORDER co\n", """                  from (select co.* from RRL_CUSTOMER_ORDER co {where_sql}
                        order by co.CUSTOMER_ORDER_ID desc fetch first :limit rows only) co
""",1)
t=t.replace("                  {where_sql}\n                 group by", "                 group by",1)
t=t.replace("                 order by co.CUSTOMER_ORDER_ID desc\n              )\n             where rownum <= :limit", "                 order by co.CUSTOMER_ORDER_ID desc",1)
files[p]=t
p="api/wms_api_server/app/routers/customer_orders.py";t=Path(p).read_text(encoding="utf-8")
t=t.replace("    legacy_order_id: int | None = None,\n    limit: int = 200,", "    legacy_order_id: int | None = None,\n    limit: int = 200,\n    before_id: int | None = None,",1)
t=t.replace("legacy_order_id=legacy_order_id, limit=limit,", "legacy_order_id=legacy_order_id, limit=limit, before_id=before_id,",1)
needle='''    except PermissionError as exc:
        raise HTTPException(403, str(exc)) from exc

'''
assert needle in t;t=t.replace(needle,needle.rstrip()+"\n    except ValueError as exc:\n        raise HTTPException(422, str(exc)) from exc\n\n",1)
files[p]=t
p="wiki-raw/wms_admin_ui_reference/customer-orders.js";t=Path(p).read_text(encoding="utf-8")
t=t.replace('let orderListGeneration=0,', 'let orderPageCursor=null,orderPageHistory=[],orderPageFilters="",orderPageBusy=false;\nlet orderListGeneration=0,',1)
t=t.replace('async function loadOrders() {\n  const serial=', '''function orderPagingControls(){
  orderEl("orderPagePrevious").disabled=orderPageBusy||!orderPageHistory.length;
  orderEl("orderPageNext").disabled=orderPageBusy||!orderState.orders.length||
    orderState.orders.length<Math.min(500,Math.max(1,Number(orderEl("orderLimit").value)||200));
}
async function orderPage(direction){
  if(orderPageBusy)return;
  const filters=orderFilters().toString();
  if(filters!==orderPageFilters){await loadOrders();return;}
  if(direction==="next"){
    if(!orderState.orders.length)return;
    orderPageHistory.push(orderPageCursor);
    orderPageCursor=orderState.orders.at(-1).customer_order_id;
  }else if(orderPageHistory.length){orderPageCursor=orderPageHistory.pop();}
  else return;
  await loadOrders(true);
}
async function loadOrders(keepPage=false) {
  if(keepPage!==true){orderPageCursor=null;orderPageHistory=[];}
  const params=orderFilters();orderPageFilters=params.toString();
  if(orderPageCursor!=null)params.set("before_id",String(orderPageCursor));
  orderPageBusy=true;orderPagingControls();
  const serial=''',1)
t=t.replace('orderRequest("/api/customer-orders?"+orderFilters().toString())', 'orderRequest("/api/customer-orders?"+params.toString())',1)
t=t.replace('orderEl("orderStatusText").textContent="Заказов: "+rows.length;', 'orderEl("orderStatusText").textContent="Страница "+(orderPageHistory.length+1)+" · заказов: "+rows.length;',1)
t=t.replace('}catch(error){if(serial===orderListGeneration&&scope===orderScope())orderEl("orderStatusText").textContent=error.message;}\n}', '}catch(error){if(serial===orderListGeneration&&scope===orderScope())orderEl("orderStatusText").textContent=error.message;}\n  finally{if(serial===orderListGeneration&&scope===orderScope()){orderPageBusy=false;orderPagingControls();}}\n}',1)
t=t.replace('  orderIdentity=scope;orderListGeneration++;orderDetailGeneration++;', '  orderIdentity=scope;orderListGeneration++;orderDetailGeneration++;\n  orderPageCursor=null;orderPageHistory=[];orderPageFilters="";orderPageBusy=false;',1)
t=t.replace('    orderBind("orderLoad",loadOrders);', '    orderBind("orderPageNext",()=>orderPage("next"));orderBind("orderPagePrevious",()=>orderPage("previous"));\n    orderBind("orderLoad",loadOrders);',1)
files[p]=t
p="wiki-raw/wms_admin_ui_reference/customer-orders.html";t=Path(p).read_text(encoding="utf-8")
t=t.replace('<div class="rights-summary"><span id="orderStatusText">Ожидание данных</span></div>', '<div class="order-pagination"><span id="orderStatusText">Ожидание данных</span><div><button id="orderPagePrevious" type="button" disabled>← Новее</button><button id="orderPageNext" type="button" disabled>Старее →</button></div></div>')
t=re.sub(r'customer-orders.js\?v=[^"]+', 'customer-orders.js?v=20261013-1045',t)
files[p]=t
p="wiki-raw/wms_admin_ui_reference/order-execution.css";t=Path(p).read_text(encoding="utf-8")
files[p]=t+"\n.order-pagination{display:flex;justify-content:space-between;align-items:center;gap:12px;margin:14px 0;color:#63758e;font-size:13px}.order-pagination>div{display:flex;gap:8px}.order-pagination button{padding:8px 12px;border:1px solid #dce6f3;border-radius:8px;background:#fff;color:#2459a0;cursor:pointer}.order-pagination button:disabled{opacity:.45;cursor:default}\n"
print(json.dumps(files,ensure_ascii=True))
