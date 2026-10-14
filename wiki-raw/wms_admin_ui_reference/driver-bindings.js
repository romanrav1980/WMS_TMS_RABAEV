(() => {
 const el=id=>document.getElementById(id),auth=()=>window.wmsAdminAuth;
 let snapshot=null,busy=false,scope="";
 const identity=()=>auth().state.apiBase+":"+auth().state.user?.username+":"+(auth().state.user?.permissions||[]).slice().sort().join(",");
 const say=text=>{el("bindingMessage").textContent=text;};
 function controls(){for(const id of ["bindingDriver","bindingLoad","bindingUser","bindingActive","bindingSave"])el(id).disabled=busy;}
 async function request(driver,body){
  const response=await fetch(auth().state.apiBase.replace(/\/$/,"")+"/api/transport/driver-bindings/"+driver,{method:body?"PUT":"GET",headers:auth().headers(body?{"Content-Type":"application/json"}:{}),...(body?{body:JSON.stringify(body)}:{})});
  const data=await response.json();if(!response.ok)throw Error(typeof data.detail==="string"?data.detail:data.detail?.message||"Не удалось изменить привязку");return data;
 }
 async function load(){
  if(busy)return;const driver=Number(el("bindingDriver").value),owner=identity();if(!Number.isSafeInteger(driver)||driver<1){say("Укажите водителя.");return;}
  busy=true;controls();snapshot=null;
  try{const data=await request(driver);if(owner===identity()){snapshot=data;el("bindingUser").value=data.user_id||"";el("bindingActive").checked=Boolean(data.active);el("bindingSummary").textContent="Водитель "+driver+" · версия "+data.binding_version;say("");}}
  catch(error){if(owner===identity())say(error.message);}finally{busy=false;controls();}
 }
 async function save(){
  if(busy||!snapshot||snapshot.driver_id!==Number(el("bindingDriver").value)){say("Покажите текущую привязку.");return;}
  const original=snapshot,owner=identity(),body={user_id:el("bindingUser").value,active:el("bindingActive").checked,expected_version:original.binding_version};
  busy=true;controls();
  try{const data=await request(original.driver_id,body);if(owner===identity()){snapshot=data;el("bindingSummary").textContent="Водитель "+data.driver_id+" · версия "+data.binding_version;say("Привязка сохранена.");}}
  catch(error){if(owner===identity()){snapshot=null;say(error.message+". Покажите текущую привязку: ответ мог не дойти.");}}
  finally{busy=false;controls();}
 }
 function changed(){
  const current=identity();if(current===scope)return;scope=current;snapshot=null;for(const id of ["bindingDriver","bindingUser"])el(id).value="";el("bindingActive").checked=false;el("bindingSummary").textContent="";say("");
 }
 el("bindingLoad").addEventListener("click",load);el("bindingSave").addEventListener("click",save);window.addEventListener("wms-admin-auth-ready",changed);changed();
})();
