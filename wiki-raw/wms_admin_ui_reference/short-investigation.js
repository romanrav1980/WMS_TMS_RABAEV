(() => {
  const e=id=>document.getElementById(id);
  const shortId=new URLSearchParams(location.search).get("short_id");
  const pendingKey="retailcase.investigation.pending:"+shortId;
  let incident=null, cameras=[], busy=false, serial=0;
  const message=text=>{e("investigationMessage").textContent=text;};
  const auth=()=>window.wmsAdminAuth;
  async function api(path,method="GET",body) {
    const response=await fetch((auth().state.apiBase||"http://127.0.0.1:8088").replace(/\/$/,"")+path,
      {method,headers:auth().headers(body?{"Content-Type":"application/json"}:{}),body:body?JSON.stringify(body):undefined});
    const data=await response.json();
    if(!response.ok){const error=Error(typeof data.detail==="string"?data.detail:JSON.stringify(data.detail));
      error.status=response.status;error.detail=data.detail;throw error;}
    return data;
  }
  function bookmark(uri,title) {
    const a=document.createElement("a"), parsed=new URL(uri);
    if(!["http:","https:"].includes(parsed.protocol))throw Error("Недопустимая ссылка архива.");
    a.href=uri;a.textContent=title;a.target="_blank";a.rel="noopener noreferrer";return a;
  }
  function restorePending() {
    const pending=JSON.parse(localStorage.getItem(pendingKey)||"null");
    for(const id of ["investigationStatus","investigationNote","investigationVideo"])e(id).disabled=!!pending;
    if(pending){e("investigationStatus").value=pending.status;e("investigationNote").value=pending.note;
      e("investigationVideo").value=pending.video_uri||"";message("Повторите сохранённую запись, чтобы подтвердить её результат.");}
    return pending;
  }
  async function load() {
    if(!/^[1-9][0-9]*$/.test(shortId||""))throw Error("Не указан номер инцидента.");
    const token=++serial, data=await api("/api/inventory/shorts/"+shortId+"/investigation");
    if(token!==serial)return;
    incident=data;
    e("investigationTitle").textContent="Недостача #"+shortId+" · "+data.cell;
    e("investigationContext").textContent=data.article+" · "+data.short_quantity+" · "+
      data.created_at+" · сообщил "+data.created_by+" · восстановление "+(data.recovery_state||data.status);
    const links=e("investigationCameras");links.replaceChildren();
    if(!data.cameras.length)links.textContent="Для ячейки не настроена ссылка на видеоархив.";
    for(const camera of data.cameras) {
      const p=document.createElement("p");
      if(camera.uri)p.append(bookmark(camera.uri,"Просмотреть: "+camera.viewpoint));
      else p.textContent=camera.viewpoint+" · проверьте настройку архива";
      links.append(p);
    }
    const history=e("investigationHistory");history.replaceChildren();
    for(const review of data.history) {
      const p=document.createElement("p");
      p.textContent=review.created_at+" · "+review.created_by+" · "+review.status+" · "+review.note+" ";
      if(review.video_uri)p.append(bookmark(review.video_uri,"Фрагмент записи"));
      history.append(p);
    }
    message("Расследование "+data.investigation_status+" · версия "+data.investigation_version);
    restorePending();
    if(auth().hasPermission("warehouse_settings_edit")) {
      cameras=await api("/api/inventory/cctv-viewpoints?warehouse="+data.warehouse+"&cell="+encodeURIComponent(data.cell));
      const select=e("cameraExisting");select.replaceChildren();
      const blank=document.createElement("option");blank.value="";blank.textContent="Новая точка обзора";select.append(blank);
      cameras.forEach((camera,index)=>{const o=document.createElement("option");o.value=String(index);
        o.textContent=camera.viewpoint_code+(camera.active?"":" · отключена");select.append(o);});
      select.dispatchEvent(new Event("change"));
    }
  }
  async function saveReview() {
    if(!incident||!auth().hasPermission("case_pick_short_approve"))throw Error("Нет права сохранять расследование.");
    let pending=restorePending();
    if(!pending){
      pending={expected_version:incident.investigation_version,offline_event_id:"INV.REVIEW:"+crypto.randomUUID(),
        status:e("investigationStatus").value,note:e("investigationNote").value.trim(),
        video_uri:e("investigationVideo").value.trim()||null};
      if(!pending.note)throw Error("Укажите вывод расследования.");
      localStorage.setItem(pendingKey,JSON.stringify(pending));restorePending();
    }
    try {
      const result=await api("/api/inventory/shorts/"+shortId+"/investigation","POST",pending);
      localStorage.removeItem(pendingKey);await load();message("Записан вывод расследования · версия "+result.version);
    }catch(error) {
      if(error.status<500&&error.detail!=="INVESTIGATION_EVENT_CONTENT_CONFLICT")localStorage.removeItem(pendingKey);
      restorePending();throw error;
    }
  }
  async function saveCamera() {
    if(!incident||!auth().hasPermission("warehouse_settings_edit"))throw Error("Нет права настроек склада.");
    const chosen=e("cameraExisting").value, old=chosen===""?null:cameras[Number(chosen)];
    const result=await api("/api/inventory/cctv-viewpoints","PUT",{warehouse:incident.warehouse,cell:incident.cell,
      viewpoint:e("cameraCode").value.trim(),expected_version:old?.policy_version||0,
      archive_uri_template:e("cameraTemplate").value.trim(),stored_time_offset:e("cameraOffset").value.trim(),
      before_seconds:Number(e("cameraBefore").value),after_seconds:Number(e("cameraAfter").value),active:e("cameraActive").checked});
    await load();
    const found=cameras.findIndex(c=>c.viewpoint_code===result.viewpoint);
    if(found>=0){e("cameraExisting").value=String(found);e("cameraExisting").dispatchEvent(new Event("change"));}
    message("Привязка видеоархива сохранена · версия "+result.version);
  }
  e("cameraExisting").addEventListener("change",()=>{
    const chosen=e("cameraExisting").value, camera=chosen===""?null:cameras[Number(chosen)];
    e("cameraCode").value=camera?.viewpoint_code||"";e("cameraCode").disabled=!!camera;
    e("cameraTemplate").value=camera?.archive_uri_template||"";e("cameraOffset").value=camera?.stored_time_offset||"+03:00";
    e("cameraBefore").value=camera?.before_seconds??120;e("cameraAfter").value=camera?.after_seconds??120;
    e("cameraActive").checked=camera?!!camera.active:true;
  });
  function action(id,fn){e(id).addEventListener("click",async()=>{
    if(busy)return;busy=true;e(id).disabled=true;
    try{await fn();}catch(error){message(error.message);}finally{busy=false;e(id).disabled=false;}
  });}
  action("investigationReload",load);action("investigationSave",saveReview);action("cameraSave",saveCamera);
  window.addEventListener("wms-admin-auth-ready",()=>load().catch(error=>message(error.message)));
  if(auth()?.state?.user)load().catch(error=>message(error.message));
})();
