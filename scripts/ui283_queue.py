from pathlib import Path
import json
out={}
p=Path("wiki-raw/wms_admin_ui_reference/store-return-receiving.js");s=p.read_text(encoding="utf-8")
s=s.replace('let rows=[],policy=null,pending=null,busy=false,identity="",serial=0;', 'let rows=[],policy=null,pending=null,busy=false,identity="",serial=0,selectedSource=null,next=null;')
s=s.replace('  el("receiveRetry").hidden', '  el("receiveConfirm").disabled=busy||!!pending||!selectedSource;el("receiveNext").disabled=busy||!!pending||!next;\n  el("receiveRetry").hidden',1)
s=s.replace('function selected(){return rows.find(row=>row.pickup_operation_id===el("receivePickup").value);}', 'function selected(){return selectedSource;}')
a=s.index(' function summary(){');b=s.index(' async function load()',a)
s=s[:a]+""" async function summary(){
  const row=rows.find(value=>value.pickup_operation_id===el("receivePickup").value),scope=key(),version=++serial;
  selectedSource=null;markDraft.setContext(null,scope+':source-pending');
  el("receiveBoxes").value="";el("receiveGoodBoxes").checked=false;
  for(const id of ["receiveVehicle","receivePallet","receiveCell","receiveBarcode","receiveQuantity","receiveBatch","receiveExpiry","receiveGross","receiveNet"])el(id).value="";
  el("receiveSource").textContent=row?"Читается исходный возврат…":"";controls();if(!row)return;
  try{
   const ware=warehouse(),source=await request("/warehouses/"+ware+"/pickups/"+encodeURIComponent(row.pickup_operation_id)+"/source");
   if(scope!==key()||version!==serial||ware!==Number(el("receiveWare").value)||source.pickup_operation_id!==el("receivePickup").value)return;
   selectedSource=source;markDraft.setContext(source.marked_unit_control||null,scope+':'+source.pickup_operation_id);
   el("receiveSource").textContent=source.store_addr+" · "+source.return_document+" · "+source.article+" · "+source.quantity+" "+source.base_uom+" · "+source.expiry_date+" · зона "+(source.receive_cell||"не настроена")+" · "+source.disposition;
  }catch(error){if(scope===key()&&version===serial)say(error.message);}
  finally{if(scope===key()&&version===serial)controls();}
 }
"""+s[b:]
s=s.replace(' async function load(){',' async function load(nextPage=false){',1)
s=s.replace('data=await request("/warehouses/"+ware+"/pending");','data=await request("/warehouses/"+ware+"/pending-page?"+new URLSearchParams({limit:"20",after:nextPage===true&&next?next:""}));',1)
s=s.replace('   rows=data;','   rows=data.items;next=data.next_after;',1)
s=s.replace('say(data.length?"":"Нет возвратов, ожидающих приёмки.");','say(rows.length?(data.has_more?"Показана страница очереди. Остальные возвраты доступны по кнопке продолжения.":""):"Нет возвратов, ожидающих приёмки.");',1)
s=s.replace('identity=fingerprint;++serial;rows=[];policy=null;pending=null;', 'identity=fingerprint;++serial;rows=[];policy=null;pending=null;selectedSource=null;next=null;')
s=s.replace('el("receiveLoad").addEventListener("click",load);', 'el("receiveLoad").addEventListener("click",()=>load());el("receiveNext").addEventListener("click",()=>load(true));')
s=s.replace('++serial;rows=[];policy=null;el("receivePickup")', '++serial;rows=[];policy=null;selectedSource=null;next=null;el("receivePickup")')
out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/store-return-receiving.html");s=p.read_text(encoding="utf-8")
s=s.replace('<label>Возврат<select id="receivePickup">','<button id="receiveNext" disabled>Следующие возвраты</button><label>Возврат<select id="receivePickup">',1);out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
