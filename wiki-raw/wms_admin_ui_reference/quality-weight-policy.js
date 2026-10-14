(() => {
 const panel=document.createElement("section");panel.className="panel";
 panel.innerHTML='<h2>Весовой контроль товара</h2><p>Масса на базовую единицу включает упаковку товара; тара паллеты взвешивается отдельно. Допуск равен половине массы самой лёгкой коробки в составе СТ.</p><label>Склад <input data-warehouse type="number" min="1"></label><label>Артикул <input data-article></label><button data-load>Загрузить</button><label>Базовая единица <input data-base-uom placeholder="EA"></label><label>Масса на базовую единицу, кг <input data-base-weight inputmode="decimal"></label><label>Масса стандартной коробки, кг <input data-box-weight inputmode="decimal"></label><button data-save>Сохранить</button><p role="status"></p>';
 (document.querySelector("main")||document.body).append(panel);
 const el=k=>panel.querySelector("[data-"+k+"]"),message=panel.querySelector("[role=status]");
 let snapshot=null,busy=false,generation=0,identity="";
 const base=()=>window.wmsAdminAuth.state.apiBase.replace(/\/$/,"");
 const url=()=>"/api/sku-quality-weight/"+Number(el("warehouse").value)+"/"+encodeURIComponent(el("article").value.trim());
 async function call(options={}){
  const r=await fetch(base()+url(),{...options,headers:{...window.wmsAdminAuth.headers(),...(options.headers||{})}}),data=await r.json();
  if(!r.ok)throw new Error(typeof data.detail==="string"?data.detail:JSON.stringify(data.detail||data));return data;
 }
 function show(data){
  snapshot=data;el("base-uom").value=data.base_uom||"";el("base-weight").value=data.base_weight_kg||"";el("box-weight").value=data.box_weight_kg||"";
  message.textContent="Настройка загружена. Изменение потребует повторного контроля ранее проверенных СТ.";
 }
 el("load").onclick=async()=>{
  if(busy||Number(el("warehouse").value)<1||!el("article").value.trim())return;
  const current=++generation,path=url();snapshot=null;
  try{const data=await call();if(current===generation&&url()===path)show(data);}catch(e){message.textContent=e.message;}
 };
 el("save").onclick=async()=>{
  if(busy||!snapshot||snapshot.warehouse!==Number(el("warehouse").value)||snapshot.article!==el("article").value.trim()){message.textContent="Загрузите настройку перед сохранением.";return;}
  const weight=k=>el(k).value.trim()||null,baseWeight=weight("base-weight"),boxWeight=weight("box-weight");
  if((baseWeight===null)!==(boxWeight===null)){message.textContent="Укажите обе массы или очистите обе для запрета весового допуска.";return;}
  for(const v of [baseWeight,boxWeight])if(v!==null&&(!/^(0|[1-9][0-9]*)(\.[0-9]{1,9})?$/.test(v)||Number(v)<=0)){message.textContent="Масса должна быть положительным числом через точку.";return;}
  const body={expected_version:snapshot.version,base_uom:el("base-uom").value.trim(),base_weight_kg:baseWeight,box_weight_kg:boxWeight};
  busy=true;panel.querySelectorAll("input,button").forEach(x=>x.disabled=true);
  try{show(await call({method:"PUT",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)}));}
  catch(e){snapshot=null;message.textContent=e.message+" Загрузите сохранённую настройку.";}
  finally{busy=false;panel.querySelectorAll("input,button").forEach(x=>x.disabled=false);rights();}
 };
 function rights(){panel.hidden=!window.wmsAdminAuth?.hasPermission("finished_goods_view");el("save").hidden=!window.wmsAdminAuth?.hasPermission("warehouse_settings_edit");const next=(window.wmsAdminAuth.state.apiBase||"")+":"+(window.wmsAdminAuth.state.user?.username||"");if(identity!==next){identity=next;snapshot=null;generation++;}}
 for(const name of ["warehouse","article"])el(name).addEventListener("input",()=>{const next=(window.wmsAdminAuth.state.apiBase||"")+":"+(window.wmsAdminAuth.state.user?.username||"");if(identity!==next){identity=next;snapshot=null;generation++;}});
 window.addEventListener("wms-admin-auth-ready",rights);rights();
})();
