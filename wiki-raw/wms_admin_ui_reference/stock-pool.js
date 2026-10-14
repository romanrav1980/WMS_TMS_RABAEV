/* Exact decimal strings; durable command identity survives reload and uncertain responses. */
(() => {
  const e=id=>document.getElementById(id);
  let policy=null, selection=null, serial=0, busy=false;
  const msg=text=>{e("poolMessage").textContent=text;};
  const auth=()=>window.wmsAdminAuth;
  const key="nicora.soft-pool.pending.v1";
  function selected() {
    const warehouse=e("poolWarehouse").value.trim(), article=e("poolArticle").value.trim();
    if(!/^[1-9][0-9]*$/.test(warehouse)||!article)throw Error("Укажите склад и артикул.");
    return {warehouse,article};
  }
  const path=s=>"/"+s.warehouse+"/"+encodeURIComponent(s.article);
  async function request(url,method="GET",body) {
    const response=await fetch((auth().state.apiBase||"http://127.0.0.1:8088").replace(/\/$/,"")+url,
      {method,headers:auth().headers(body?{"Content-Type":"application/json"}:{}),body:body?JSON.stringify(body):undefined});
    const data=await response.json();
    if(!response.ok) {
      const error=Error(typeof data.detail==="string"?data.detail:JSON.stringify(data.detail));
      error.confirmed=response.status<500 && data.detail?.outcome_confirmed!==false;
      throw error;
    }
    return data;
  }
  function render(data) {
    e("poolAvailable").textContent="Доступно "+data.available_quantity+" "+data.unit+
      (data.from_stock?" · обеспечение из наличия":" · плановое обеспечение")+" · предпросмотр";
    const rows=e("poolRows");rows.replaceChildren();
    for(const order of data.orders) {
      const tr=document.createElement("tr");
      for(const value of [order.order_id,order.line_id,order.quantity,data.allocations[String(order.line_id)]||"0"]) {
        const td=document.createElement("td");td.textContent=String(value);tr.append(td);
      }
      rows.append(tr);
    }
  }
  async function load() {
    const s=selected(), token=++serial;selection=s;policy=null;
    const [p,pool]=await Promise.all([request("/api/sku-allocation"+path(s)),request("/api/inventory/soft-pools"+path(s))]);
    if(token!==serial)return;
    policy=p;e("poolClass").value=p.stock_class;e("poolFlag").value=p.ship_from_stock===null?"":String(p.ship_from_stock);
    e("poolStep").value=p.pick_step;render(pool);
    msg(p.policy_version===0?"Сначала сохраните ячейку отбора товара в настройках приёмки.":"Версия настройки "+p.policy_version+". Мягкий резерв не закрепляет паллету и не увеличивает жёсткий резерв.");
  }
  async function save() {
    const s=selected();
    if(!policy||JSON.stringify(s)!==JSON.stringify(selection))throw Error("Сначала загрузите настройку выбранного товара.");
    await request("/api/sku-allocation"+path(s),"PUT",{expected_version:policy.policy_version,stock_class:e("poolClass").value,
      ship_from_stock:e("poolFlag").value===""?null:e("poolFlag").value==="true",pick_step:e("poolStep").value.trim()});
    await load();
  }
  async function allocate() {
    let pending=JSON.parse(localStorage.getItem(key)||"null");
    const s=selected();
    if(pending&&JSON.stringify(s)!==JSON.stringify(pending.selection))throw Error("Сначала повторите незавершённый расчёт склада "+pending.selection.warehouse+", товара "+pending.selection.article+".");
    if(!pending){pending={selection:s,body:{operation_id:"POOL.UI:"+crypto.randomUUID()}};localStorage.setItem(key,JSON.stringify(pending));}
    try {
      const result=await request("/api/inventory/soft-pools"+path(s)+"/allocate","POST",pending.body);
      localStorage.removeItem(key);await load();
      msg("Расчёт сохранён: "+result.allocated_quantity+" "+result.unit+". Операция "+result.operation_id);
    } catch(error){if(error.confirmed)localStorage.removeItem(key);throw error;}
  }
  function action(id,permission,fn) {
    e(id).addEventListener("click",async()=>{
      if(busy)return;
      if(!auth()?.hasPermission(permission)){msg("Недостаточно прав.");return;}
      busy=true;for(const n of ["poolLoad","poolSave","poolAllocate"])e(n).disabled=true;
      try{await fn();}catch(error){msg(error.message);}
      finally{busy=false;for(const n of ["poolLoad","poolSave","poolAllocate"])e(n).disabled=false;}
    });
  }
  action("poolLoad","stock_reservation_view",load);
  action("poolSave","warehouse_settings_edit",save);
  action("poolAllocate","stock_reservation_edit",allocate);
  try {
    const pending=JSON.parse(localStorage.getItem(key)||"null");
    if(pending){e("poolWarehouse").value=pending.selection.warehouse;e("poolArticle").value=pending.selection.article;msg("Результат прошлого расчёта требует подтверждения. Повторите расчёт с сохранённым идентификатором.");}
  }catch{msg("Не удалось прочитать незавершённый расчёт. Не создавайте повторную операцию до выяснения результата.");}
})();
