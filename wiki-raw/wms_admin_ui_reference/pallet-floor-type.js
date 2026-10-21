(() => {
 const el=id=>document.getElementById(id);
 let current=null;
 function reset(){current=null;el("palletFloorPanel").hidden=true;el("palletFloorStatus").textContent="";el("palletFloorReference").value="";}
 async function read(composition,request,isCurrent){
  reset();
  if(composition.mode!=="SINGLE"||composition.nodes[0].kind!=="STOCK")return;
  const type=await request("/api/inventory/pallet-floor-types?identifier="+encodeURIComponent(composition.root));
  const types=type.types;
  if(!Array.isArray(types))throw new Error("Перечитайте паллету: список типов не получен.");
  if(!isCurrent())return;
  current={...type,root:composition.root};
  el("palletFloorSelect").replaceChildren(new Option("Выберите фактический тип",""),...types.map(t=>new Option(t.name,String(t.id))));
  el("palletFloorSelect").value=type.pallet_type_id?String(type.pallet_type_id):"";
  el("palletFloorStatus").textContent=type.status==="CONFIGURED"?"Сохранён тип: "+type.current_type_name+" · версия "+type.version:"Тип целой паллеты ещё не указан.";
  el("palletFloorPanel").hidden=false;
 }
 function collect(composition){
  if(!current||current.root!==composition?.root||composition.mode!=="SINGLE"||!current.has_physical_stock)throw new Error("Покажите актуальную целую паллету с товаром.");
  const type=Number(el("palletFloorSelect").value),reference=el("palletFloorReference").value.trim();
  if(!Number.isSafeInteger(type)||type<1||!reference)throw new Error("Выберите фактический тип паллеты и укажите основание подтверждения.");
  return {identifier:current.root,pallet_type_id:type,expected_version:current.version,
   scan_pallet:el("loadScan").value,scan_cell:el("loadCell").value,evidence_reference:reference};
 }
 window.wmsPalletFloorType={read,collect,reset};
})();