(() => {
  const e=id=>document.getElementById(id);
  let busy=false;
  async function run(execute) {
    if(busy)return;
    const auth=window.wmsAdminAuth, warehouse=e("minimaxWarehouse").value.trim();
    if(!/^[1-9][0-9]*$/.test(warehouse)){e("minimaxMessage").textContent="Укажите склад.";return;}
    if(!auth?.hasPermission(execute?"pick_wave_launch":"pick_wave_view")){e("minimaxMessage").textContent="Недостаточно прав.";return;}
    busy=true;e("minimaxPreview").disabled=e("minimaxReconcile").disabled=true;
    try {
      const response=await fetch((auth.state.apiBase||"http://127.0.0.1:8088").replace(/\/$/,"")+
        "/api/inventory/minimax/"+warehouse+(execute?"/reconcile":""),{method:execute?"POST":"GET",headers:auth.headers()});
      const data=await response.json();
      if(!response.ok)throw Error(typeof data.detail==="string"?data.detail:JSON.stringify(data.detail));
      const reasons={MIN_MAX_NORM_REQUIRED:"Не заданы минимум и максимум",MIN_MAX_NORM_INVALID:"Некорректные нормы",
        EXISTING_REPLENISHMENT:"Уже есть открытая подача",ABOVE_MINIMUM:"Остаток выше минимума",READY:"Требуется подача",
        WAIT_FREE_CELL:"Нет свободной вместимости"};
      e("minimaxMessage").textContent=(execute?"Создано заданий: "+data.created+"\n":"Предпросмотр\n")+
        data.faces.map(r=>r.cell_code+" · "+r.articul+" · "+(reasons[r.reason]||r.reason)+" · "+r.quantity+" базовых единиц").join("\n");
    }catch(error){e("minimaxMessage").textContent=error.message;}
    finally{busy=false;e("minimaxPreview").disabled=e("minimaxReconcile").disabled=false;}
  }
  e("minimaxPreview").addEventListener("click",()=>run(false));
  e("minimaxReconcile").addEventListener("click",()=>run(true));
})();
